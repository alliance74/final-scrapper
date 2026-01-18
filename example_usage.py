"""
Example usage of the scrapers with real-world scenarios
Customize the URLs and selectors based on your target websites
"""

from events_scraper import EventsScraper
from deals_scraper import DealsScraper

def example_1_scrape_eventbrite():
    """Example: Scraping events (adjust selectors for your target site)"""
    scraper = EventsScraper(headless=False)
    
    url = "https://www.eventbrite.com/d/online/all-events/"
    
    # These selectors are examples - inspect your target site to get the correct ones
    selectors = {
        'container': '[data-testid="search-result-card"]',
        'title': 'h2',
        'date': '[data-testid="event-date"]',
        'location': '[data-testid="event-location"]',
        'price': '[data-testid="event-price"]'
    }
    
    events = scraper.scrape_events(url, selectors)
    scraper.save_events(events, 'eventbrite_events.json')
    
    print(f"\nScraped {len(events)} events")
    if events:
        print("\nFirst event:")
        print(events[0])

def example_2_scrape_deals():
    """Example: Scraping deals (adjust selectors for your target site)"""
    scraper = DealsScraper(headless=False)
    
    url = "https://www.example-deals-site.com/deals"
    
    # These selectors are examples - inspect your target site to get the correct ones
    selectors = {
        'container': '.deal-item',
        'title': '.deal-title',
        'price': '.current-price',
        'discount': '.discount-percentage',
        'description': '.deal-description'
    }
    
    deals = scraper.scrape_deals(url, selectors)
    scraper.save_deals(deals, 'deals_output.json')
    
    print(f"\nScraped {len(deals)} deals")
    if deals:
        print("\nFirst deal:")
        print(deals[0])

def custom_scraper_example():
    """Create a custom scraper for your specific needs"""
    from scraper_base import BaseScraper
    from selenium.webdriver.common.by import By
    
    scraper = BaseScraper(headless=False)
    scraper.setup_driver()
    
    try:
        # Navigate to your target page
        scraper.driver.get("https://your-target-site.com")
        
        # Wait for content to load
        scraper.scroll_to_bottom()
        
        # Extract data using custom logic
        items = scraper.wait_for_elements(By.CSS_SELECTOR, '.your-item-class')
        
        data = []
        for item in items:
            # Extract specific fields
            title = item.find_element(By.CSS_SELECTOR, '.title').text
            data.append({'title': title})
        
        print(f"Scraped {len(data)} items")
        
    finally:
        scraper.close()

if __name__ == "__main__":
    print("Choose an example to run:")
    print("1. Scrape Events")
    print("2. Scrape Deals")
    print("3. Custom Scraper")
    
    choice = input("\nEnter choice (1-3): ")
    
    if choice == "1":
        example_1_scrape_eventbrite()
    elif choice == "2":
        example_2_scrape_deals()
    elif choice == "3":
        custom_scraper_example()
    else:
        print("Invalid choice")
