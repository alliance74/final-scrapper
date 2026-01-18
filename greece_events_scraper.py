"""
Scraper for Visit Greece events
URL: https://www.visitgreece.gr/events/
"""

from events_scraper import EventsScraper
import json

def scrape_greece_events():
    """Scrape events from Visit Greece website"""
    
    scraper = EventsScraper(headless=False)
    
    url = "https://www.visitgreece.gr/events/"
    
    # CSS selectors for Visit Greece events page
    # These will need to be adjusted after inspecting the actual page
    selectors = {
        'container': '.event-item, .event-card, article, .listing-item',
        'title': 'h2, h3, .event-title, .title',
        'date': '.event-date, .date, time',
        'location': '.event-location, .location, .venue',
        'description': '.event-description, .description, p',
        'category': '.event-category, .category',
        'link': 'a'
    }
    
    print(f"Scraping events from: {url}")
    print("This will open Chrome browser to scrape the page...\n")
    
    events = scraper.scrape_events(url, selectors)
    
    if events:
        scraper.save_events(events, 'greece_events.json')
        
        print(f"\n✓ Successfully scraped {len(events)} events")
        print(f"✓ Data saved to: scraped_data/greece_events.json")
        
        # Display first few events
        print("\n--- Sample Events ---")
        for i, event in enumerate(events[:3], 1):
            print(f"\nEvent {i}:")
            for key, value in event.items():
                if value:
                    print(f"  {key}: {value[:100] if len(str(value)) > 100 else value}")
    else:
        print("\n⚠ No events found. The selectors may need adjustment.")
        print("Please inspect the page and update the selectors in this script.")
    
    return events

if __name__ == "__main__":
    scrape_greece_events()
