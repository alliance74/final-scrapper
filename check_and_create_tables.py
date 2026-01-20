"""
Check database connection and create tables if needed
"""
from database import init_db, SessionLocal, Event, Deal, engine
from sqlalchemy import inspect
import os

def check_database():
    """Check database connection and tables"""
    
    print("="*60)
    print("Database Check")
    print("="*60)
    
    # Check DATABASE_URL
    database_url = os.getenv('DATABASE_URL', 'sqlite:///./events_deals.db')
    print(f"\nDatabase URL: {database_url[:50]}...")
    
    # Check if tables exist
    print("\n[1/3] Checking existing tables...")
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()
    
    print(f"      Existing tables: {existing_tables}")
    
    if not existing_tables:
        print("      ⚠ No tables found!")
    else:
        print(f"      ✓ Found {len(existing_tables)} tables")
        
        # Show table details
        for table in existing_tables:
            columns = inspector.get_columns(table)
            print(f"\n      Table: {table}")
            print(f"      Columns: {len(columns)}")
            for col in columns[:5]:  # Show first 5 columns
                print(f"        - {col['name']}: {col['type']}")
    
    # Create tables if needed
    print("\n[2/3] Creating/updating tables...")
    try:
        init_db()
        print("      ✓ Tables created/updated")
    except Exception as e:
        print(f"      ✗ Error: {e}")
        return False
    
    # Verify tables were created
    print("\n[3/3] Verifying tables...")
    inspector = inspect(engine)
    tables_after = inspector.get_table_names()
    
    print(f"      Tables now: {tables_after}")
    
    expected_tables = ['events', 'deals']
    missing = [t for t in expected_tables if t not in tables_after]
    
    if missing:
        print(f"      ✗ Missing tables: {missing}")
        return False
    else:
        print(f"      ✓ All required tables exist")
    
    # Check if we can query
    print("\n[4/4] Testing database connection...")
    try:
        db = SessionLocal()
        count = db.query(Event).count()
        print(f"      ✓ Connection successful")
        print(f"      Events in database: {count}")
        db.close()
    except Exception as e:
        print(f"      ✗ Connection error: {e}")
        return False
    
    print("\n" + "="*60)
    print("✅ Database check complete!")
    print("="*60)
    
    return True

if __name__ == "__main__":
    success = check_database()
    
    if success:
        print("\n✓ Database is ready to use")
        print("\nNext steps:")
        print("1. Run: python test_save_existing_data.py")
        print("2. Or run: python manual_scrape_test.py")
        print("3. Check: python check_db.py")
    else:
        print("\n✗ Database setup failed")
        print("Check the error messages above")
