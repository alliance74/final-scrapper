# Greek Events & Deals Scraper API

Production-ready web scraping and API system for Greek events and deals.

## Features

- 🔄 Continuous scraping from 4 Greek event websites
- 🔀 Data transformation into standardized format
- 🚀 FastAPI REST endpoints
- 📊 Background scheduler
- 🗄️ PostgreSQL/SQLite database support

## Quick Start (Local)

```bash
# Install dependencies
pip install -r requirements.txt

# Run API
python run_api.py

# Visit http://localhost:8000/docs
```

## Deploy to Railway

1. Install Railway CLI:
```bash
npm install -g @railway/cli
```

2. Login and initialize:
```bash
railway login
railway init
```

3. Add PostgreSQL database:
```bash
railway add --database postgresql
```

4. Set environment variables:
```bash
railway variables set HEADLESS_MODE=True
railway variables set SCRAPER_SCHEDULE=every_6_hours
railway variables set SCRAPER_MAX_EVENTS=100
railway variables set SCRAPER_RUN_ON_STARTUP=True
```

5. Deploy:
```bash
railway up
```

6. Get your URL:
```bash
railway domain
```

## Environment Variables

```
HEADLESS_MODE=True
SCRAPER_SCHEDULE=every_6_hours
SCRAPER_MAX_EVENTS=100
SCRAPER_RUN_ON_STARTUP=True
DATABASE_URL=<auto-set-by-railway>
```

## API Endpoints

- `GET /events` - Get all events
- `GET /combined-events` - Get combined JSON
- `POST /scrape` - Trigger scraping
- `GET /stats` - Get statistics
- `GET /scheduler/status` - Scheduler status
- `GET /docs` - API documentation

## Project Structure

```
.
├── api.py                              # FastAPI application
├── database.py                         # Database models
├── scraper_manager.py                  # Scraper orchestration
├── data_transformer.py                 # Data standardization
├── scheduler.py                        # Background scheduler
├── scrapers/
│   ├── culture_final_scraper.py
│   ├── visitgreece_detailed_scraper.py
│   ├── pigolampides_scraper.py
│   └── more_events_scraper_optimized.py
├── start.py                            # Production starter
└── requirements.txt                    # Dependencies
```
