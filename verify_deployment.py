"""
Railway Deployment Verification Script
Check if your deployed API is working correctly
"""
import requests
import sys
from datetime import datetime

def verify_deployment(base_url):
    """Verify all endpoints are working"""
    
    # Remove trailing slash
    base_url = base_url.rstrip('/')
    
    print("=" * 70)
    print("🚀 RAILWAY DEPLOYMENT VERIFICATION")
    print("=" * 70)
    print(f"📡 Testing: {base_url}")
    print(f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    results = {}
    
    # Test 1: Health Check
    print("\n[1/7] Testing Health Check...")
    try:
        r = requests.get(f"{base_url}/health", timeout=10)
        if r.status_code == 200:
            data = r.json()
            print(f"  ✅ Status: {r.status_code}")
            print(f"  ✅ Response: {data}")
            results['health'] = True
        else:
            print(f"  ❌ Status: {r.status_code}")
            results['health'] = False
    except Exception as e:
        print(f"  ❌ Error: {e}")
        results['health'] = False
    
    # Test 2: API Root
    print("\n[2/7] Testing API Root...")
    try:
        r = requests.get(base_url, timeout=10)
        if r.status_code == 200:
            data = r.json()
            print(f"  ✅ Status: {r.status_code}")
            print(f"  ✅ API: {data.get('message', 'N/A')}")
            print(f"  ✅ Version: {data.get('version', 'N/A')}")
            results['root'] = True
        else:
            print(f"  ❌ Status: {r.status_code}")
            results['root'] = False
    except Exception as e:
        print(f"  ❌ Error: {e}")
        results['root'] = False
    
    # Test 3: Scheduler Status
    print("\n[3/7] Testing Scheduler Status...")
    try:
        r = requests.get(f"{base_url}/scheduler/status", timeout=10)
        if r.status_code == 200:
            data = r.json()
            print(f"  ✅ Status: {r.status_code}")
            print(f"  ✅ Running: {data.get('running', False)}")
            if data.get('jobs'):
                for job in data['jobs']:
                    print(f"  ✅ Job: {job.get('name')} - Next run: {job.get('next_run', 'N/A')}")
            results['scheduler'] = True
        else:
            print(f"  ❌ Status: {r.status_code}")
            results['scheduler'] = False
    except Exception as e:
        print(f"  ❌ Error: {e}")
        results['scheduler'] = False
    
    # Test 4: Events Endpoint
    print("\n[4/7] Testing Events Endpoint...")
    try:
        r = requests.get(f"{base_url}/events?limit=5", timeout=10)
        if r.status_code == 200:
            data = r.json()
            print(f"  ✅ Status: {r.status_code}")
            print(f"  ✅ Events returned: {len(data)}")
            if data:
                print(f"  ✅ Sample event: {data[0].get('title', 'N/A')}")
                print(f"     - Source: {data[0].get('source', 'N/A')}")
                print(f"     - Date: {data[0].get('date', 'N/A')}")
            results['events'] = True
        else:
            print(f"  ❌ Status: {r.status_code}")
            results['events'] = False
    except Exception as e:
        print(f"  ❌ Error: {e}")
        results['events'] = False
    
    # Test 5: Statistics
    print("\n[5/7] Testing Statistics...")
    try:
        r = requests.get(f"{base_url}/stats", timeout=10)
        if r.status_code == 200:
            data = r.json()
            print(f"  ✅ Status: {r.status_code}")
            print(f"  ✅ Total Events: {data.get('total_events', 0)}")
            print(f"  ✅ Total Deals: {data.get('total_deals', 0)}")
            if data.get('events_by_source'):
                print(f"  ✅ Events by source:")
                for source, count in data['events_by_source'].items():
                    print(f"     - {source}: {count}")
            results['stats'] = True
        else:
            print(f"  ❌ Status: {r.status_code}")
            results['stats'] = False
    except Exception as e:
        print(f"  ❌ Error: {e}")
        results['stats'] = False
    
    # Test 6: Combined Events
    print("\n[6/7] Testing Combined Events JSON...")
    try:
        r = requests.get(f"{base_url}/combined-events", timeout=10)
        if r.status_code == 200:
            data = r.json()
            print(f"  ✅ Status: {r.status_code}")
            print(f"  ✅ Combined events: {len(data) if isinstance(data, list) else 'N/A'}")
            results['combined'] = True
        else:
            print(f"  ⚠️  Status: {r.status_code} (May not have data yet)")
            results['combined'] = False
    except Exception as e:
        print(f"  ⚠️  Error: {e} (May not have data yet)")
        results['combined'] = False
    
    # Test 7: API Documentation
    print("\n[7/7] Testing API Documentation...")
    try:
        r = requests.get(f"{base_url}/docs", timeout=10)
        if r.status_code == 200:
            print(f"  ✅ Status: {r.status_code}")
            print(f"  ✅ Swagger UI available at: {base_url}/docs")
            results['docs'] = True
        else:
            print(f"  ❌ Status: {r.status_code}")
            results['docs'] = False
    except Exception as e:
        print(f"  ❌ Error: {e}")
        results['docs'] = False
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 VERIFICATION SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status}: {test.upper()}")
    
    print("\n" + "-" * 70)
    print(f"  Score: {passed}/{total} tests passed ({passed/total*100:.0f}%)")
    print("=" * 70)
    
    # Recommendations
    print("\n💡 NEXT STEPS:")
    print("-" * 70)
    
    if results.get('health'):
        print("✅ API is healthy and running!")
    else:
        print("❌ API health check failed - check Railway logs")
    
    if results.get('scheduler'):
        print("✅ Scheduler is running - scraping will happen automatically")
    else:
        print("⚠️  Scheduler may not be running - check environment variables")
    
    if results.get('events') and results.get('stats'):
        print("✅ Database has events - scraping has completed!")
    else:
        print("⚠️  No events yet - trigger manual scrape or wait for scheduler")
        print(f"   Run: curl -X POST {base_url}/scrape")
    
    if not results.get('combined'):
        print("⚠️  Combined events file not ready - wait for first scrape")
    
    print("\n📚 USEFUL LINKS:")
    print("-" * 70)
    print(f"  API Docs: {base_url}/docs")
    print(f"  Health Check: {base_url}/health")
    print(f"  Events: {base_url}/events")
    print(f"  Stats: {base_url}/stats")
    print(f"  Scheduler: {base_url}/scheduler/status")
    print("=" * 70)
    
    return passed == total

if __name__ == "__main__":
    print("\n🚀 Railway Deployment Verification Tool")
    print("=" * 70)
    
    # Get URL from user
    if len(sys.argv) > 1:
        url = sys.argv[1]
    else:
        url = input("\n📡 Enter your Railway URL (e.g., https://your-app.up.railway.app): ").strip()
    
    if not url:
        print("❌ No URL provided!")
        sys.exit(1)
    
    # Ensure URL has protocol
    if not url.startswith('http'):
        url = 'https://' + url
    
    success = verify_deployment(url)
    
    if success:
        print("\n🎉 All tests passed! Your deployment is working perfectly!")
    else:
        print("\n⚠️  Some tests failed. Check the errors above and Railway logs.")
    
    sys.exit(0 if success else 1)
