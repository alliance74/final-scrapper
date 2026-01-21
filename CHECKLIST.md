# 🎯 Quick Deployment Checklist

## ✅ Pre-Deployment (Local Testing)

- [ ] Run component tests
  ```bash
  python test_components.py
  ```

- [ ] Test API locally
  ```bash
  python run_api.py
  # Visit http://localhost:8000/docs
  ```

- [ ] Verify all scrapers work (optional)
  ```bash
  python run_scrapers.py --headless --max-events 10
  ```

---

## ✅ GitHub Setup

- [ ] Initialize git (if not done)
  ```bash
  git init
  ```

- [ ] Add all files
  ```bash
  git add .
  ```

- [ ] Commit
  ```bash
  git commit -m "Ready for Railway deployment"
  ```

- [ ] Create GitHub repo and push
  ```bash
  git remote add origin <your-repo-url>
  git push -u origin main
  ```

---

## ✅ Railway Deployment

### Option A: Via Dashboard (Recommended for beginners)

- [ ] Go to https://railway.app
- [ ] Click "New Project"
- [ ] Select "Deploy from GitHub repo"
- [ ] Choose your repository
- [ ] Click "Add Database" → PostgreSQL
- [ ] Go to Variables tab, add:
  - `HEADLESS_MODE=True`
  - `SCRAPER_SCHEDULE=every_6_hours`
  - `SCRAPER_MAX_EVENTS=100`
  - `SCRAPER_RUN_ON_STARTUP=True`
- [ ] Go to Settings → Generate Domain
- [ ] Wait for deployment to complete

### Option B: Via CLI (Recommended for advanced users)

- [ ] Install Railway CLI
  ```bash
  npm install -g @railway/cli
  ```

- [ ] Login
  ```bash
  railway login
  ```

- [ ] Initialize project
  ```bash
  railway init
  ```

- [ ] Add PostgreSQL
  ```bash
  railway add --database postgresql
  ```

- [ ] Set environment variables
  ```bash
  railway variables set HEADLESS_MODE=True
  railway variables set SCRAPER_SCHEDULE=every_6_hours
  railway variables set SCRAPER_MAX_EVENTS=100
  railway variables set SCRAPER_RUN_ON_STARTUP=True
  ```

- [ ] Deploy
  ```bash
  railway up
  ```

- [ ] Generate domain
  ```bash
  railway domain
  ```

---

## ✅ Post-Deployment Verification

- [ ] Check health
  ```bash
  curl https://your-app.up.railway.app/health
  ```

- [ ] Visit API docs
  ```
  https://your-app.up.railway.app/docs
  ```

- [ ] Check scheduler status
  ```bash
  curl https://your-app.up.railway.app/scheduler/status
  ```

- [ ] Test events endpoint
  ```bash
  curl https://your-app.up.railway.app/events
  ```

- [ ] View logs
  ```bash
  railway logs
  ```

---

## ✅ Important URLs

After deployment, save these URLs:

- API Documentation: `https://your-app.up.railway.app/docs`
- Events Endpoint: `https://your-app.up.railway.app/events`
- Combined Events: `https://your-app.up.railway.app/combined-events`
- Statistics: `https://your-app.up.railway.app/stats`
- Health Check: `https://your-app.up.railway.app/health`
- Scheduler Status: `https://your-app.up.railway.app/scheduler/status`

---

## 🎉 You're Done!

Your scraper is now running in production and will automatically scrape events every 6 hours!

## Need Help?

See `DEPLOY_RAILWAY.md` for detailed instructions and troubleshooting.
