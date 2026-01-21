"""
Quick test to verify all components are working
"""
import sys

def test_imports():
    """Test that all modules can be imported"""
    print("=" * 60)
    print("TESTING MODULE IMPORTS")
    print("=" * 60)
    
    modules = [
        'api',
        'database',
        'scraper_manager',
        'data_transformer',
        'scheduler',
        'config',
        'scraper_base',
        'culture_final_scraper',
        'visitgreece_detailed_scraper',
        'pigolampides_scraper',
        'more_events_scraper_optimized'
    ]
    
    failed = []
    
    for module in modules:
        try:
            __import__(module)
            print(f"  ✓ {module}")
        except Exception as e:
            print(f"  ✗ {module}: {e}")
            failed.append(module)
    
    if failed:
        print(f"\n✗ Failed to import: {', '.join(failed)}")
        return False
    else:
        print(f"\n✓ All {len(modules)} modules imported successfully!")
        return True

def test_database():
    """Test database initialization"""
    print("\n" + "=" * 60)
    print("TESTING DATABASE")
    print("=" * 60)
    
    try:
        from database import init_db, SessionLocal
        init_db()
        print("  ✓ Database initialized")
        
        # Test session creation
        db = SessionLocal()
        db.close()
        print("  ✓ Database session created")
        
        return True
    except Exception as e:
        print(f"  ✗ Database error: {e}")
        return False

def test_api_creation():
    """Test FastAPI app creation"""
    print("\n" + "=" * 60)
    print("TESTING API")
    print("=" * 60)
    
    try:
        from api import app
        print(f"  ✓ FastAPI app created")
        print(f"  ✓ App title: {app.title}")
        print(f"  ✓ App version: {app.version}")
        
        # Count routes
        routes = [r for r in app.routes if hasattr(r, 'methods')]
        print(f"  ✓ Total endpoints: {len(routes)}")
        
        return True
    except Exception as e:
        print(f"  ✗ API error: {e}")
        return False

def test_transformer():
    """Test data transformer"""
    print("\n" + "=" * 60)
    print("TESTING DATA TRANSFORMER")
    print("=" * 60)
    
    try:
        from data_transformer import DataTransformer
        
        transformer = DataTransformer()
        
        # Test with sample event
        sample_event = {
            'title': 'Test Event',
            'description': 'Test description',
            'date': '2026-02-15',
            'location': 'Athens',
            'url': 'https://example.com/event1'
        }
        
        transformed = transformer.transform_event(sample_event, 'test_source')
        
        if transformed and transformed.get('title') == 'Test Event':
            print("  ✓ Data transformer working")
            print(f"  ✓ Detected region: {transformed.get('region')}")
            print(f"  ✓ Detected category: {transformed.get('category')}")
            return True
        else:
            print("  ✗ Transformation failed")
            return False
            
    except Exception as e:
        print(f"  ✗ Transformer error: {e}")
        return False

def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("🧪 RUNNING COMPONENT TESTS")
    print("=" * 60)
    
    results = {
        'Imports': test_imports(),
        'Database': test_database(),
        'API': test_api_creation(),
        'Transformer': test_transformer()
    }
    
    print("\n" + "=" * 60)
    print("TEST RESULTS")
    print("=" * 60)
    
    for name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"  {status}: {name}")
    
    all_passed = all(results.values())
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✓ ALL TESTS PASSED - READY FOR DEPLOYMENT!")
    else:
        print("✗ SOME TESTS FAILED - FIX ERRORS BEFORE DEPLOYING")
    print("=" * 60)
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
