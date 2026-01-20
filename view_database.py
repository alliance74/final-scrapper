"""
Comprehensive database viewer
Shows all data in a clear format
"""
from database import SessionLocal, Event
import json
from datetime import datetime

def view_database():
    """View all database contents"""
    
    db = SessionLocal()
    
    print("="*80)
    print("DATABASE VIEWER")
    print("="*80)
    print(f"Database: events_deals.db")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    # Get total count
    total = db.query(Event).count()
    print(f"\nTotal Events: {total}")
    
    if total == 0:
        print("\n❌ Database is empty!")
        print("\nTo populate database, run:")
        print("  python test_save_existing_data.py")
        db.close()
        return
    
    # Get events by source
    print("\n" + "-"*80)
    print("EVENTS BY SOURCE")
    print("-"*80)
    
    sources = db.query(Event.source).distinct().all()
    for (source,) in sources:
        count = db.query(Event).filter(Event.source == source).count()
        print(f"  {source}: {count} events")
    
    # Get events by category
    print("\n" + "-"*80)
    print("EVENTS BY CATEGORY")
    print("-"*80)
    
    categories = db.query(Event.category).distinct().all()
    for (category,) in categories:
        if category:
            count = db.query(Event).filter(Event.category == category).count()
            print(f"  {category}: {count} events")
    
    # Show all events
    print("\n" + "-"*80)
    print("ALL EVENTS")
    print("-"*80)
    
    events = db.query(Event).order_by(Event.id).all()
    
    for i, event in enumerate(events, 1):
        print(f"\n[{i}] ID: {event.id}")
        print(f"    Title: {event.title[:70]}")
        print(f"    Date: {event.date or 'Not set'}")
        print(f"    Category: {event.category or 'Not set'}")
        print(f"    Source: {event.source}")
        print(f"    Location: {event.location[:50] if event.location else 'Not set'}")
        print(f"    Price: {event.price}")
        print(f"    Images: {len(event.images) if event.images else 0}")
        print(f"    Region: {event.content.get('region') if event.content else 'Not set'}")
        print(f"    URL: {event.url[:60]}...")
        print(f"    Created: {event.created_at}")
    
    # Show detailed view of first 3
    print("\n" + "="*80)
    print("DETAILED VIEW (First 3 Events)")
    print("="*80)
    
    for i, event in enumerate(events[:3], 1):
        print(f"\n{'='*80}")
        print(f"EVENT {i} - FULL DETAILS")
        print(f"{'='*80}")
        
        event_dict = {
            'id': event.id,
            'title': event.title,
            'description': event.description,
            'date': event.date,
            'location': event.location,
            'category': event.category,
            'price': event.price,
            'url': event.url,
            'source': event.source,
            'images': event.images,
            'contact': event.contact,
            'content': event.content,
            'full_text': event.full_text[:200] if event.full_text else None,
            'created_at': str(event.created_at),
            'updated_at': str(event.updated_at)
        }
        
        print(json.dumps(event_dict, indent=2, ensure_ascii=False))
    
    # Summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print(f"✓ Total events in database: {total}")
    print(f"✓ Sources: {len(sources)}")
    print(f"✓ Categories: {len([c for c in categories if c[0]])}")
    print(f"✓ Database file: events_deals.db")
    print(f"✓ Database size: {get_db_size()} KB")
    print("="*80)
    
    db.close()

def get_db_size():
    """Get database file size"""
    import os
    try:
        size = os.path.getsize('events_deals.db')
        return round(size / 1024, 2)
    except:
        return 0

if __name__ == "__main__":
    view_database()
