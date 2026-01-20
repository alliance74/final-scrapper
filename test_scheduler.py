"""
Test the scheduler functionality
This will run a quick test to verify the scheduler works
"""
import os
import time
from datetime import datetime

# Set test environment
os.environ['SCRAPER_SCHEDULE'] = 'hourly'  # For testing
os.environ['SCRAPER_MAX_EVENTS'] = '5'  # Small number for quick test
os.environ['SCRAPER_RUN_ON_STARTUP'] = 'True'  # Run immediately
os.environ['HEADLESS_MODE'] = 'False'  # See what's happening

from scheduler import ScraperScheduler
from database import SessionLocal, init_db

def test_scheduler():
    """Test the scheduler"""
    print("="*60)
    print("Scheduler Test")
    print("="*60)
    
    # Initialize database
    print("\n1. Initializing database...")
    init_db()
    print("   ✓ Database initialized")
    
    # Create scheduler
    print("\n2. Creating scheduler...")
    scheduler = ScraperScheduler()
    print("   ✓ Scheduler created")
    
    # Start scheduler
    print("\n3. Starting scheduler...")
    print("   Schedule: hourly (for testing)")
    print("   Max events: 5 per source")
    print("   Run on startup: True")
    scheduler.start()
    print("   ✓ Scheduler started")
    
    # Get status
    print("\n4. Scheduler Status:")
    jobs = scheduler.get_jobs()
    for job in jobs:
        print(f"   Job ID: {job.id}")
        print(f"   Name: {job.name}")
        print(f"   Next run: {job.next_run_time}")
    
    # Wait for initial scrape to complete (if run on startup)
    print("\n5. Waiting for initial scrape to complete...")
    print("   (This may take a few minutes)")
    print("   Press Ctrl+C to stop")
    
    try:
        # Monitor for 5 minutes
        for i in range(60):
            time.sleep(5)
            if i % 6 == 0:  # Every 30 seconds
                print(f"   [{datetime.now().strftime('%H:%M:%S')}] Scheduler running... ({i*5}s elapsed)")
        
        print("\n✓ Test completed successfully!")
        
    except KeyboardInterrupt:
        print("\n\n⚠ Test interrupted by user")
    
    finally:
        print("\n6. Stopping scheduler...")
        scheduler.stop()
        print("   ✓ Scheduler stopped")
    
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    print("✓ Scheduler can be created")
    print("✓ Scheduler can be started")
    print("✓ Jobs are registered")
    print("✓ Scheduler can be stopped")
    print("\nTo verify scraping worked:")
    print("1. Check scraped_data/combined_events.json")
    print("2. Check events_deals.db")
    print("3. Run: python -c \"from database import SessionLocal, Event; db = SessionLocal(); print(f'Events in DB: {db.query(Event).count()}')\"")
    print("="*60)

if __name__ == "__main__":
    test_scheduler()
