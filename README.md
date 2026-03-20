# Job Market Intelligence System

This project is designed to gather and analyze job market intelligence using web scraping and browser automation technologies.

## Technologies Used
- **Selenium**: For browser automation to interact with dynamic web pages.
- **Scrapy**: For efficient web scraping and data extraction.

## Project Structure
- `selenium/`: Contains scripts for browser automation tasks.
- `scrapy_project/`: Houses the Scrapy spider and related scraping logic.
- `data/raw/`: Stores raw data files, including `job_links.csv` for collected job links.
- `data/final/`: Contains processed data files, such as `jobs.csv` for cleaned job data.
- `analysis/`: Includes scripts and notebooks for data analysis and insights.
- `docs/`: Documentation and reports generated from the analysis.

## Setup
1. Install dependencies: `pip install selenium scrapy`
2. Configure your environment variables for any API keys or credentials if needed.
3. Run the scraping scripts as per the instructions in each module.

## Usage
- Use Selenium scripts in `selenium/` for automated browsing.
- Execute Scrapy spiders in `scrapy_project/` to scrape job data.
- Analyze data using scripts in `analysis/`.
- Refer to `docs/` for detailed reports.

## Contributing
Please follow standard Python coding practices and add tests for new features.

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