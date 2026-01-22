# ✅ How to Check Your Railway Deployment

## 🎉 Congratulations on deploying!

Now let's verify everything is working correctly.

---

## Method 1: Use the Verification Script (RECOMMENDED)

```bash
python verify_deployment.py https://your-app.up.railway.app
```

This will test all endpoints and give you a full report!

---

## Method 2: Manual Testing

### 1. ✅ Check Health Status

```bash
curl https://your-app.up.railway.app/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "timestamp": "2026-01-21T20:43:00"
}
```

✅ If you see this, your API is running!

---

### 2. 📖 View API Documentation

**Open in browser:**
```
https://your-app.up.railway.app/docs
```

You'll see a beautiful Swagger UI with all endpoints you can test interactively!

---

### 3. ⏰ Check Scheduler Status

```bash
curl https://your-app.up.railway.app/scheduler/status
```

**Expected Response:**
```json
{
  "running": true,
  "jobs": [{
    "id": "scraper_6h",
    "name": "6-Hour Scraper",
    "next_run": "2026-01-22T02:00:00"
  }]
}
```

✅ If `"running": true`, your scheduler is active!

---

### 4. 📊 Check Statistics

```bash
curl https://your-app.up.railway.app/stats
```

**Expected Response:**
```json
{
  "total_events": 150,
  "total_deals": 0,
  "events_by_source": {
    "Culture.gov.gr": 40,
    "VisitGreece.gr": 35,
    "Pigolampides.gr": 50,
    "More.com": 25
  }
}
```

✅ If you see events, scraping has already happened!
⚠️ If `"total_events": 0`, wait for first scrape or trigger manually.

---

### 5. 📅 Get Events

```bash
curl https://your-app.up.railway.app/events?limit=5
```

This returns the latest 5 events from your database.

**Sample Event:**
```json
{
  "id": 1,
  "title": "Event Title",
  "description": "Description...",
  "date": "2026-02-09",
  "location": "Athens",
  "category": "Cultural",
  "source": "Culture.gov.gr",
  "url": "https://..."
}
```

---

### 6. ⭐ Get Combined Events (Standardized Format)

```bash
curl https://your-app.up.railway.app/combined-events
```

This returns all events in the standardized format!

---

### 7. 🔍 Search Events

```bash
# Search by keyword
curl "https://your-app.up.railway.app/events?search=concert"

# Filter by source
curl "https://your-app.up.railway.app/events?source=Culture.gov.gr"

# Filter by category
curl "https://your-app.up.railway.app/events?category=Cultural"

# Combine filters
curl "https://your-app.up.railway.app/events?source=More.com&limit=10"
```

---

## Method 3: Check Railway Logs

### Via Railway CLI:
```bash
railway logs
```

### Via Railway Dashboard:
1. Go to https://railway.app
2. Click on your project
3. Click "Deployments"
4. Click "View Logs"

**Look for:**
- ✅ "API started successfully"
- ✅ "Database initialized"
- ✅ "Scheduler started"
- ✅ "Scraping completed successfully"

---

## 🚨 What If Nothing Is Running Yet?

### Scenario 1: No Events Yet (First Deploy)

If you just deployed, the scraper might not have run yet.

**Trigger manual scrape:**
```bash
curl -X POST https://your-app.up.railway.app/scrape
```

Or wait for the next scheduled run (check `/scheduler/status`).

### Scenario 2: Scheduler Not Running

Check environment variables in Railway dashboard:
- `SCRAPER_SCHEDULE` should be set to `every_6_hours`
- `SCRAPER_RUN_ON_STARTUP` should be `True` or `False`

### Scenario 3: Database Connection Issues

Check Railway dashboard:
- PostgreSQL database should be added
- `DATABASE_URL` should be auto-set

---

## 📈 Monitor Your Deployment

### Real-time Logs:
```bash
railway logs --follow
```

### Check Next Scrape Time:
```bash
curl https://your-app.up.railway.app/scheduler/status
```

### Monitor Events Growth:
```bash
# Check every minute
watch -n 60 'curl -s https://your-app.up.railway.app/stats | grep total_events'
```

---

## 🎯 Expected Behavior Timeline

**Immediately after deployment:**
- ⏱️ 0-2 min: Container building
- ⏱️ 2-3 min: API starts
- ⏱️ 3-5 min: Database connected
- ⏱️ 5 min: Health check passes ✅

**After startup (if SCRAPER_RUN_ON_STARTUP=True):**
- ⏱️ 5-15 min: First scrape runs
- ⏱️ 15+ min: Events appear in database ✅

**Ongoing:**
- 🔄 Every 6 hours: Automatic scraping
- 📊 Events grow continuously

---

## 💡 Quick Verification Checklist

Run these commands (replace YOUR_APP):

```bash
# 1. Health (should return 200)
curl https://YOUR_APP.up.railway.app/health

# 2. Stats (check total_events)
curl https://YOUR_APP.up.railway.app/stats

# 3. Scheduler (should show "running": true)
curl https://YOUR_APP.up.railway.app/scheduler/status

# 4. Events (should return array of events)
curl https://YOUR_APP.up.railway.app/events?limit=3
```

---

## 🔗 Your Live Endpoints

Replace `YOUR_APP` with your Railway URL:

```
https://YOUR_APP.up.railway.app/              → API info
https://YOUR_APP.up.railway.app/docs          → Interactive API docs
https://YOUR_APP.up.railway.app/health        → Health check
https://YOUR_APP.up.railway.app/events        → All events
https://YOUR_APP.up.railway.app/combined-events → Standardized JSON
https://YOUR_APP.up.railway.app/stats         → Statistics
https://YOUR_APP.up.railway.app/scheduler/status → Scheduler info
```

---

## 🎉 Success Indicators

Your deployment is working if:
- ✅ `/health` returns `{"status": "healthy"}`
- ✅ `/docs` shows Swagger UI
- ✅ `/scheduler/status` shows `"running": true`
- ✅ `/stats` shows `total_events > 0` (after first scrape)
- ✅ Railway logs show "API started successfully"

---

## 🆘 Troubleshooting

### Problem: Health check fails
**Solution:** Check Railway logs for errors
```bash
railway logs
```

### Problem: No events in database
**Solution:** Trigger manual scrape
```bash
curl -X POST https://YOUR_APP.up.railway.app/scrape
```

### Problem: Scheduler not running
**Solution:** Check environment variables in Railway dashboard

### Problem: Database connection error
**Solution:** Verify PostgreSQL is added and DATABASE_URL is set

---

## 📞 Get Your Railway URL

If you don't know your URL:

### Via CLI:
```bash
railway domain
```

### Via Dashboard:
1. Go to https://railway.app
2. Click your project
3. Go to Settings
4. See "Domains" section

---

## 🎊 You're Live!

Your Greek Events API is now running 24/7 on Railway!

**Next:** Share your API URL with your frontend team or start building! 🚀
