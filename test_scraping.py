"""
Quick test script to verify scraping and database saving works
Tests one scraper only for speed
"""
import sys
from database import init_db, SessionLocal
from scraper_manager import ScraperManager

def main():
    print("=" * 60)
    print("QUICK SCRAPING TEST")
    print("=" * 60)
    print("Testing: Culture.gov.gr scraper")
    print("Max events: 5")
    print("Headless: True")
    print("=" * 60)
    
    try:
        # Initialize database
        print("\n[1/4] Initializing database...")
        init_db()
        print("✓ Database initialized")
        
        # Create session
        print("\n[2/4] Creating database session...")
        db = SessionLocal()
        print("✓ Session created")
        
        # Test scraping
        print("\n[3/4] Running Culture.gov.gr scraper...")
        print("(This may take 1-2 minutes)\n")
        
        from culture_final_scraper import CultureFinalScraper
        from data_transformer import DataTransformer
        
        # Scrape events
        scraper = CultureFinalScraper(headless=True)
        events = scraper.scrape_all_events(max_events=5)
        print(f"\n✓ Scraped {len(events)} events from Culture.gov.gr")
        
        # Transform data
        print("\n[4/4] Transforming and saving to database...")
        transformer = DataTransformer()
        events_by_source = {'culture_gov': events}
        standardized = transformer.transform_all_events(events_by_source)
        print(f"✓ Transformed {len(standardized)} events")
        
        # Save to database
        manager = ScraperManager(db)
        saved_count = manager.save_standardized_events(standardized)
        print(f"✓ Saved {saved_count} new events to database")
        
        # Save combined JSON
        json_path = transformer.save_combined_json(standardized, 'test_combined_events.json')
        print(f"✓ Combined JSON saved to: {json_path}")
        
        # Show sample event
        if standardized:
            print("\n" + "=" * 60)
            print("SAMPLE EVENT (Standardized Format):")
            print("=" * 60)
            sample = standardized[0]
            print(f"Title: {sample.get('title')}")
            print(f"Date: {sample.get('date')}")
            print(f"Region: {sample.get('region')}")
            print(f"Category: {sample.get('category')}")
            print(f"Source: {sample.get('source')}")
            print(f"URL: {sample.get('url')}")
        
        print("\n" + "=" * 60)
        print("✓ TEST COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print("\nVerification:")
        print(f"  - Scraped: {len(events)} events")
        print(f"  - Transformed: {len(standardized)} events")
        print(f"  - Saved to DB: {saved_count} new events")
        print(f"  - JSON file: {json_path}")
        print("\n✅ Scraping works! Ready for Railway deployment!")
        print("=" * 60)
        
        db.close()
        return 0
        
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
