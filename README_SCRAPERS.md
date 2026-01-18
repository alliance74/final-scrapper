# Greek Events Scrapers

Collection of web scrapers for Greek event websites using Selenium and Chrome.

## Available Scrapers

### 1. Visit Greece Events
**File:** `visitgreece_improved_scraper.py`  
**URL:** https://www.visitgreece.gr/events  
**Features:**
- Scrapes events with pagination support
- Extracts: title, date, location, description, category, price, contact, images
- Handles multiple pages automatically

**Usage:**
```bash
python visitgreece_improved_scraper.py
```

### 2. Greek Ministry of Culture
**File:** `culture_gov_fixed_scraper.py`  
**URL:** https://allofgreeceone.culture.gov.gr/en/  
**Features:**
- Scrapes 968+ cultural events
- Handles infinite scroll and "Load More" buttons
- Extracts: title, date, location, description, category, organizer, images

**Usage:**
```bash
python culture_gov_fixed_scraper.py
```

### 3. Combined Scraper
**File:** `combined_events_scraper.py`  
**Features:**
- Scrapes from all sources in one run
- Combines results into single JSON file
- Provides detailed summary statistics

**Usage:**
```bash
python combined_events_scraper.py
```

## Quick Start

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Configure environment:**
```bash
copy .env.example .env
```

3. **Run a scraper:**
```bash
python visitgreece_improved_scraper.py
```

## Output

All scraped data is saved to `scraped_data/` folder as JSON files:
- `visitgreece_all_events.json` - Visit Greece events
- `culture_gov_all_events.json` - Ministry of Culture events
- `all_greek_events.json` - Combined events from all sources

## Configuration

Edit `.env` file:
```
CHROME_DRIVER_PATH=C:\path\to\chromedriver.exe
HEADLESS_MODE=False
TIMEOUT=20
RETRY_ATTEMPTS=5
```

## Troubleshooting

### ChromeDriver version mismatch
Run the fix script:
```bash
python fix_chromedriver.py
```

### Network timeout
Increase timeout in `.env`:
```
TIMEOUT=30
```

### Too few events scraped
- Check if the website structure changed
- Increase max_events parameter
- Run with `headless=False` to watch the browser

## Event Data Structure

Each event contains:
```json
{
  "url": "event URL",
  "title": "Event title",
  "date": "Event date/time",
  "location": "Venue/location",
  "description": "Event description",
  "category": "Event category",
  "price": "Ticket price",
  "contact": "Contact information",
  "images": ["image URLs"],
  "source": "Source website name",
  "source_url": "Source website URL"
}
```

## Notes

- Scrapers respect website rate limits with delays
- Chrome browser will open unless headless mode is enabled
- Large scraping jobs may take several minutes
- Always check website's robots.txt and terms of service
