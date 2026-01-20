"""
Setup Neon database and populate with existing data
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base, Event
from data_transformer import DataTransformer
import json
import os

def setup_neon():
    """Setup Neon database with data"""
    
    print("="*60)
    print("SETUP NEON DATABASE")
    print("="*60)
    
    # Get Neon connection string
    print("\nYour Neon connection string should look like:")
    print("postgresql://user:password@ep-xxx.region.aws.neon.tech/dbname?sslmode=require")
    print()
    
    neon_url = input("Enter your Neon DATABASE_URL: ").strip()
    
    if not neon_url:
        print("❌ No database URL provided!")
        return False
    
    print("\n[1/4] Connecting to Neon PostgreSQL...")
    try:
        engine = create_engine(neon_url)
        print("      ✓ Connected successfully")
    except Exception as e:
        print(f"      ❌ Connection failed: {e}")
        return False
    
    print("\n[2/4] Creating tables...")
    try:
        Base.metadata.create_all(engine)
        print("      ✓ Tables created (events, deals)")
    except Exception as e:
        print(f"      ❌ Failed to create tables: {e}")
        return False
    
    print("\n[3/4] Loading existing JSON data...")
    
    # Load existing JSON files
    events_by_source = {}
    
    json_files = {
        'more_events': 'scraped_data/more_events_optimized.json',
        'pigolampides': 'scraped_data/pigolampides_events.json',
        'visitgreece': 'scraped_data/visitgreece_all_events.json',
        'culture_gov': 'scraped_data/culture_gov_final_events.json'
    }
    
    for source, filepath in json_files.items():
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    events_by_source[source] = data[:10]  # First 10 from each
                    print(f"      ✓ Loaded {len(events_by_source[source])} events from {source}")
            except Exception as e:
                print(f"      ⚠ Error loading {source}: {e}")
                events_by_source[source] = []
        else:
            print(f"      ⚠ File not found: {filepath}")
            events_by_source[source] = []
    
    total_loaded = sum(len(events) for events in events_by_source.values())
    print(f"\n      Total events loaded: {total_loaded}")
    
    if total_loaded == 0:
        print("\n      ❌ No events found in JSON files!")
        return False
    
    # Transform data
    print("\n      Transforming data...")
    transformer = DataTransformer()
    standardized = transformer.transform_all_events(events_by_source)
    print(f"      ✓ Transformed {len(standardized)} events")
    
    print("\n[4/4] Saving to Neon database...")
    Session = sessionmaker(bind=engine)
    db = Session()
    
    saved = 0
    
    for event_data in standardized:
        try:
            # Check if exists
            url = event_data.get('url') or event_data.get('eventUrl')
            if url:
                existing = db.query(Event).filter(Event.url == url).first()
                if existing:
                    continue
            
            # Create event
            event = Event(
                title=event_data.get('title', 'Untitled'),
                description=event_data.get('description'),
                date=event_data.get('date'),
                location=event_data.get('location') or event_data.get('venue'),
                category=event_data.get('category'),
                price=str(event_data.get('price', 0)),
                url=url,
                source=event_data.get('source', 'Unknown'),
                images=[event_data.get('image')] if event_data.get('image') else [],
                contact=None,
                content={'region': event_data.get('region'), 'venue': event_data.get('venue')},
                full_text=None
            )
            
            db.add(event)
            db.commit()
            saved += 1
            print(f"      ✓ Saved: {event.title[:50]}")
            
        except Exception as e:
            print(f"      ❌ Error: {e}")
            db.rollback()
            continue
    
    # Verify
    total = db.query(Event).count()
    
    print("\n" + "="*60)
    print("SETUP COMPLETE")
    print("="*60)
    print(f"Events saved: {saved}")
    print(f"Total in database: {total}")
    print("="*60)
    
    if saved > 0:
        print("\n✅ Neon database is ready!")
        print("\nNext steps:")
        print("1. Update .env file:")
        print(f"   DATABASE_URL={neon_url}")
        print("2. Restart your API")
        print("3. Test: python check_db.py")
    else:
        print("\n⚠ No new events saved")
    
    db.close()
    return saved > 0

if __name__ == "__main__":
    setup_neon()
