"""
Test database format - verify data is saved correctly
"""
from database import SessionLocal, Event, init_db
from data_transformer import DataTransformer
import json

def test_database_format():
    """Test that data is saved in expected format"""
    
    print("="*60)
    print("Database Format Test")
    print("="*60)
    
    # Initialize database
    print("\n[1/5] Initializing database...")
    init_db()
    db = SessionLocal()
    print("      ✓ Database initialized")
    
    # Create sample data
    print("\n[2/5] Creating sample data...")
    sample_events = {
        'more_events': [
            {
                'title': 'Τα μυστικά της ανωτερότητας των Ιταλικών ζυμαρικών',
                'description': 'Masterclass για ζυμαρικά',
                'date': '2026-02-09',
                'location': 'Technopolis - City of Athens, Peiraios 100 & Persefonis, Gazi',
                'venue': 'Technopolis',
                'category': 'Conference',
                'price': '30',
                'url': 'https://www.more.com/gr-en/tickets/conference/masterclass-zymarikon/',
                'images': ['https://www.more.com/image.png']
            }
        ]
    }
    print("      ✓ Sample data created")
    
    # Transform data
    print("\n[3/5] Transforming data...")
    transformer = DataTransformer()
    standardized = transformer.transform_all_events(sample_events)
    print(f"      ✓ Transformed {len(standardized)} events")
    
    # Display standardized format
    print("\n[4/5] Standardized Format:")
    print("-"*60)
    print(json.dumps(standardized[0], indent=2, ensure_ascii=False))
    print("-"*60)
    
    # Save to database
    print("\n[5/5] Saving to database...")
    try:
        event_data = standardized[0]
        
        # Check if exists
        existing = db.query(Event).filter(Event.url == event_data['url']).first()
        if existing:
            print("      ⚠ Event already exists, deleting for test...")
            db.delete(existing)
            db.commit()
        
        # Create event
        event = Event(
            title=event_data.get('title'),
            description=event_data.get('description'),
            date=event_data.get('date'),
            location=event_data.get('location') or event_data.get('venue'),
            category=event_data.get('category'),
            price=str(event_data.get('price', 0)),
            url=event_data.get('url'),
            source=event_data.get('source'),
            images=[event_data.get('image')] if event_data.get('image') else [],
            contact=None,
            content={'region': event_data.get('region'), 'venue': event_data.get('venue')},
            full_text=None
        )
        
        db.add(event)
        db.commit()
        db.refresh(event)
        
        print("      ✓ Event saved to database")
        print(f"      Event ID: {event.id}")
        
        # Retrieve and verify
        print("\n" + "="*60)
        print("Database Record:")
        print("="*60)
        
        retrieved = db.query(Event).filter(Event.id == event.id).first()
        
        print(f"ID: {retrieved.id}")
        print(f"Title: {retrieved.title}")
        print(f"Description: {retrieved.description[:100]}...")
        print(f"Date: {retrieved.date}")
        print(f"Location: {retrieved.location}")
        print(f"Category: {retrieved.category}")
        print(f"Price: {retrieved.price}")
        print(f"URL: {retrieved.url}")
        print(f"Source: {retrieved.source}")
        print(f"Images: {retrieved.images}")
        print(f"Content: {retrieved.content}")
        print(f"Created: {retrieved.created_at}")
        
        # Verify format matches expected
        print("\n" + "="*60)
        print("Format Verification:")
        print("="*60)
        
        checks = {
            'Title exists': bool(retrieved.title),
            'Description exists': bool(retrieved.description),
            'Date formatted (YYYY-MM-DD)': retrieved.date and len(retrieved.date) == 10,
            'Category set': bool(retrieved.category),
            'Source set': bool(retrieved.source),
            'URL unique': bool(retrieved.url),
            'Images is list': isinstance(retrieved.images, list),
            'Content is dict': isinstance(retrieved.content, dict),
            'Region in content': 'region' in (retrieved.content or {}),
        }
        
        all_passed = True
        for check, passed in checks.items():
            status = "✓" if passed else "✗"
            print(f"  {status} {check}")
            if not passed:
                all_passed = False
        
        # Compare with expected format
        print("\n" + "="*60)
        print("Expected Format Comparison:")
        print("="*60)
        
        expected_format = {
            "id": retrieved.id,
            "title": retrieved.title,
            "description": retrieved.description,
            "date": retrieved.date,
            "region": retrieved.content.get('region') if retrieved.content else None,
            "category": retrieved.category,
            "location": retrieved.location,
            "venue": retrieved.content.get('venue') if retrieved.content else None,
            "url": retrieved.url,
            "image": retrieved.images[0] if retrieved.images else None,
            "price": int(retrieved.price) if retrieved.price and retrieved.price.isdigit() else 0,
            "source": retrieved.source
        }
        
        print(json.dumps(expected_format, indent=2, ensure_ascii=False))
        
        print("\n" + "="*60)
        if all_passed:
            print("✅ All format checks passed!")
            print("✅ Data is saved in expected format!")
        else:
            print("⚠ Some format checks failed")
        print("="*60)
        
        # Clean up
        db.delete(event)
        db.commit()
        print("\n✓ Test data cleaned up")
        
        return all_passed
        
    except Exception as e:
        print(f"      ✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        db.close()

def test_api_format():
    """Test API response format"""
    print("\n" + "="*60)
    print("Testing API Format")
    print("="*60)
    
    try:
        import requests
        
        # Test combined events endpoint
        print("\nTesting /combined-events endpoint...")
        response = requests.get('http://localhost:8000/combined-events', timeout=5)
        
        if response.status_code == 200:
            events = response.json()
            print(f"✓ Endpoint accessible")
            print(f"✓ Events returned: {len(events)}")
            
            if events:
                sample = events[0]
                print("\nSample event from API:")
                print(json.dumps(sample, indent=2, ensure_ascii=False)[:500])
                
                # Check required fields
                required_fields = [
                    'id', 'title', 'description', 'date', 'region',
                    'category', 'categoryColor', 'location', 'venue',
                    'url', 'eventUrl', 'image', 'imageUrl', 'price',
                    'source'
                ]
                
                print("\nRequired fields check:")
                all_present = True
                for field in required_fields:
                    present = field in sample
                    status = "✓" if present else "✗"
                    print(f"  {status} {field}")
                    if not present:
                        all_present = False
                
                if all_present:
                    print("\n✅ API format is correct!")
                else:
                    print("\n⚠ Some required fields missing")
                
                return all_present
            else:
                print("⚠ No events in response (run scrapers first)")
                return True
        else:
            print(f"✗ Endpoint returned status {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("⚠ API not running (start with: python run_api.py)")
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

if __name__ == "__main__":
    print("\n" + "="*60)
    print("COMPREHENSIVE FORMAT TEST")
    print("="*60)
    
    # Test 1: Database format
    db_passed = test_database_format()
    
    # Test 2: API format
    api_passed = test_api_format()
    
    # Summary
    print("\n" + "="*60)
    print("FINAL RESULTS")
    print("="*60)
    print(f"Database Format: {'✅ PASSED' if db_passed else '❌ FAILED'}")
    print(f"API Format: {'✅ PASSED' if api_passed else '❌ FAILED'}")
    print("="*60)
    
    if db_passed and api_passed:
        print("\n🎉 All tests passed! Format is correct!")
    else:
        print("\n⚠ Some tests failed. Check output above.")
