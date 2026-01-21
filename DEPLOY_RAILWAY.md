# 🚀 Railway Deployment Guide

## Prerequisites

1. GitHub account
2. Railway account (sign up at https://railway.app)
3. Your code pushed to GitHub

---

## Method 1: Deploy via Railway Dashboard (Easiest)

### Step 1: Push to GitHub

```bash
# If not already a git repo
git init
git add .
git commit -m "Initial commit - Events scraper API"

# Create GitHub repo and push
git remote add origin <your-github-repo-url>
git push -u origin main
```

### Step 2: Deploy on Railway

1. Go to https://railway.app
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Choose your repository
5. Railway will auto-detect the Dockerfile and deploy

### Step 3: Add PostgreSQL Database

1. In your Railway project, click "New"
2. Select "Database" → "PostgreSQL"
3. Railway automatically sets `DATABASE_URL` environment variable

### Step 4: Set Environment Variables

In Railway dashboard, go to Variables tab and add:

```
HEADLESS_MODE=True
SCRAPER_SCHEDULE=every_6_hours
SCRAPER_MAX_EVENTS=100
SCRAPER_RUN_ON_STARTUP=True
CHROME_DRIVER_PATH=auto
```

### Step 5: Generate Domain

1. Go to Settings tab
2. Click "Generate Domain"
3. Your API will be available at: `https://your-app.up.railway.app`

---

## Method 2: Deploy via Railway CLI

### Step 1: Install Railway CLI

```bash
npm install -g @railway/cli
```

### Step 2: Login

```bash
railway login
```

### Step 3: Initialize Project

```bash
cd c:\Users\HP\Videos\scaraper
railway init
```

Select "Create new project" and give it a name.

### Step 4: Add PostgreSQL

```bash
railway add --database postgresql
```

### Step 5: Set Environment Variables

```bash
railway variables set HEADLESS_MODE=True
railway variables set SCRAPER_SCHEDULE=every_6_hours
railway variables set SCRAPER_MAX_EVENTS=100
railway variables set SCRAPER_RUN_ON_STARTUP=True
railway variables set CHROME_DRIVER_PATH=auto
```

### Step 6: Deploy

```bash
railway up
```

Railway will build and deploy your application.

### Step 7: Generate Domain

```bash
railway domain
```

Or generate via dashboard.

### Step 8: View Logs

```bash
railway logs
```

---

## Verification

Once deployed, test your API:

### 1. Health Check
```bash
curl https://your-app.up.railway.app/health
```

### 2. API Documentation
Visit: `https://your-app.up.railway.app/docs`

### 3. Check Scheduler Status
```bash
curl https://your-app.up.railway.app/scheduler/status
```

### 4. Get Events
```bash
curl https://your-app.up.railway.app/events
```

### 5. Get Combined Events
```bash
curl https://your-app.up.railway.app/combined-events
```

---

## Important Files for Railway

✅ **Dockerfile** - Railway uses this automatically
✅ **start.py** - Production entry point
✅ **requirements.txt** - Python dependencies
✅ **railway.toml** - Railway configuration (optional)

---

## Environment Variables Reference

| Variable | Value | Description |
|----------|-------|-------------|
| `DATABASE_URL` | Auto-set | PostgreSQL connection (auto-set by Railway) |
| `HEADLESS_MODE` | `True` | Run Chrome in headless mode |
| `SCRAPER_SCHEDULE` | `every_6_hours` | How often to scrape |
| `SCRAPER_MAX_EVENTS` | `100` | Max events per source |
| `SCRAPER_RUN_ON_STARTUP` | `True` | Run scraper when app starts |
| `CHROME_DRIVER_PATH` | `auto` | Auto-detect ChromeDriver |
| `PORT` | Auto-set | Railway sets this automatically |

---

## Schedule Options

Choose one for `SCRAPER_SCHEDULE`:

- `hourly` - Every hour
- `every_6_hours` - Every 6 hours (recommended)
- `every_12_hours` - Every 12 hours
- `twice_daily` - 6 AM and 6 PM
- `daily` - Once daily at 2 AM

---

## Costs

**Free Tier:**
- 500 hours/month
- $5 credit/month
- Enough for development

**Paid:**
- ~$5-10/month for this app
- Pay only for what you use

---

## Troubleshooting

### App not starting?
```bash
railway logs
```
Check for errors in the logs.

### Database connection issues?
Make sure PostgreSQL is added and `DATABASE_URL` is set automatically.

### Chrome/Selenium issues?
Ensure `HEADLESS_MODE=True` is set. Railway's containers support Chrome in headless mode.

### Scraper not running?
Check scheduler status:
```bash
curl https://your-app.up.railway.app/scheduler/status
```

---

## Local Testing Before Deploy

Test everything locally:

```bash
# 1. Run component tests
python test_components.py

# 2. Start API locally
python run_api.py

# 3. Test endpoints
# Visit http://localhost:8000/docs

# 4. Trigger manual scrape
python run_scrapers.py --headless --max-events 10
```

---

## Post-Deployment

### Monitor Your App

```bash
# View logs
railway logs

# Check status
curl https://your-app.up.railway.app/health

# View stats
curl https://your-app.up.railway.app/stats
```

### Update Your App

```bash
# Make changes, then:
git add .
git commit -m "Update"
git push

# Railway auto-deploys on push
```

---

## Quick Reference

```bash
# Railway CLI cheatsheet
railway login           # Login to Railway
railway init            # Create new project
railway link            # Link to existing project
railway up              # Deploy
railway logs            # View logs
railway variables       # Manage env vars
railway domain          # Generate domain
railway status          # Check project status
```

---

## Success! 🎉

Your API is now live at:
- **API Docs:** `https://your-app.up.railway.app/docs`
- **Events:** `https://your-app.up.railway.app/events`
- **Combined JSON:** `https://your-app.up.railway.app/combined-events`
- **Stats:** `https://your-app.up.railway.app/stats`

The scraper will automatically run based on your schedule!
