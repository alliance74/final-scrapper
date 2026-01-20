# 🎉 Events & Deals Scraper API

A complete, production-ready web scraping and API system for Greek events and deals with **continuous background scraping**.

## ✨ Features

- 🔄 **Continuous Scraping** - Automatic scheduled scraping (hourly, daily, etc.)
- 🌐 **Multiple Sources** - Scrapes 4 Greek event websites
- 🔀 **Data Transformation** - Standardizes all data into unified format
- 📄 **Combined JSON Export** - All events in one standardized JSON file
- 🗄️ **Database Storage** - SQLite, PostgreSQL, or MySQL support
- 🚀 **REST API** - FastAPI-powered endpoints
- 🐳 **Docker Ready** - Easy deployment with Docker
- ☁️ **Cloud Deploy** - One-click deploy to Railway, Render, etc.
- 📊 **Monitoring** - Built-in scheduler status and statistics
- 🔍 **Search & Filter** - Filter by source, category, search keywords

## 📋 Quick Links

- **[🚀 Get Started (3 Steps)](GET_STARTED.md)** ⭐ START HERE
- **[🚂 Railway Deployment](RAILWAY_DEPLOY.md)** ⭐ WORKS ON RAILWAY!
- **[📚 Documentation Index](DOCS_INDEX.md)** - All docs
- **[5-Minute Deploy Guide](QUICKSTART.md)** ⚡
- **[Full Deployment Guide](DEPLOYMENT.md)** 📚
- **[API Documentation](README_API.md)** 📖
- **[Data Transformer Guide](TRANSFORMER_GUIDE.md)** 🔀
- **[Complete Summary](FINAL_SUMMARY.md)** 📝
- **[Workflow Guide](WORKFLOW.md)** 🔄
- **[Architecture](ARCHITECTURE.md)** 🏗️

## 🚀 Quick Start

### Option 1: Local Setup

```bash
# 1. Clone repository
git clone your-repo
cd your-repo

# 2. Run setup
python setup.py

# 3. Edit .env file
# Set SCRAPER_SCHEDULE=every_6_hours

# 4. Start API
python run_api.py

# 5. Visit http://localhost:8000/docs
```

### Option 2: Docker

```bash
# 1. Clone and configure
git clone your-repo
cd your-repo
cp .env.example .env

# 2. Run with Docker Compose
docker-compose up -d

# 3. Visit http://localhost:8000/docs
```

### Option 3: Deploy to Railway (Recommended)

```bash
# 1. Install Railway CLI
npm install -g @railway/cli

# 2. Login and deploy
railway login
railway init
railway up

# 3. Add PostgreSQL
railway add --database postgresql

# 4. Set environment variables
railway variables set HEADLESS_MODE=True
railway variables set SCRAPER_SCHEDULE=every_6_hours
railway variables set SCRAPER_MAX_EVENTS=100

# 5. Get your URL
railway domain
```

## 📡 API Endpoints

### Events
```bash
GET  /events              # Get all events
GET  /events?source=culture_gov&limit=20
GET  /events?search=concert
GET  /events/{id}         # Get specific event
```

### Deals
```bash
GET  /deals               # Get all deals
GET  /deals/{id}          # Get specific deal
```

### Scraping
```bash
POST /scrape              # Run scrapers (background)
POST /scrape/sync         # Run scrapers (wait for completion)
```

### Monitoring
```bash
GET  /stats               # Statistics
GET  /scheduler/status    # Scheduler info
GET  /health              # Health check
GET  /combined-events     # Get combined JSON file
```

### Documentation
```bash
GET  /docs                # Swagger UI
GET  /redoc               # ReDoc
```

## 🔄 Data Transformation

All scraped data is automatically transformed into a **standardized format** before storage:

```json
{
  "id": 1342,
  "title": "Event Title",
  "description": "Event description...",
  "date": "2026-02-09",
  "region": "Αττική",
  "category": "Cultural",
  "categoryColor": "#F39C12",
  "location": "Venue address",
  "venue": "Venue name",
  "url": "https://example.com/event",
  "image": "https://example.com/image.jpg",
  "price": 0,
  "source": "More.com"
}
```

**Benefits:**
- ✅ Consistent format across all sources
- ✅ Clean, normalized data
- ✅ Combined JSON export available
- ✅ Easy frontend integration

See [TRANSFORMER_GUIDE.md](TRANSFORMER_GUIDE.md) for details.

## 🔄 Continuous Scraping

The system automatically scrapes events at scheduled intervals:

**Configure in `.env`:**
```bash
SCRAPER_SCHEDULE=every_6_hours
# Options: hourly, every_6_hours, every_12_hours, twice_daily, daily

SCRAPER_MAX_EVENTS=100
SCRAPER_RUN_ON_STARTUP=True
```

**Check status:**
```bash
curl http://localhost:8000/scheduler/status
```

## 🌐 Data Sources

1. **Culture.gov.gr** - Greek Ministry of Culture events
2. **VisitGreece.gr** - Tourism and cultural events
3. **Pigolampides.gr** - Blog posts and event reviews
4. **More.com** - Event tickets and shows

## 📊 Example Usage

### Get Latest Events
```python
import requests

response = requests.get('http://localhost:8000/events?limit=10')
events = response.json()

for event in events:
    print(f"{event['title']} - {event['date']}")
```

### Search Events
```bash
curl "http://localhost:8000/events?search=concert&category=music"
```

### Get Combined JSON
```bash
curl http://localhost:8000/combined-events
```

This returns all events in standardized format from a single JSON file.

### Get Statistics
```bash
curl http://localhost:8000/stats
```

Response:
```json
{
  "total_events": 450,
  "total_deals": 23,
  "events_by_source": {
    "culture_gov": 120,
    "visitgreece": 180,
    "pigolampides": 100,
    "more_events": 50
  }
}
```

## 🗄️ Database

### SQLite (Default)
```bash
DATABASE_URL=sqlite:///./events_deals.db
```

### PostgreSQL (Recommended for Production)
```bash
DATABASE_URL=postgresql://user:password@localhost/events_db
pip install psycopg2-binary
```

### MySQL
```bash
DATABASE_URL=mysql://user:password@localhost/events_db
pip install pymysql
```

## 🐳 Docker Deployment

### Docker Compose (with PostgreSQL)
```bash
docker-compose up -d
```

### Docker Only
```bash
docker build -t events-api .
docker run -d -p 8000:8000 \
  -e HEADLESS_MODE=True \
  -e SCRAPER_SCHEDULE=every_6_hours \
  events-api
```

## ☁️ Cloud Deployment

### Railway (Easiest)
1. Connect GitHub repo
2. Add PostgreSQL database
3. Set environment variables
4. Deploy automatically

### Render
1. Create web service from repo
2. Add PostgreSQL
3. Configure environment
4. Deploy

### DigitalOcean / AWS / VPS
See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed guides.

## 📁 Project Structure

```
.
├── api.py                          # FastAPI application
├── database.py                     # Database models
├── scraper_manager.py              # Scraper orchestration
├── scheduler.py                    # Background scheduler
├── scrapers/
│   ├── culture_final_scraper.py
│   ├── visitgreece_detailed_scraper.py
│   ├── pigolampides_scraper.py
│   └── more_events_scraper_optimized.py
├── Dockerfile                      # Docker configuration
├── docker-compose.yml              # Multi-container setup
├── requirements.txt                # Python dependencies
├── .env                            # Environment variables
└── docs/
    ├── QUICKSTART.md              # 5-minute deploy guide
    ├── DEPLOYMENT.md              # Full deployment guide
    ├── README_API.md              # API documentation
    └── PROJECT_SUMMARY.md         # Project overview
```

## ⚙️ Configuration

### Environment Variables

```bash
# Chrome/Selenium
CHROME_DRIVER_PATH=auto
HEADLESS_MODE=True

# Database
DATABASE_URL=sqlite:///./events_deals.db

# API
API_HOST=0.0.0.0
API_PORT=8000

# Scheduler
SCRAPER_SCHEDULE=every_6_hours
SCRAPER_MAX_EVENTS=100
SCRAPER_RUN_ON_STARTUP=True
```

## 🧪 Testing

```bash
# Test API endpoints
python test_api.py

# Manual scraper run
python run_scrapers.py --headless --max-events 50

# Test individual scraper
python culture_final_scraper.py
```

## 📈 Monitoring

### Check Scheduler Status
```bash
curl http://localhost:8000/scheduler/status
```

### View Logs
```bash
# Docker Compose
docker-compose logs -f api

# Docker
docker logs -f container-name

# Railway
railway logs
```

## 🔧 Troubleshooting

### ChromeDriver Issues
- Ensure Chrome is installed
- Set `CHROME_DRIVER_PATH=auto`
- Use `HEADLESS_MODE=True` in production

### Database Locked (SQLite)
- Use PostgreSQL for production
- Or ensure single-writer access

### Memory Issues
- Reduce `SCRAPER_MAX_EVENTS`
- Use less frequent schedule
- Upgrade instance size

## 💰 Cost Estimates

| Platform | Free Tier | Paid |
|----------|-----------|------|
| Railway | 500h/month + $5 credit | $5-20/month |
| Render | 750h/month | $7-25/month |
| DigitalOcean | No | $12-25/month |
| AWS | 12 months | $15-50/month |

**Recommendation:** Start with Railway or Render free tier.

## 🎯 Recommended Configurations

### Development
```bash
SCRAPER_SCHEDULE=daily
SCRAPER_MAX_EVENTS=50
HEADLESS_MODE=False
```

### Production (Light)
```bash
SCRAPER_SCHEDULE=daily
SCRAPER_MAX_EVENTS=100
HEADLESS_MODE=True
```

### Production (Heavy)
```bash
SCRAPER_SCHEDULE=every_6_hours
SCRAPER_MAX_EVENTS=200
HEADLESS_MODE=True
```

## 📚 Documentation

- **[QUICKSTART.md](QUICKSTART.md)** - Deploy in 5 minutes
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Detailed deployment guide
- **[README_API.md](README_API.md)** - Complete API documentation
- **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** - Project overview

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Make changes
4. Test thoroughly
5. Submit pull request

## 📝 License

MIT License - Use freely for your projects!

## 🆘 Support

- Check logs for errors
- Read documentation
- Test endpoints with `/docs`
- Monitor `/health` and `/scheduler/status`

## 🎉 What's Next?

1. ✅ Deploy to cloud (see QUICKSTART.md)
2. ✅ Configure continuous scraping
3. ✅ Monitor with `/scheduler/status`
4. ✅ Integrate with your frontend
5. ✅ Scale as needed

---

**Made with ❤️ for the Greek events community**
#   s c r a p e r - f o r - m a z i -  
 