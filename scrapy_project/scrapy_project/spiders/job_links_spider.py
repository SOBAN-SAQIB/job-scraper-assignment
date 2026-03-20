import csv
import os
import scrapy
from scrapy_project.items import JobItem


class JobLinksSpider(scrapy.Spider):
    name = "job_links"
    custom_settings = {
        'ITEM_PIPELINES': {
            'scrapy_project.pipelines.JobPipeline': 300,
        },
        'CLOSESPIDER_PAGECOUNT': 0,
        'ROBOTSTXT_OBEY': False,
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    }

    # Default source URLs (from selenium scraper)
    source_urls = [
        "https://careers.airbnb.com/positions/",
        "https://stripe.com/jobs/search",
        "https://jobs.ashbyhq.com/openai"
    ]

    def __init__(self, urls_csv='job_links.csv', *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.urls_csv = urls_csv
        self.collected_items = []  # Collect items to save to CSV

    def start_requests(self):
        url_data = self._load_urls_from_csv(self.urls_csv)
        
        if url_data:
            self.logger.info(f'✓ Loaded {len(url_data)} URLs from {self.urls_csv}')
            for data in url_data:
                yield scrapy.Request(url=data['url'], callback=self.parse, 
                                   meta={'source_url': data['source_url']},
                                   errback=self.error_callback)
        else:
            # Fallback: if CSV not found, scrape directly from source pages
            self.logger.warning(f'No URLs loaded from CSV. Using source URLs from selenium scraper.')
            for source_url in self.source_urls:
                yield scrapy.Request(url=source_url, callback=self.parse_listings, 
                                   meta={'source_url': source_url})

    def _load_urls_from_csv(self, file_path):
        # Try multiple possible paths
        search_paths = [
            file_path,  # Current working directory
            os.path.join(os.getcwd(), file_path),  # CWD
            os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', file_path)),  # Project root
            os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'data', 'raw', 'job_links.csv')),  # data/raw/
        ]
        
        found_path = None
        for path in search_paths:
            if os.path.isfile(path):
                found_path = path
                self.logger.info(f"✓ Found job_links.csv at: {path}")
                break
        
        if not found_path:
            self.logger.error(f"❌ Could not find job_links.csv in any of these locations:")
            for path in search_paths:
                self.logger.error(f"  - {path}")
            return []

        urls = []
        try:
            with open(found_path, mode='r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    url = row.get('job_link') or row.get('Job Link') or row.get('job_url')
                    source_url = row.get('source_url') or ''
                    
                    if url and url.strip():
                        url = url.strip()
                        # Skip invalid URLs (anchors, fragments, relative paths)
                        if url.startswith('http') and '#' not in url:
                            urls.append({'url': url, 'source_url': source_url.strip()})
                        elif url.startswith('http'):
                            # Keep URLs with # but they'll be handled by Scrapy
                            urls.append({'url': url, 'source_url': source_url.strip()})
            
            self.logger.info(f"✓ Loaded {len(urls)} URLs from CSV")
        except Exception as e:
            self.logger.error(f"Error reading CSV: {e}")
            return []
        
        return urls

    def error_callback(self, failure):
        """Handle request errors gracefully"""
        self.logger.warning(f"Failed request to {failure.request.url}: {failure.value}")
        # Don't yield anything, just continue with other requests

    def parse_listings(self, response):
        """Extract job links from career listing pages (fallback for selenium scraper)"""
        # Extract all links from the page
        links = response.xpath('//a/@href').getall()
        
        job_keywords = ['job', 'position', 'career', 'opening', 'role']
        source_url = response.meta.get('source_url', '')
        
        for link in links:
            link = response.urljoin(link)
            link_lower = link.lower()
            
            # Filter for job-related links
            if any(keyword in link_lower for keyword in job_keywords):
                # Avoid duplicate paths
                if link not in [d.get('url') for d in getattr(self, '_processed_links', [])]:
                    yield scrapy.Request(url=link, callback=self.parse, 
                                       meta={'source_url': source_url})

    def parse(self, response):
        """Parse job listing page"""
        try:
            item = JobItem()

            item['job_title'] = self._extract_text(response, [
                "//h1[not(contains(., 'Stripe logo')) and not(contains(., 'Jobs')) and normalize-space()!='']/text()",
                "//h1[contains(@class, 'job') or contains(@class, 'title')]/text()",
                "//div[contains(@class, 'job-title')]/text()",
                "//meta[@property='og:title']/@content",
                "//title/text()",
                "//html/@data-page-title"
            ])

            item['company'] = self._extract_text(response, [
                "//meta[@name='author']/@content",
                "//a[contains(@href,'/company')]/text()",
                "//div[contains(@class,'company')]/text()"
            ])
            if not item['company']:
                # Detect company from source URL
                source = response.meta.get('source_url', '')
                if 'airbnb' in source.lower():
                    item['company'] = 'Airbnb'
                elif 'stripe' in source.lower():
                    item['company'] = 'Stripe'
                elif 'openai' in source.lower():
                    item['company'] = 'OpenAI'
                else:
                    item['company'] = response.url.split('//')[-1].split('/')[0].replace('www.', '').capitalize()
            
            item['location'] = self._extract_text(response, [
                "//span[contains(@class,'location')]/text()",
                "//div[contains(@class,'location')]/text()",
                "//li[contains(text(),'Location')]/text()",
                "//div[contains(text(),'Office locations')]/text()",
                "//div[contains(@class,'job-meta')]/text()",
                "//dd[contains(@class,'location')]/text()"
            ])
            if not item['location']:
                loc_text = self._extract_text(response, ["//p[contains(., 'Office locations')]/text()"], join=True)
                item['location'] = loc_text.replace('Office locations', '').strip()

            item['description'] = self._extract_text(response, [
                "//meta[@name='description']/@content",
                "//meta[@property='og:description']/@content",
                "//div[contains(@class,'description')]//text()",
                "//div[contains(@id,'job-description')]//text()",
                "//section[contains(@class,'job-description')]//text()",
                "//div[contains(@class,'content')]//text()"
            ], join=True)
            if not item['description']:
                item['description'] = self._extract_text(response, ["//p/text()"], join=True)

            item['job_url'] = response.url
            item['source_url'] = response.meta.get('source_url', '')
            item['skills'] = self._extract_skills(response, item.get('description', ''))

            item['department'] = self._extract_text(response, [
                "//span[contains(@class,'department')]/text()",
                "//div[contains(@class,'department')]/text()",
                "//li[contains(text(),'Department')]/text()"
            ])

            item['employment_type'] = self._extract_text(response, [
                "//span[contains(text(),'Full-time') or contains(text(),'Part-time') or contains(text(),'Contract')]/text()",
                "//div[contains(@class,'employment-type')]/text()",
                "//li[contains(text(),'Employment Type')]/text()"
            ])

            item['posted_date'] = self._extract_text(response, [
                "//span[contains(text(),'Posted') or contains(text(),'Date')]/text()",
                "//div[contains(@class,'posted-date')]/text()",
                "//li[contains(text(),'Posted')]/text()"
            ])

            # Gracefully handle missing fields
            for field in ['job_title', 'company', 'location', 'description', 'skills', 'department', 'employment_type', 'posted_date']:
                if item.get(field) is None:
                    item[field] = '' if field != 'skills' else []

            # Collect item for CSV export
            self.collected_items.append(dict(item))
            
            yield item
            
        except Exception as e:
            self.logger.warning(f"⚠️ Error parsing {response.url}: {str(e)[:100]}")
            # Continue with other URLs instead of crashing

    def _extract_text(self, response, xpaths, join=False):
        for xp in xpaths:
            data = response.xpath(xp).getall()
            if data:
                cleaned = [d.strip() for d in data if d and d.strip()]
                if cleaned:
                    return ' '.join(cleaned) if join else cleaned[0]
        return ''

    def _extract_skills(self, response, description=''):
        if not description:
            description = self._extract_text(response, [
                "//div[contains(@class,'description')]//text()",
                "//div[contains(@id,'job-description')]//text()",
                "//section[contains(@class,'job-description')]//text()"
            ], join=True)

        # Look for bullet or list-based skills
        bullets = response.xpath("//ul[./li[contains(., 'Python') or contains(., 'SQL') or contains(., 'AWS')]]/li/text() | //li[contains(@class,'skill')]/text()").getall()
        skills = [s.strip() for s in bullets if s and s.strip()]

        if not skills and description:
            # basic keyword matching
            candidate_skills = [
                'Python', 'Java', 'JavaScript', 'C++', 'SQL', 'AWS', 'Azure', 'GCP',
                'Docker', 'Kubernetes', 'Pandas', 'NumPy', 'Machine Learning', 'Data Analysis',
                'Django', 'Flask', 'React', 'Node.js'
            ]
            desc_lower = description.lower()
            for skill in candidate_skills:
                if skill.lower() in desc_lower and skill not in skills:
                    skills.append(skill)

        return list(dict.fromkeys(skills))

    def closed(self, reason):
        """Save collected job data to CSV when spider closes"""
        import pandas as pd
        
        if not self.collected_items:
            self.logger.warning("No items collected to save")
            return
        
        # Get the project root directory
        root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
        
        # Try to save to data/final/jobs.csv first, then fall back to job_links.csv
        output_paths = [
            os.path.join(root, 'data', 'final', 'jobs.csv'),
            os.path.join(root, 'job_links.csv'),
        ]
        
        saved = False
        for output_path in output_paths:
            try:
                # Create directory if it doesn't exist
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                
                # Convert skills list to string for CSV export
                items_for_export = []
                for item in self.collected_items:
                    item_dict = dict(item)
                    if isinstance(item_dict.get('skills'), list):
                        item_dict['skills'] = ', '.join(item_dict['skills'])
                    items_for_export.append(item_dict)
                
                # Save to CSV
                df = pd.DataFrame(items_for_export)
                df.to_csv(output_path, index=False)
                
                self.logger.info(f"✅ Saved {len(self.collected_items)} job records to {output_path}")
                saved = True
                break
                
            except Exception as e:
                self.logger.warning(f"Could not save to {output_path}: {e}")
                continue
        
        if not saved:
            self.logger.error("Failed to save job data to CSV")
