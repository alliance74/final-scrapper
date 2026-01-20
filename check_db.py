"""Quick script to check database contents"""
from database import SessionLocal, Event
import json

db = SessionLocal()

count = db.query(Event).count()
print(f"Events in database: {count}")

if count > 0:
    print("\nSample events:")
    events = db.query(Event).limit(3).all()
    
    for i, event in enumerate(events, 1):
        print(f"\n[{i}] {event.title[:60]}")
        print(f"    Date: {event.date}")
        print(f"    Category: {event.category}")
        print(f"    Source: {event.source}")
        print(f"    URL: {event.url[:60]}...")
        
    # Show full format of first event
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
        'created_at': str(first.created_at)
    }
    
    print(json.dumps(event_dict, indent=2, ensure_ascii=False))
else:
    print("\nNo events yet. Background scraping may still be running.")
    print("Check process output or wait a few minutes.")

db.close()
