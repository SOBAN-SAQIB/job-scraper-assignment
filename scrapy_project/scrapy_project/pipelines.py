# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

from itemadapter import ItemAdapter
import pandas as pd
import re
import os


class JobPipeline:
    """Pipeline that deduplicates, cleans, extracts skills, and writes CSV."""

    SKILL_KEYWORDS = [
        'Python', 'SQL', 'Excel', 'Java', 'JavaScript', 'C++', 'C#',
        'AWS', 'Azure', 'GCP', 'Docker', 'Kubernetes', 'Pandas',
        'NumPy', 'Tableau', 'Power BI', 'Machine Learning', 'Data Analysis',
        'R', 'Spark'
    ]

    OUTPUT_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'final', 'jobs.csv'))

    def open_spider(self, spider):
        self.items = []
        self.seen_urls = set()

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        url = (adapter.get('job_url') or '').strip()
        if not url:
            return item

        if url in self.seen_urls:
            return item
        self.seen_urls.add(url)

        cleaned_item = {}
        for field in ['job_title', 'company', 'location', 'department', 'employment_type', 'posted_date', 'description']:
            value = adapter.get(field, '') or ''
            cleaned_item[field] = self._clean_text(value)

        cleaned_item['job_url'] = url

        cleaned_item['source_url'] = self._clean_text(adapter.get('source_url', '') or '')

        skills = adapter.get('skills') or []
        if isinstance(skills, str):
            skills = [s.strip() for s in re.split(r'[;,\n]+', skills) if s.strip()]

        skills = [s for s in skills if s]

        auto_skills = self._extract_skills(cleaned_item['description'])
        combined_skills = list(dict.fromkeys([*skills, *auto_skills]))

        cleaned_item['skills'] = combined_skills

        self.items.append(cleaned_item)
        return item

    def close_spider(self, spider):
        if not self.items:
            spider.logger.info('No jobs to store.')
            return

        os.makedirs(os.path.dirname(self.OUTPUT_FILE), exist_ok=True)

        df = pd.DataFrame(self.items)

        columns = ['job_title', 'company', 'location', 'department', 'employment_type', 'posted_date', 'job_url', 'description', 'skills', 'source_url']
        for c in columns:
            if c not in df.columns:
                df[c] = ''

        # Convert list-valued skills to comma-separated string for clean CSV
        if 'skills' in df.columns:
            df['skills'] = df['skills'].apply(lambda x: ', '.join(x) if isinstance(x, (list, tuple)) else str(x))

        df = df[columns]
        df.to_csv(self.OUTPUT_FILE, index=False, encoding='utf-8')

        spider.logger.info(f"Saved {len(df)} unique job listings to {self.OUTPUT_FILE}")

    def _clean_text(self, value):
        if not value:
            return ''
        if isinstance(value, list):
            value = ' '.join(value)
        text = re.sub(r'\s+', ' ', str(value)).strip()
        return text

    def _extract_skills(self, text):
        if not text:
            return []

        found = []
        text_lower = text.lower()
        for keyword in self.SKILL_KEYWORDS:
            if keyword.lower() in text_lower:
                found.append(keyword)

        return list(dict.fromkeys(found))

