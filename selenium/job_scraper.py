import time
import os
import pandas as pd

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager


# ----------------------------
# Setup Selenium Driver
# ----------------------------
def get_driver():
    options = Options()
    options.add_argument("--headless")  # run in background
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )
    return driver


# ----------------------------
# Scroll Page (for dynamic sites)
# ----------------------------
def scroll_page(driver, max_scrolls=15):
    """Scroll page until no new content loads"""
    print(f"    Starting scroll sequence...")
    previous_height = driver.execute_script("return document.body.scrollHeight")
    scroll_count = 0
    no_change_count = 0
    
    while scroll_count < max_scrolls:
        # Scroll down
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)  # Wait for content to load
        
        # Calculate new height
        new_height = driver.execute_script("return document.body.scrollHeight")
        
        # If height hasn't changed, increment no-change counter
        if new_height == previous_height:
            no_change_count += 1
            if no_change_count >= 2:  # Stop after 2 consecutive no-change scrolls
                print(f"    ✓ Page fully loaded after {scroll_count} scrolls ({new_height}px)")
                break
        else:
            no_change_count = 0
            print(f"    Scroll {scroll_count + 1}: Height {previous_height} → {new_height}px")
        
        previous_height = new_height
        scroll_count += 1


# ----------------------------
# Scrape Job Links
# ----------------------------
def scrape_job_links(driver, url, company_name=""):
    """Scrape all job listing links from career page"""
    print(f"  Loading page: {url}")
    driver.get(url)
    time.sleep(5)

    # Scroll to load all dynamic content
    print(f"  Scrolling to load all content...")
    scroll_page(driver)

    links = set()
    elements = driver.find_elements(By.TAG_NAME, "a")
    
    print(f"  Found {len(elements)} total links on page")

    for el in elements:
        try:
            href = el.get_attribute("href")
            
            if not href:
                continue
            
            href_lower = href.lower()
            
            # Remove anchors and fragments
            href = href.split('#')[0]
            
            # Company-specific filtering
            if 'airbnb' in url.lower():
                # Airbnb job listing pattern
                if '/positions/' in href_lower and 'job' not in href_lower.split('/')[-1]:
                    links.add(href)
            elif 'stripe' in url.lower():
                # Stripe job listing pattern - /jobs/listing/ or similar
                if '/jobs/listing' in href_lower or '/jobs/search' in href_lower:
                    links.add(href)
            elif 'ashby' in url.lower() or 'openai' in url.lower():
                # OpenAI/Ashby pattern - usually has job ID in URL
                if '/jobs.ashbyhq.com/' in href_lower or any(x in href_lower for x in ['/openai/', 'ashbyhq']):
                    links.add(href)
            else:
                # Generic job link detection
                if any(keyword in href_lower for keyword in ["job", "position", "career", "opening"]):
                    links.add(href)
        except Exception as e:
            continue

    print(f"  ✓ Extracted {len(links)} job links")
    return list(links)


# ----------------------------
# Main Function
# ----------------------------
def main():
    driver = None
    print("=" * 70)
    print("🔍 STARTING JOB SCRAPER")
    print("=" * 70)
    
    try:
        print("⏳ Initializing Chrome driver...")
        driver = get_driver()

        urls = [
            "https://careers.airbnb.com/positions/",
            "https://stripe.com/jobs/search",
            "https://jobs.ashbyhq.com/openai"
        ]

        all_data = []

        for url in urls:
            print(f"\n{'='*60}")
            print(f"Scraping: {url}")
            print(f"{'='*60}")
            
            try:
                job_links = scrape_job_links(driver, url)
                print(f"✅ Found {len(job_links)} job links for this source\n")
                
                for link in job_links:
                    all_data.append({
                        "source_url": url,
                        "job_link": link
                    })
            except Exception as e:
                print(f"❌ Error scraping {url}: {e}\n")
                continue

        if driver:
            driver.quit()

        # Save to CSV
        if all_data:
            df = pd.DataFrame(all_data)
            
            # Get project root and save to data/raw/
            script_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(os.path.dirname(script_dir))
            output_dir = os.path.join(project_root, 'data', 'raw')
            os.makedirs(output_dir, exist_ok=True)
            
            output_path = os.path.join(output_dir, 'job_links.csv')
            df.to_csv(output_path, index=False)
            
            print(f"\n{'='*60}")
            print(f"✅ SUCCESS!")
            print(f"{'='*60}")
            print(f"Total job links saved: {len(df)}")
            print(f"Output file: {output_path}")
            print(f"Breakdown by source:")
            print(f"{df['source_url'].value_counts().to_string()}")
        else:
            print("❌ No job links scraped")

    except Exception as e:
        print(f"Error in main: {e}")
    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass


# ----------------------------
# Run Script
# ----------------------------
if __name__ == "__main__":
    main()