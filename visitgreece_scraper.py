"""
Scraper for Visit Greece events
URL: https://www.visitgreece.gr/events
"""

from scraper_base import BaseScraper
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import os
import time
import config

class VisitGreeceScraper(BaseScraper):
    def __init__(self, headless=False):
        super().__init__(headless)
        self.base_url = "https://www.visitgreece.gr/events"
    
    def scrape_events(self, max_pages=5):
        """
        Scrape events from Visit Greece website
        
        Args:
            max_pages: Maximum number of pages to scrape (default: 5)
        """
        self.setup_driver()
        all_events = []
        
        try:
            print(f"Navigating to {self.base_url}...")
            self.driver.get(self.base_url)
            
            # Wait for page to load
            time.sleep(3)
            
            # Scroll to load more content
            print("Loading dynamic content...")
            self.scroll_to_bottom(pause_time=2)
            
            # Try to find event cards - adjust selectors based on actual site structure
            print("Extracting events...")
            
            # Common possible selectors for event listings
            possible_selectors = [
                '.event-card',
                '.event-item',
                'article',
                '[class*="event"]',
                '.card',
                '.item',
                '[data-event]'
            ]
            
            event_elements = None
            used_selector = None
            
            for selector in possible_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if len(elements) > 0:
                        event_elements = elements
                        used_selector = selector
                        print(f"Found {len(elements)} elements using selector: {selector}")
                        break
                except:
                    continue
            
            if not event_elements:
                print("Could not find events with standard selectors.")
                print("Page source preview (first 500 chars):")
                print(self.driver.page_source[:500])
                return []
            
            # Extract data from each event
            for idx, element in enumerate(event_elements):
                try:
                    event = self.extract_event_details(element)
                    if event:
                        all_events.append(event)
                        print(f"Scraped event {idx + 1}: {event.get('title', 'N/A')[:50]}")
                except Exception as e:
                    print(f"Error extracting event {idx + 1}: {e}")
                    continue
            
            print(f"\nTotal events scraped: {len(all_events)}")
            
        except Exception as e:
            print(f"Error during scraping: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            self.close()
        
        return all_events
    
    def extract_event_details(self, element):
        """Extract details from a single event element"""
        event = {}
        
        # Try multiple possible selectors for each field
        title_selectors = ['h2', 'h3', '.title', '[class*="title"]', 'a']
        date_selectors = ['.date', '[class*="date"]', 'time', '.event-date']
        location_selectors = ['.location', '[class*="location"]', '.place', '[class*="place"]']
        description_selectors = ['.description', 'p', '[class*="description"]']
        link_selectors = ['a']
        image_selectors = ['img']
        
        # Extract title
        event['title'] = self.try_extract(element, title_selectors)
        
        # Extract date
        event['date'] = self.try_extract(element, date_selectors)
        
        # Extract location
        event['location'] = self.try_extract(element, location_selectors)
        
        # Extract description
        event['description'] = self.try_extract(element, description_selectors)
        
        # Extract link
        try:
            link_element = element.find_element(By.CSS_SELECTOR, 'a')
            event['link'] = link_element.get_attribute('href')
        except:
            event['link'] = None
        
        # Extract image
        try:
            img_element = element.find_element(By.CSS_SELECTOR, 'img')
            event['image'] = img_element.get_attribute('src')
        except:
            event['image'] = None
        
        # Get all text as fallback
        event['full_text'] = element.text
        
        return event if event['title'] else None
    
    def try_extract(self, element, selectors):
        """Try multiple selectors to extract text"""
        for selector in selectors:
            try:
                found = element.find_element(By.CSS_SELECTOR, selector)
                text = found.text.strip()
                if text:
                    return text
            except:
                continue
        return None
    
    def save_events(self, events, filename='visitgreece_events.json'):
        """Save events to JSON file"""
        os.makedirs(config.OUTPUT_DIR, exist_ok=True)
        filepath = os.path.join(config.OUTPUT_DIR, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(events, f, indent=2, ensure_ascii=False)
        
        print(f"\nEvents saved to {filepath}")
        return filepath

if __name__ == "__main__":
    print("Visit Greece Events Scraper")
    print("=" * 50)
    
    scraper = VisitGreeceScraper(headless=False)
    events = scraper.scrape_events(max_pages=1)
    
    if events:
        scraper.save_events(events)
        print(f"\nSuccessfully scraped {len(events)} events!")
        print("\nSample event:")
        print(json.dumps(events[0], indent=2, ensure_ascii=False))
    else:
        print("\nNo events found. The website structure may have changed.")
        print("Please inspect the page manually to identify the correct selectors.")
