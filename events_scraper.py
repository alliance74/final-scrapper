from scraper_base import BaseScraper
from selenium.webdriver.common.by import By
import json
import os
import config

class EventsScraper(BaseScraper):
    def __init__(self, headless=config.HEADLESS_MODE):
        super().__init__(headless)
        
    def scrape_events(self, url, selectors):
        """
        Scrape events from a website
        
        Args:
            url: Website URL to scrape
            selectors: Dictionary with CSS selectors for event elements
                Example: {
                    'container': '.event-card',
                    'title': '.event-title',
                    'date': '.event-date',
                    'location': '.event-location',
                    'price': '.event-price'
                }
        """
        self.setup_driver()
        events = []
        
        try:
            self.driver.get(url)
            self.scroll_to_bottom()
            
            # Wait for event containers to load
            event_elements = self.wait_for_elements(By.CSS_SELECTOR, selectors['container'])
            
            for element in event_elements:
                event = {}
                
                for key, selector in selectors.items():
                    if key == 'container':
                        continue
                    
                    try:
                        event[key] = element.find_element(By.CSS_SELECTOR, selector).text
                    except:
                        event[key] = None
                
                events.append(event)
            
            print(f"Scraped {len(events)} events")
            
        except Exception as e:
            print(f"Error scraping events: {e}")
        
        finally:
            self.close()
        
        return events
    
    def save_events(self, events, filename='events.json'):
        """Save events to JSON file"""
        os.makedirs(config.OUTPUT_DIR, exist_ok=True)
        filepath = os.path.join(config.OUTPUT_DIR, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(events, f, indent=2, ensure_ascii=False)
        
        print(f"Events saved to {filepath}")
