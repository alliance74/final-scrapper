"""
Verify deployment is working correctly
Run this after deploying to Railway or any platform
"""
import requests
import sys
import json
from datetime import datetime

def test_endpoint(url, name, method='GET', data=None):
    """Test an endpoint and return result"""
    try:
        if method == 'GET':
            response = requests.get(url, timeout=10)
        else:
            response = requests.post(url, json=data, timeout=10)
        
        if response.status_code == 200:
            print(f"  ✓ {name}")
            return True, response.json()
        else:
            print(f"  ✗ {name} (Status: {response.status_code})")
            return False, None
    except Exception as e:
        print(f"  ✗ {name} (Error: {e})")
        return False, None

def verify_deployment(base_url):
    """Verify all critical endpoints"""
    
    print("="*60)
    print("Deployment Verification")
    print("="*60)
    print(f"Testing: {base_url}")
    print("="*60)
    
    results = {
        'passed': 0,
        'failed': 0,
        'tests': []
    }
    
    # Test 1: Health Check
    print("\n[1/7] Testing Health Endpoint...")
    success, data = test_endpoint(f"{base_url}/health", "Health check")
    results['tests'].append(('Health', success))
    if success:
        results['passed'] += 1
        if data:
            print(f"      Status: {data.get('status')}")
            scheduler = data.get('scheduler', {})
            print(f"      Scheduler Running: {scheduler.get('running')}")
    else:
        results['failed'] += 1
    
    # Test 2: Scheduler Status
    print("\n[2/7] Testing Scheduler Status...")
    success, data = test_endpoint(f"{base_url}/scheduler/status", "Scheduler status")
    results['tests'].append(('Scheduler', success))
    if success:
        results['passed'] += 1
        if data:
            print(f"      Running: {data.get('running')}")
            jobs = data.get('jobs', [])
            print(f"      Jobs: {len(jobs)}")
            if jobs:
                for job in jobs:
                    print(f"        - {job.get('name')}: {job.get('next_run')}")
    else:
        results['failed'] += 1
    
    # Test 3: Stats
    print("\n[3/7] Testing Stats Endpoint...")
    success, data = test_endpoint(f"{base_url}/stats", "Statistics")
    results['tests'].append(('Stats', success))
    if success:
        results['passed'] += 1
        if data:
            print(f"      Total Events: {data.get('total_events', 0)}")
            print(f"      Total Deals: {data.get('total_deals', 0)}")
    else:
        results['failed'] += 1
    
    # Test 4: Events Endpoint
    print("\n[4/7] Testing Events Endpoint...")
    success, data = test_endpoint(f"{base_url}/events?limit=5", "Events list")
    results['tests'].append(('Events', success))
    if success:
        results['passed'] += 1
        if data:
            print(f"      Events returned: {len(data)}")
            if data:
                print(f"      Sample: {data[0].get('title', 'N/A')[:50]}")
    else:
        results['failed'] += 1
    
    # Test 5: Combined Events
    print("\n[5/7] Testing Combined Events Endpoint...")
    success, data = test_endpoint(f"{base_url}/combined-events", "Combined events")
    results['tests'].append(('Combined Events', success))
    if success:
        results['passed'] += 1
        if data:
            print(f"      Events in JSON: {len(data)}")
            if data:
                # Verify format
                sample = data[0]
                required_fields = ['id', 'title', 'date', 'category', 'source']
                has_all = all(field in sample for field in required_fields)
                print(f"      Format Valid: {has_all}")
    else:
        results['failed'] += 1
    
    # Test 6: API Docs
    print("\n[6/7] Testing API Documentation...")
    success, _ = test_endpoint(f"{base_url}/docs", "API docs")
    results['tests'].append(('API Docs', success))
    if success:
        results['passed'] += 1
    else:
        results['failed'] += 1
    
    # Test 7: Root Endpoint
    print("\n[7/7] Testing Root Endpoint...")
    success, data = test_endpoint(f"{base_url}/", "Root")
    results['tests'].append(('Root', success))
    if success:
        results['passed'] += 1
    else:
        results['failed'] += 1
    
    # Summary
    print("\n" + "="*60)
    print("RESULTS")
    print("="*60)
    print(f"Passed: {results['passed']}/7")
    print(f"Failed: {results['failed']}/7")
    print()
    
    for test_name, passed in results['tests']:
        status = "✓" if passed else "✗"
        print(f"  {status} {test_name}")
    
    print("="*60)
    
    if results['failed'] == 0:
        print("\n🎉 All tests passed! Deployment is working correctly!")
        print("\nYour API is ready to use:")
        print(f"  - API Docs: {base_url}/docs")
        print(f"  - Health: {base_url}/health")
        print(f"  - Events: {base_url}/events")
        print(f"  - Combined: {base_url}/combined-events")
        return True
    else:
        print(f"\n⚠ {results['failed']} test(s) failed. Check the errors above.")
        print("\nTroubleshooting:")
        print("  1. Check logs: railway logs")
        print("  2. Verify environment variables")
        print("  3. Ensure database is connected")
        print("  4. Wait a few minutes for initial scrape")
        return False

def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("Usage: python verify_deployment.py <base_url>")
        print("\nExamples:")
        print("  python verify_deployment.py http://localhost:8000")
        print("  python verify_deployment.py https://your-app.railway.app")
        sys.exit(1)
    
    base_url = sys.argv[1].rstrip('/')
    success = verify_deployment(base_url)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
