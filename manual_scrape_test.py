"""
Manual scrape test - Run scrapers and save to database
"""
from scraper_manager import ScraperManager
from database import SessionLocal, Event, init_db
import json

def manual_scrape():
    """Run a manual scrape with just a few events"""
    
    print("="*60)
    print("Manual Scrape Test")
    print("="*60)
    print("This will scrape 3 events from each source")
    print("and save them to the database.")
    print("="*60)
    
    # Initialize database
    print("\n[1/4] Initializing database...")
    init_db()
    db = SessionLocal()
    print("      ✓ Database initialized")
    
    # Check current count
    before_count = db.query(Event).count()
    print(f"      Events in DB before: {before_count}")
    
    # Run scrapers
    print("\n[2/4] Running scrapers...")
    print("      (This will take a few minutes)")
    print("      Scraping 3 events per source...")
    
    try:
        manager = ScraperManager(db)
        results = manager.run_all_scrapers(
            headless=False,  # So you can see progress
            max_events_per_source=3
        )
        
        print(f"\n      ✓ Scraping complete!")
        print(f"      Results: {results}")
        
    except Exception as e:
        print(f"\n      ✗ Error during scraping: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Check database
    print("\n[3/4] Checking database...")
    after_count = db.query(Event).count()
    print(f"      Events in DB after: {after_count}")
    print(f"      New events added: {after_count - before_count}")
    
    if after_count == 0:
        print("\n      ⚠ No events in database!")
        print("      Checking for errors...")
        
        # Check if combined JSON was created
        import os
        json_path = 'scraped_data/combined_events.json'
        if os.path.exists(json_path):
            with open(json_path, 'r', encoding='utf-8') as f:
                events = json.load(f)
            print(f"      Combined JSON has {len(events)} events")
            if events:
                print("\n      Sample event from JSON:")
                print(json.dumps(events[0], indent=2, ensure_ascii=False)[:500])
        else:
            print("      Combined JSON not found")
        
        return False
    
    # Show sample events
    print("\n[4/4] Sample events from database:")
    events = db.query(Event).limit(5).all()
    
    for i, event in enumerate(events, 1):
        print(f"\n      [{i}] {event.title[:60]}")
        print(f"          Date: {event.date}")
        print(f"          Category: {event.category}")
        print(f"          Source: {event.source}")
        print(f"          URL: {event.url[:60]}...")
    
    # Show full format of first event
    if events:
        print("\n" + "="*60)
        print("Full format of first event:")
        print("="*60)
        
        first = events[0]
        event_dict = {
            'id': first.id,
            'title': first.title,
            'description': first.description[:100] if first.description else None,
            'date': first.date,
            'location': first.location,
            'category': first.category,
            'price': first.price,
            'url': first.url,
            'source': first.source,
            'images': first.images,
            'content': first.content,
        }
        
        print(json.dumps(event_dict, indent=2, ensure_ascii=False))
    
    print("\n" + "="*60)
    print("✅ Manual scrape complete!")
    print(f"Total events in database: {after_count}")
    print("="*60)
    
    db.close()
    return True

if __name__ == "__main__":
    manual_scrape()
