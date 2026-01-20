"""
Complete workflow test - scrape, transform, save, verify
"""
from scraper_manager import ScraperManager
from database import SessionLocal, Event, init_db
from data_transformer import DataTransformer
import json
import os

def test_complete_workflow():
    """Test the complete workflow"""
    
    print("="*60)
    print("COMPLETE WORKFLOW TEST")
    print("="*60)
    print("This will:")
    print("1. Run scrapers (5 events per source)")
    print("2. Transform data to standard format")
    print("3. Save to database")
    print("4. Verify format")
    print("5. Check combined JSON")
    print("="*60)
    
    input("\nPress Enter to start (this may take a few minutes)...")
    
    # Initialize
    print("\n[1/6] Initializing database...")
    init_db()
    db = SessionLocal()
    print("      ✓ Database initialized")
    
    # Run scrapers
    print("\n[2/6] Running scrapers (5 events per source)...")
    print("      This will take a few minutes...")
    
    manager = ScraperManager(db)
    results = manager.run_all_scrapers(
        headless=False,  # So you can see what's happening
        max_events_per_source=5
    )
    
    print(f"\n      ✓ Scraping complete!")
    print(f"      Total events: {results['total_events']}")
    print(f"      By source: {results['by_source']}")
    
    # Check database
    print("\n[3/6] Checking database...")
    count = db.query(Event).count()
    print(f"      Events in database: {count}")
    
    if count == 0:
        print("      ✗ No events in database!")
        return False
    
    # Get sample events
    print("\n[4/6] Verifying database format...")
    events = db.query(Event).limit(3).all()
    
    for i, event in enumerate(events, 1):
        print(f"\n      Event {i}:")
        print(f"        Title: {event.title[:50]}")
        print(f"        Date: {event.date}")
        print(f"        Category: {event.category}")
        print(f"        Source: {event.source}")
        print(f"        Price: {event.price}")
        print(f"        Images: {len(event.images) if event.images else 0}")
        print(f"        Region: {event.content.get('region') if event.content else 'N/A'}")
    
    # Verify format
    print("\n[5/6] Format verification...")
    first = events[0]
    
    checks = {
        'Title exists': bool(first.title),
        'Date formatted (YYYY-MM-DD)': first.date and len(first.date) == 10 and '-' in first.date,
        'Category set': bool(first.category),
        'Source set': bool(first.source),
        'URL exists': bool(first.url),
        'Images is list': isinstance(first.images, list),
        'Content has region': first.content and 'region' in first.content,
    }
    
    all_passed = True
    for check, passed in checks.items():
        status = "✓" if passed else "✗"
        print(f"      {status} {check}")
        if not passed:
            all_passed = False
    
    # Check combined JSON
    print("\n[6/6] Checking combined JSON file...")
    json_path = results.get('combined_json_path')
    
    if json_path and os.path.exists(json_path):
        with open(json_path, 'r', encoding='utf-8') as f:
            combined_events = json.load(f)
        
        print(f"      ✓ Combined JSON exists")
        print(f"      Events in JSON: {len(combined_events)}")
        
        if combined_events:
            sample = combined_events[0]
            print(f"\n      Sample event from JSON:")
            print(f"        ID: {sample.get('id')}")
            print(f"        Title: {sample.get('title', '')[:50]}")
            print(f"        Date: {sample.get('date')}")
            print(f"        Region: {sample.get('region')}")
            print(f"        Category: {sample.get('category')}")
            print(f"        Category Color: {sample.get('categoryColor')}")
            print(f"        Price: {sample.get('price')}")
            print(f"        Source: {sample.get('source')}")
            
            # Verify all required fields
            required_fields = [
                'id', 'title', 'description', 'date', 'region',
                'category', 'categoryColor', 'location', 'venue',
                'url', 'eventUrl', 'image', 'imageUrl', 'price',
                'maxCapacity', 'source'
            ]
            
            print(f"\n      Required fields check:")
            fields_ok = True
            for field in required_fields:
                present = field in sample
                status = "✓" if present else "✗"
                if not present:
                    print(f"        {status} {field}")
                    fields_ok = False
            
            if fields_ok:
                print(f"        ✓ All required fields present")
            
            all_passed = all_passed and fields_ok
    else:
        print(f"      ✗ Combined JSON not found")
        all_passed = False
    
    # Final summary
    print("\n" + "="*60)
    print("TEST RESULTS")
    print("="*60)
    print(f"Events scraped: {results['total_events']}")
    print(f"Events in database: {count}")
    print(f"Combined JSON: {'✓ Created' if json_path else '✗ Not found'}")
    print(f"Format validation: {'✅ PASSED' if all_passed else '❌ FAILED'}")
    print("="*60)
    
    if all_passed:
        print("\n🎉 Complete workflow test PASSED!")
        print("\nYour system is working correctly:")
        print("  ✓ Scrapers run successfully")
        print("  ✓ Data is transformed to standard format")
        print("  ✓ Data is saved to database correctly")
        print("  ✓ Combined JSON file is created")
        print("  ✓ All required fields are present")
        print("\n✅ Ready for deployment!")
    else:
        print("\n⚠ Some checks failed. Review output above.")
    
    db.close()
    return all_passed

if __name__ == "__main__":
    test_complete_workflow()
