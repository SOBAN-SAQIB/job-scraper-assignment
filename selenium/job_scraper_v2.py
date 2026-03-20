import time
import os
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


def get_driver():
    """Setup Selenium Chrome driver"""
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-blink-features=AutomationControlled")
    
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )
    return driver


def scrape_airbnb(driver):
    """Scrape Airbnb jobs page"""
    print("\n  Loading Airbnb careers page...")
    url = "https://careers.airbnb.com/positions/"
    driver.get(url)
    time.sleep(3)
    
    links = set()
    last_height = 0
    scrolls = 0
    max_scrolls = 15
    
    while scrolls < max_scrolls:
        # Scroll
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        new_height = driver.execute_script("return document.body.scrollHeight")
        
        if new_height == last_height:
            break
        last_height = new_height
        scrolls += 1
        time.sleep(1)
    
    # Extract links - more permissive approach
    elements = driver.find_elements(By.TAG_NAME, "a")
    for el in elements:
        href = el.get_attribute("href")
        if href and 'airbnb.com' in href and ('/positions/' in href or '/jobs' in href):
            links.add(href)
    
    # Also try to get from data attributes or other selectors
    job_cards = driver.find_elements(By.CSS_SELECTOR, "[data-testid], [class*='job'], .position")
    for card in job_cards:
        try:
            job_link = card.find_elements(By.TAG_NAME, "a")
            for link in job_link:
                href = link.get_attribute("href")
                if href and 'airbnb.com' in href:
                    links.add(href)
        except:
            pass
    
    print(f"  ✓ Found {len(links)} Airbnb job links")
    return [(url, link) for link in links]


def scrape_stripe(driver):
    """Scrape Stripe jobs page"""
    print("\n  Loading Stripe jobs page...")
    url = "https://stripe.com/jobs/search"
    driver.get(url)
    time.sleep(3)
    
    links = set()
    last_height = 0
    scrolls = 0
    max_scrolls = 15
    
    while scrolls < max_scrolls:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        new_height = driver.execute_script("return document.body.scrollHeight")
        
        if new_height == last_height:
            break
        last_height = new_height
        scrolls += 1
        time.sleep(1)
    
    # Extract links - be more inclusive
    elements = driver.find_elements(By.TAG_NAME, "a")
    for el in elements:
        href = el.get_attribute("href")
        if href and 'stripe.com' in href and ('/jobs/listing' in href or '/jobs/' in href):
            full_url = href if href.startswith('http') else 'https://stripe.com' + href
            links.add(full_url)
    
    # Also try job card containers
    job_cards = driver.find_elements(By.CSS_SELECTOR, "[data-testid*='job'], [class*='job-card'], [class*='listing']")
    for card in job_cards:
        try:
            job_link = card.find_elements(By.TAG_NAME, "a")
            for link in job_link:
                href = link.get_attribute("href")
                if href and 'stripe.com' in href:
                    full_url = href if href.startswith('http') else 'https://stripe.com' + href
                    links.add(full_url)
        except:
            pass
    
    print(f"  ✓ Found {len(links)} Stripe job links")
    return [(url, link) for link in links]


def scrape_openai(driver):
    """Scrape OpenAI jobs page"""
    print("\n  Loading OpenAI jobs page...")
    url = "https://jobs.ashbyhq.com/openai"
    driver.get(url)
    time.sleep(3)
    
    links = set()
    last_height = 0
    scrolls = 0
    max_scrolls = 15
    
    while scrolls < max_scrolls:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        new_height = driver.execute_script("return document.body.scrollHeight")
        
        if new_height == last_height:
            break
        last_height = new_height
        scrolls += 1
        time.sleep(1)
    
    # Extract all job links from Ashby page - more inclusive
    elements = driver.find_elements(By.TAG_NAME, "a")
    for el in elements:
        href = el.get_attribute("href")
        if href and 'ashbyhq.com/openai' in href:
            # Filter out non-job links (search, filter pages, etc)
            if any(x not in href.lower() for x in ['#', 'filter', 'search', 'departments']):
                links.add(href)
    
    # Also try job containers
    job_items = driver.find_elements(By.CSS_SELECTOR, "[data-testid], [class*='job'], [class*='position']")
    for item in job_items:
        try:
            job_links = item.find_elements(By.TAG_NAME, "a")
            for link in job_links:
                href = link.get_attribute("href")
                if href and 'ashbyhq.com/openai' in href:
                    links.add(href)
        except:
            pass
    
    print(f"  ✓ Found {len(links)} OpenAI job links")
    return [(url, link) for link in links]


def main():
    print("=" * 70)
    print("🔍 JOB LINKS SCRAPER v2.0")
    print("=" * 70)
    
    driver = None
    try:
        print("\n⏳ Initializing Chrome driver...")
        driver = get_driver()
        
        all_data = []
        
        # Scrape Airbnb
        try:
            airbnb_data = scrape_airbnb(driver)
            all_data.extend(airbnb_data)
        except Exception as e:
            print(f"  ❌ Error scraping Airbnb: {e}")
        
        # Scrape Stripe  
        try:
            stripe_data = scrape_stripe(driver)
            all_data.extend(stripe_data)
        except Exception as e:
            print(f"  ❌ Error scraping Stripe: {e}")
        
        # Scrape OpenAI
        try:
            openai_data = scrape_openai(driver)
            all_data.extend(openai_data)
        except Exception as e:
            print(f"  ❌ Error scraping OpenAI: {e}")
        
        driver.quit()
        
        # Save to CSV
        if all_data:
            print(f"\n{'='*70}")
            print(f"💾 SAVING RESULTS")
            print(f"{'='*70}")
            
            df = pd.DataFrame(all_data, columns=["source_url", "job_link"])
            
            # Get project path
            script_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(os.path.dirname(script_dir))
            output_dir = os.path.join(project_root, 'data', 'raw')
            os.makedirs(output_dir, exist_ok=True)
            
            output_path = os.path.join(output_dir, 'job_links.csv')
            df.to_csv(output_path, index=False)
            
            print(f"\n✅ SUCCESS!")
            print(f"{'='*70}")
            print(f"Total job links:     {len(df)}")
            print(f"Output file:         {output_path}")
            print(f"\nBreakdown by source:")
            for source, count in df['source_url'].value_counts().items():
                print(f"  • {source.split('/')[-2]}: {count} jobs")
            print(f"{'='*70}")
        else:
            print("❌ No job links collected!")
            
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass


if __name__ == "__main__":
    main()
