"""
Quick check of Railway deployment status
"""
import requests
import time

url = "https://final-scrapper-production-317c.up.railway.app"

print("=" * 60)
print("CHECKING RAILWAY DEPLOYMENT")
print("=" * 60)

# Health
print("\n1. Health Check:")
r = requests.get(f"{url}/health")
print(f"   Status: {r.status_code}")
print(f"   Response: {r.json()}")

# Stats
print("\n2. Statistics:")
r = requests.get(f"{url}/stats")
data = r.json()
print(f"   Total Events: {data['total_events']}")
print(f"   By Source: {data['events_by_source']}")

# Events
print("\n3. Events:")
r = requests.get(f"{url}/events?limit=3")
events = r.json()
print(f"   Count: {len(events)}")
if events:
    for e in events[:3]:
        print(f"   - {e['title']} ({e['source']})")

# Scheduler
print("\n4. Scheduler:")
r = requests.get(f"{url}/scheduler/status")
sched = r.json()
print(f"   Running: {sched['running']}")
if sched.get('jobs'):
    for job in sched['jobs']:
        print(f"   Next run: {job.get('next_run', 'N/A')}")

print("\n" + "=" * 60)
if data['total_events'] > 0:
    print(f"✅ SUCCESS! {data['total_events']} events in database")
else:
    print("⏳ No events yet - scraping may still be in progress")
    print("   Check Railway logs or wait a few minutes")
print("=" * 60)
