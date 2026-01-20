# Railway Deployment Guide

## Fixed Issues
✅ Removed empty `railway.json` file that was causing JSON parsing error
✅ Updated Dockerfile to use Railway's `$PORT` environment variable
✅ Railway will auto-detect the Dockerfile

## Deployment Steps

### 1. Push to GitHub
```bash
git add .
git commit -m "Fix Railway deployment configuration"
git push origin main
```

### 2. Deploy on Railway
1. Go to [Railway.app](https://railway.app)
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Choose your repository: `scraper-for-mazi-`
5. Railway will automatically detect the Dockerfile and start building

### 3. Set Environment Variables
In Railway dashboard, go to your project → Variables tab and add:

**Required:**
- `DATABASE_URL` = Your Neon PostgreSQL connection string
  ```
  postgresql://[user]:[password]@[host]/[database]?sslmode=require
  ```

**Recommended:**
- `HEADLESS_MODE` = `True` (already set in Dockerfile)
- `SCRAPER_SCHEDULE` = `every_6_hours`
- `SCRAPER_MAX_EVENTS` = `100`
- `SCRAPER_RUN_ON_STARTUP` = `False` (set to True if you want immediate scraping)

**Optional:**
- `CHROME_DRIVER_PATH` = `auto` (already set in Dockerfile)

### 4. Verify Deployment
Once deployed, Railway will provide a public URL like: `https://your-app.railway.app`

Test the API:
```bash
# Health check
curl https://your-app.railway.app/health

# Get events
curl https://your-app.railway.app/api/events

# Get deals
curl https://your-app.railway.app/api/deals
```

### 5. Monitor Logs
- Go to Railway dashboard → Deployments → View Logs
- Check for successful scraper initialization
- Verify scheduler is running with your configured schedule

## API Endpoints
- `GET /` - API documentation
- `GET /health` - Health check
- `GET /api/events` - Get all events
- `GET /api/deals` - Get all deals
- `GET /api/events/{event_id}` - Get specific event
- `POST /api/scrape` - Manually trigger scraping

## Troubleshooting

### Build Fails
- Check Railway logs for specific error
- Verify all dependencies in `requirements.txt`
- Ensure Dockerfile syntax is correct

### Scrapers Not Running
- Check `HEADLESS_MODE=True` is set
- Verify Chrome installation in logs
- Check scheduler logs for cron job registration

### Database Connection Issues
- Verify `DATABASE_URL` is correctly set
- Ensure Neon database allows connections from Railway IPs
- Check connection string format includes `?sslmode=require`

### Port Issues
- Railway automatically sets `$PORT` environment variable
- Dockerfile now uses `${PORT:-8000}` to handle this

## Next Steps
1. Delete the empty `railway.json` file (already done)
2. Commit and push changes
3. Deploy on Railway
4. Set environment variables
5. Monitor first deployment and scraping cycle
