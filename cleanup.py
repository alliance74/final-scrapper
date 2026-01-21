"""
Cleanup script to remove unnecessary files
"""
import os
import shutil

# Files to DELETE
files_to_remove = [
    # All markdown documentation
    "ARCHITECTURE.md", "CHECKLIST.md", "DATABASE_CONFIRMED.md", "DATABASE_STATUS.md",
    "DEPLOYMENT.md", "DOCS_INDEX.md", "FINAL_SUMMARY.md", "GET_STARTED.md",
    "NEON_SETUP.md", "PROJECT_SUMMARY.md", "QUICKSTART.md", "RAILWAY_CACHE_FIX.md",
    "RAILWAY_CONFIRMATION.md", "RAILWAY_DEPLOY.md", "RAILWAY_FIX_START_COMMAND.md",
    "RAILWAY_TROUBLESHOOTING.md", "README.md", "README_API.md", "README_SCRAPERS.md",
    "READY_TO_DEPLOY.md", "START_HERE.md", "TEST_RESULTS.md", "TRANSFORMER_GUIDE.md",
    "TROUBLESHOOTING.md", "WORKFLOW.md",
    
    # Test files
    "test_api.py", "test_complete_workflow.py", "test_database_format.py",
    "test_save_existing_data.py", "test_scheduler.py", "test_scheduler_quick.py",
    "test_transformer.py",
    
    # Unused scrapers (old versions)
    "combined_events_scraper.py", "deals_scraper.py", "events_scraper.py",
    "greece_events_scraper.py", "more_events_scraper.py", "more_events_scraper_resumable.py",
    "pigolampides_events_scraper.py", "visitgreece_improved_scraper.py", "visitgreece_scraper.py",
    
    # Unused utility files
    "setup.py", "example_usage.py", "check_db.py", "check_and_create_tables.py",
    "combine_events_for_db.py", "fix_chromedriver.py", "inspect_page.py",
    "manual_scrape_test.py", "migrate_to_neon.py", "setup_neon_database.py",
    "verify_deployment.py", "view_database.py",
    
    # Debug/temp files
    "debug_page.html", "main.py",
    
    # Render deployment (using Railway instead)
    "render.yaml",
    
    # Docker compose (keep Dockerfile for Railway)
    "docker-compose.yml",
]

# Directories to KEEP
essential_dirs = [
    "scraped_data",
    "chromedriver-win64",
    ".git",
    ".github",
    "__pycache__"
]

def cleanup():
    """Remove unnecessary files"""
    removed_count = 0
    kept_count = 0
    
    print("=" * 60)
    print("CLEANING UP UNNECESSARY FILES")
    print("=" * 60)
    
    for filename in files_to_remove:
        filepath = os.path.join(".", filename)
        if os.path.exists(filepath):
            try:
                os.remove(filepath)
                print(f"✓ Removed: {filename}")
                removed_count += 1
            except Exception as e:
                print(f"✗ Error removing {filename}: {e}")
        else:
            kept_count += 1
    
    print("\n" + "=" * 60)
    print(f"✓ Cleanup complete!")
    print(f"  Removed: {removed_count} files")
    print(f"  Already gone: {kept_count} files")
    print("=" * 60)
    
    print("\n" + "=" * 60)
    print("ESSENTIAL FILES REMAINING:")
    print("=" * 60)
    
    essential_files = [
        "api.py",
        "database.py",
        "scraper_manager.py",
        "data_transformer.py",
        "scheduler.py",
        "config.py",
        "scraper_base.py",
        "culture_final_scraper.py",
        "visitgreece_detailed_scraper.py",
        "pigolampides_scraper.py",
        "more_events_scraper_optimized.py",
        "start.py",
        "run_api.py",
        "run_scrapers.py",
        "requirements.txt",
        ".env",
        ".env.example",
        "Dockerfile",
        "railway.toml",
        "railway-config.json",
        ".gitignore",
        ".dockerignore"
    ]
    
    for filename in essential_files:
        if os.path.exists(filename):
            print(f"  ✓ {filename}")
        else:
            print(f"  ? {filename} (missing)")
    
    print("=" * 60)

if __name__ == "__main__":
    cleanup()
