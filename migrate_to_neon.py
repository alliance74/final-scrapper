"""
Migrate data from local SQLite to Neon PostgreSQL
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Event, Base
import os

def migrate_to_neon():
    """Migrate data from SQLite to Neon PostgreSQL"""
    
    print("="*60)
    print("MIGRATE TO NEON POSTGRESQL")
    print("="*60)
    
    # Get Neon connection string
    neon_url = input("\nEnter your Neon DATABASE_URL: ").strip()
    
    if not neon_url:
        print("❌ No database URL provided!")
        return False
    
    print("\n[1/5] Connecting to local SQLite database...")
    # Local SQLite
    sqlite_engine = create_engine('sqlite:///./events_deals.db')
    SQLiteSession = sessionmaker(bind=sqlite_engine)
    sqlite_db = SQLiteSession()
    
    # Get events from SQLite
    events = sqlite_db.query(Event).all()
    print(f"      ✓ Found {len(events)} events in SQLite")
    
    if len(events) == 0:
        print("      ❌ No events to migrate!")
        sqlite_db.close()
        return False
    
    print("\n[2/5] Connecting to Neon PostgreSQL...")
    try:
        # Neon PostgreSQL
        neon_engine = create_engine(neon_url)
        print("      ✓ Connected to Neon")
    except Exception as e:
        print(f"      ❌ Failed to connect: {e}")
        sqlite_db.close()
        return False
    
    print("\n[3/5] Creating tables in Neon...")
    try:
        Base.metadata.create_all(neon_engine)
        print("      ✓ Tables created")
    except Exception as e:
        print(f"      ❌ Failed to create tables: {e}")
        sqlite_db.close()
        return False
    
    print("\n[4/5] Migrating events...")
    NeonSession = sessionmaker(bind=neon_engine)
    neon_db = NeonSession()
    
    migrated = 0
    skipped = 0
    
    for event in events:
        try:
            # Check if exists
            existing = neon_db.query(Event).filter(Event.url == event.url).first()
            if existing:
                print(f"      ⚠ Skipping duplicate: {event.title[:40]}")
                skipped += 1
                continue
            
            # Create new event
            new_event = Event(
                title=event.title,
                description=event.description,
                date=event.date,
                location=event.location,
                category=event.category,
                price=event.price,
                url=event.url,
                source=event.source,
                images=event.images,
                contact=event.contact,
                content=event.content,
                full_text=event.full_text
            )
            
            neon_db.add(new_event)
            neon_db.commit()
            migrated += 1
            print(f"      ✓ Migrated: {event.title[:50]}")
            
        except Exception as e:
            print(f"      ❌ Error migrating event: {e}")
            neon_db.rollback()
            continue
    
    print("\n[5/5] Verifying migration...")
    total_in_neon = neon_db.query(Event).count()
    print(f"      ✓ Total events in Neon: {total_in_neon}")
    
    # Summary
    print("\n" + "="*60)
    print("MIGRATION COMPLETE")
    print("="*60)
    print(f"Events migrated: {migrated}")
    print(f"Events skipped (duplicates): {skipped}")
    print(f"Total in Neon database: {total_in_neon}")
    print("="*60)
    
    if migrated > 0:
        print("\n✅ Migration successful!")
        print("\nYou can now:")
        print("1. Update your .env file with Neon DATABASE_URL")
        print("2. Restart your API")
        print("3. Deploy to Railway with Neon database")
    else:
        print("\n⚠ No new events migrated (may already exist)")
    
    # Cleanup
    sqlite_db.close()
    neon_db.close()
    
    return migrated > 0

if __name__ == "__main__":
    migrate_to_neon()
