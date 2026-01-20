"""
Quick scheduler test - just verifies it can start/stop
"""
import os

# Set test environment
os.environ['SCRAPER_SCHEDULE'] = 'daily'
os.environ['SCRAPER_MAX_EVENTS'] = '5'
os.environ['SCRAPER_RUN_ON_STARTUP'] = 'False'  # Don't run immediately

from scheduler import ScraperScheduler, get_scheduler_status
from database import init_db
import json

def quick_test():
    """Quick test of scheduler functionality"""
    print("="*60)
    print("Quick Scheduler Test")
    print("="*60)
    
    # Initialize database
    print("\n[1/5] Initializing database...")
    try:
        init_db()
        print("      ✓ Database initialized")
    except Exception as e:
        print(f"      ✗ Error: {e}")
        return False
    
    # Create scheduler
    print("\n[2/5] Creating scheduler...")
    try:
        scheduler = ScraperScheduler()
        print("      ✓ Scheduler created")
    except Exception as e:
        print(f"      ✗ Error: {e}")
        return False
    
    # Start scheduler
    print("\n[3/5] Starting scheduler...")
    try:
        scheduler.start()
        print("      ✓ Scheduler started")
    except Exception as e:
        print(f"      ✗ Error: {e}")
        return False
    
    # Check status
    print("\n[4/5] Checking scheduler status...")
    try:
        status = get_scheduler_status()
        print(f"      Running: {status['running']}")
        print(f"      Jobs: {len(status['jobs'])}")
        
        if status['jobs']:
            for job in status['jobs']:
                print(f"\n      Job Details:")
                print(f"        ID: {job['id']}")
                print(f"        Name: {job['name']}")
                print(f"        Next Run: {job['next_run']}")
        
        print("\n      ✓ Status retrieved successfully")
    except Exception as e:
        print(f"      ✗ Error: {e}")
        return False
    
    # Stop scheduler
    print("\n[5/5] Stopping scheduler...")
    try:
        scheduler.stop()
        print("      ✓ Scheduler stopped")
    except Exception as e:
        print(f"      ✗ Error: {e}")
        return False
    
    print("\n" + "="*60)
    print("✅ All Tests Passed!")
    print("="*60)
    print("\nScheduler is working correctly!")
    print("\nNext steps:")
    print("1. Run API: python run_api.py")
    print("2. Check status: curl http://localhost:8000/scheduler/status")
    print("3. Trigger scrape: curl -X POST http://localhost:8000/scrape")
    print("="*60)
    
    return True

if __name__ == "__main__":
    success = quick_test()
    exit(0 if success else 1)
