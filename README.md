# Job Market Intelligence System

This project collects, processes, and analyzes job market data from selected company career portals using Selenium + Scrapy. It is built as an end-to-end pipeline: discover job links, extract structured job fields, clean records, and generate visual insights.

## Core Features

- Dynamic job link scraping from modern JavaScript-heavy career pages.
- Role-targeted filtering support in Selenium (for selected job-title patterns).
- Robust scraping fallback flow (Selenium for URLs, Scrapy for extraction).
- Structured output datasets for downstream analysis.
- Skill keyword extraction and role-family categorization logic.
- Insight visualizations for skills, companies, locations, and entry-level share.
- Branch-based workflow (`develop`, `feature/*`, `bugfix/*`, `release/*`) for maintainable collaboration.

## Tech Stack

- **Python** for the full data pipeline.
- **Selenium** for browser automation and dynamic link discovery.
- **Scrapy** for scalable page crawling and field extraction.
- **Pandas** for cleaning and tabular transformations.
- **Matplotlib / NumPy** for visualization and summary analytics.

## End-to-End Pipeline

1. **Link Discovery (`selenium/`)**
   - Loads source career pages.
   - Scrolls pages to reveal lazy-loaded jobs.
   - Captures candidate job URLs with optional title-based filtering.
   - Writes link inventory to `data/raw/job_links.csv`.

2. **Job Extraction (`scrapy_project/`)**
   - Reads links from raw CSV.
   - Crawls job detail pages.
   - Extracts fields like `job_title`, `company`, `location`, `description`, `skills`, and `job_url`.
   - Writes cleaned records to `data/final/jobs.csv`.

3. **Analysis (`analysis/`)**
   - Aggregates role and skills trends.
   - Produces charts for top skills, role families, company distribution, and more.
   - Stores generated screenshots in `docs/`.

## Project Structure

- `selenium/` - Selenium scripts for dynamic job-link scraping.
- `scrapy_project/` - Scrapy spider, items, and pipelines for structured extraction.
- `data/raw/` - Raw link outputs (`job_links.csv`).
- `data/final/` - Final cleaned dataset (`jobs.csv`).
- `analysis/` - Analysis scripts (chart generation logic).
- `docs/` - Generated charts and documentation.

## Quick Start

1. Install requirements:
   - `pip install -r requirements.txt`
2. Run Selenium link scraper:
   - `python selenium/job_scraper_v2.py`
3. Run Scrapy extractor:
   - `cd scrapy_project`
   - `python -m scrapy crawl job_links`
4. Generate analysis visuals:
   - `cd ..`
   - `python analysis/job_insights.py --csv data/final/jobs.csv --plot`

## Data Outputs

- `data/raw/job_links.csv`
  - Source-level list of discovered job URLs.
- `data/final/jobs.csv`
  - Structured records with extracted and cleaned job metadata.

## Documentation and Visual Reports

All generated screenshots are maintained in `docs/`.  
A gallery-style report is available at `docs/README.md`.

## Reliability Notes

- Windows console encoding can fail on emoji output in some shells; logging is kept plain-text for stability.
- Dynamic career sites can change selectors over time; fallback link logic is used to reduce breakage.
- Some pages may block or throttle requests; retries and partial outputs are expected in long runs.

## Contributing

Please follow standard Python coding practices and include tests/checks for new behavior where possible.

## Git Branching Strategy

This project uses a feature-branch workflow to organize work and maintain code quality.

### Recommended Branches

| Branch | Purpose | Example Usage |
|--------|---------|---|
| `main` | Stable final version | Only tested code should reach this branch |
| `develop` | Integration branch | All reviewed features are merged here first |
| `feature/*` | Task-specific work | feature/selenium-filtering, feature/scrapy-parser |
| `bugfix/*` | Fixes for issues discovered during review | bugfix/date-parser, bugfix/duplicate-links |
| `release/*` | Optional final submission hardening | release/v1.0-assignment |

### Workflow
1. **Create feature branch** from `develop`: `git checkout -b feature/your-feature develop`
2. **Commit changes** with descriptive messages
3. **Push to remote**: `git push origin feature/your-feature`
4. **Create Pull Request** to merge into `develop`
5. **After review**, merge to `develop`
6. **From `develop`**, create PR to merge into `main` for releases

## License
[Specify your license here]