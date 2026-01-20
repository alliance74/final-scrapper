# 🐘 Neon PostgreSQL Setup Guide

## Problem

You have data in **local SQLite** (`events_deals.db`) but your **Neon PostgreSQL** database is empty.

## Solution

Migrate your data to Neon PostgreSQL.

---

## 📋 Quick Setup (3 Steps)

### Step 1: Get Your Neon Connection String

1. Go to your Neon dashboard
2. Click on your database
3. Copy the connection string

It should look like:
```
postgresql://user:password@ep-xxx-xxx.region.aws.neon.tech/dbname?sslmode=require
```

### Step 2: Run Setup Script

```bash
python setup_neon_database.py
```

When prompted, paste your Neon connection string.

**This will:**
1. Connect to Neon
2. Create tables (events, deals)
3. Load existing JSON data
4. Transform to standard format
5. Save to Neon database

### Step 3: Update Your .env File

```bash
# Replace this line in .env:
DATABASE_URL=sqlite:///./events_deals.db

# With your Neon URL:
DATABASE_URL=postgresql://user:password@ep-xxx.region.aws.neon.tech/dbname?sslmode=require
```

---

## ✅ Verify It Works

### Check Database

```bash
python check_db.py
```

Should show events from Neon database.

### Test API

```bash
# Start API
python run_api.py

# In another terminal
curl http://localhost:8000/events?limit=5
```

---

## 🔄 Alternative: Migrate Existing SQLite Data

If you want to migrate the exact data from SQLite:

```bash
python migrate_to_neon.py
```

This will copy all 22 events from SQLite to Neon.

---

## 🚂 For Railway Deployment

When deploying to Railway:

1. **Don't use Neon** - Railway provides PostgreSQL
2. Railway sets `DATABASE_URL` automatically
3. Just deploy and it works

**OR**

If you want to use Neon with Railway:

1. Set up Neon database (using script above)
2. In Railway, set environment variable:
   ```
   DATABASE_URL=your_neon_connection_string
   ```
3. Deploy

---

## 📊 Current Situation

### Local SQLite
- ✅ Has 22 events
- ✅ Working locally
- ❌ Can't be used in production

### Neon PostgreSQL
- ❌ Currently empty (0 tables)
- ✅ Can be used in production
- ✅ Can be populated with script

---

## 🎯 Recommended Approach

### For Local Development
Keep using SQLite:
```bash
DATABASE_URL=sqlite:///./events_deals.db
```

### For Production (Railway)
Use Railway's PostgreSQL:
```bash
# Railway sets this automatically
DATABASE_URL=postgresql://...railway.app/...
```

### For Production (Other)
Use Neon:
```bash
DATABASE_URL=postgresql://...neon.tech/...
```

---

## 🔧 Troubleshooting

### "No tables in public schema"

**Problem:** Neon database is empty

**Solution:** Run `python setup_neon_database.py`

### "Connection failed"

**Problem:** Wrong connection string

**Solution:** 
1. Check connection string format
2. Ensure `?sslmode=require` is at the end
3. Verify credentials

### "No events found"

**Problem:** JSON files not found

**Solution:**
1. Run scrapers first: `python test_save_existing_data.py`
2. Or use migration: `python migrate_to_neon.py`

---

## 📝 Summary

**Current Status:**
- Local SQLite: ✅ 22 events
- Neon PostgreSQL: ❌ Empty

**To Fix:**
```bash
# Option 1: Setup fresh (recommended)
python setup_neon_database.py

# Option 2: Migrate existing
python migrate_to_neon.py

# Then update .env
DATABASE_URL=your_neon_url
```

**For Railway:**
- Don't worry about Neon
- Railway provides PostgreSQL
- Just deploy and it works

---

## 🎉 After Setup

Once Neon is populated:

1. ✅ Update `.env` with Neon URL
2. ✅ Restart API
3. ✅ Test endpoints
4. ✅ Deploy to production

Your data will be in Neon and accessible from anywhere!
