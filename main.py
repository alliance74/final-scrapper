from events_scraper import EventsScraper
from deals_scraper import DealsScraper

def scrape_events_example():
    """Example: Scrape events from a website"""
    scraper = EventsScraper(headless=False)
    
    # Replace with your target URL and selectors
    url = "https://example.com/events"
    selectors = {
        'container': '.event-item',
        'title': '.event-title',
        'date': '.event-date',
        'location': '.event-location',
        'price': '.event-price'
    }
    
    events = scraper.scrape_events(url, selectors)
    scraper.save_events(events)
    
    return events

def scrape_deals_example():
    """Example: Scrape deals from a website"""
    scraper = DealsScraper(headless=False)
    
    # Replace with your target URL and selectors
    url = "https://example.com/deals"
    selectors = {
        'container': '.deal-card',
        'title': '.deal-title',
        'price': '.price',
        'discount': '.discount',
        'description': '.description'
    }
    
    deals = scraper.scrape_deals(url, selectors)
    scraper.save_deals(deals)
    
    return deals

if __name__ == "__main__":
    print("Dynamic Web Scraper")
    print("1. Scrape Events")
    print("2. Scrape Deals")
    
    choice = input("Enter your choice (1 or 2): ")
    
    if choice == "1":
        scrape_events_example()
    elif choice == "2":
        scrape_deals_example()
    else:
        print("Invalid choice")
