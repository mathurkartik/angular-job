# Automated Senior Angular Job Scraper

A high-performance, stealth-enabled job scraping pipeline specifically tuned for Senior Angular Engineering roles. It categorizes target companies into three distinct tiers with varying strictness for location, seniority, and stack filtering.

## Features
- **3-Tier Architecture**: Strict filtering for global tech, relaxed for domestic product companies, and minimal for service-based market intelligence.
- **Stealth Browsing**: Uses `playwright-stealth` with identity rotation and pacing to evade Cloudflare/Datadome bot detection.
- **LLM Extraction**: Uses Groq LLM to intelligently extract job listings from unstructured HTML and text.
- **Factory Pattern Scrapers**: Automatically routes companies to Workday, Greenhouse, Lever, Phenom or Generic scrapers.

## Installation

1. Install Python 3.10+
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   playwright install chromium
   ```

## Usage

Run the pipeline in headless mode (default) scraping all categories:
```bash
python main.py
```

Run visibly (headed) to debug scraping:
```bash
python main.py --headed
```

Scrape a specific category:
```bash
python main.py --category main     # Only Category 1
python main.py --category product  # Only Category 2
python main.py --category service  # Only Category 3
```

## Output
Outputs are saved to the `output/` directory:
- `jobs.csv`: Spreadsheets for easy filtering and tracking.
- `jobs.json`: Raw JSON data for programmatic use.
- **Console Report**: A rich, formatted table of the top 20 matches.
