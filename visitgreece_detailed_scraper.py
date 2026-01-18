"""
Advanced scraper for Visit Greece events with detailed information
Clicks into each event to get full details
"""

from scraper_base import BaseScraper
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import os
import time
import config

class VisitGreeceDetailedScraper(BaseScraper):
    def __init__(self, headless=False):
        super().__init__(headless)
        self.base_url = "https://www.visitgreece.gr/events"
    
    def scrape_events_with_details(self, max_events=20):
        """
        Scrape events and click into each for detailed information
        
        Args:
            max_events: Maximum number of events to scrape in detail
        """
        self.setup_driver()
        all_events = []
        
        try:
            print(f"Navigating to {self.base_url}...")
            self.driver.get(self.base_url)
            time.sleep(4)
            
            # Scroll to load content
            print("Loading events...")
            self.scroll_to_bottom(pause_time=2)
            
            # Get all event links
            event_links = self.get_event_links()
            
            if not event_links:
                print("No event links found. Trying alternative approach...")
                return self.scrape_events_simple()
            
            print(f"Found {len(event_links)} event links")
            
            # Limit to max_events
            event_links = event_links[:max_events]
            
            # Visit each event page for details
            for idx, link in enumerate(event_links):
                try:
                    print(f"\nScraping event {idx + 1}/{len(event_links)}: {link}")
                    event_details = self.scrape_event_detail_page(link)
                    
                    if event_details:
                        all_events.append(event_details)
                        print(f"✓ Scraped: {event_details.get('title', 'N/A')[:60]}")
                    
                    time.sleep(1)  # Be polite to the server
                    
                except Exception as e:
                    print(f"✗ Error scraping event {idx + 1}: {e}")
                    continue
            
            print(f"\n{'='*60}")
            print(f"Total events scraped: {len(all_events)}")
            
        except Exception as e:
            print(f"Error during scraping: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            self.close()
        
        return all_events
    
    def get_event_links(self):
        """Extract all event links from the main page"""
        links = []
        
        try:
            # Try to find all links that might be events
            all_links = self.driver.find_elements(By.TAG_NAME, 'a')
            
            for link in all_links:
                href = link.get_attribute('href')
                if href and '/events/' in href and href != self.base_url:
                    if href not in links:
                        links.append(href)
        
        except Exception as e:
            print(f"Error getting event links: {e}")
        
        return links
    
    def scrape_event_detail_page(self, url):
        """Scrape detailed information from an individual event page"""
        try:
            self.driver.get(url)
            time.sleep(2)
            
            event = {'url': url}
            
            # Extract title
            title_selectors = ['h1', '.event-title', '[class*="title"]']
            event['title'] = self.find_text_by_selectors(title_selectors)
            
            # Extract date/time
            date_selectors = ['.event-date', '[class*="date"]', 'time', '.date']
            event['date'] = self.find_text_by_selectors(date_selectors)
            
            # Extract location
            location_selectors = ['.event-location', '[class*="location"]', '.location', '[class*="place"]']
            event['location'] = self.find_text_by_selectors(location_selectors)
            
            # Extract description
            desc_selectors = ['.event-description', '[class*="description"]', '.description', 'article p']
            event['description'] = self.find_text_by_selectors(desc_selectors)
            
            # Extract category
            category_selectors = ['.category', '[class*="category"]', '.tag']
            event['category'] = self.find_text_by_selectors(category_selectors)
            
            # Extract price/cost
            price_selectors = ['.price', '[class*="price"]', '.cost', '[class*="cost"]']
            event['price'] = self.find_text_by_selectors(price_selectors)
            
            # Extract contact info
            contact_selectors = ['.contact', '[class*="contact"]', '.phone', '[class*="phone"]']
            event['contact'] = self.find_text_by_selectors(contact_selectors)
            
            # Extract images
            try:
                images = self.driver.find_elements(By.TAG_NAME, 'img')
                event['images'] = [img.get_attribute('src') for img in images[:3] if img.get_attribute('src')]
            except:
                event['images'] = []
            
            # Get all text content as backup
            try:
                body = self.driver.find_element(By.TAG_NAME, 'body')
                event['full_text'] = body.text[:1000]  # First 1000 chars
            except:
                event['full_text'] = None
            
            return event
            
        except Exception as e:
            print(f"Error scraping detail page {url}: {e}")
            return None
    
    def find_text_by_selectors(self, selectors):
        """Try multiple selectors to find text"""
        for selector in selectors:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                for element in elements:
                    text = element.text.strip()
                    if text:
                        return text
            except:
                continue
        return None
    
    def scrape_events_simple(self):
        """Fallback: Simple scraping without clicking into details"""
        print("Using simple scraping method...")
        events = []
        
        try:
            # Get all visible text elements
            elements = self.driver.find_elements(By.XPATH, "//*[contains(@class, 'event') or contains(@class, 'card') or contains(@class, 'item')]")
            
            for element in elements:
                text = element.text.strip()
                if text and len(text) > 20:
                    events.append({
                        'text': text,
                        'html': element.get_attribute('outerHTML')[:500]
                    })
        
        except Exception as e:
            print(f"Error in simple scraping: {e}")
        
        return events
    
    def save_events(self, events, filename='visitgreece_detailed_events.json'):
        """Save events to JSON file"""
        os.makedirs(config.OUTPUT_DIR, exist_ok=True)
        filepath = os.path.join(config.OUTPUT_DIR, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(events, f, indent=2, ensure_ascii=False)
        
        print(f"\n{'='*60}")
        print(f"Events saved to: {filepath}")
        return filepath

if __name__ == "__main__":
    print("Visit Greece Detailed Events Scraper")
    print("=" * 60)
    print("This scraper will:")
    print("1. Load the events page")
    print("2. Find all event links")
    print("3. Visit each event for detailed information")
    print("=" * 60)
    
    max_events = input("\nHow many events to scrape? (default: 20): ").strip()
    max_events = int(max_events) if max_events.isdigit() else 20
    
    scraper = VisitGreeceDetailedScraper(headless=False)
    events = scraper.scrape_events_with_details(max_events=max_events)
    
    if events:
        filepath = scraper.save_events(events)
        print(f"\n✓ Successfully scraped {len(events)} events!")
        
        if events:
            print("\n" + "="*60)
            print("Sample event:")
            print("="*60)
            print(json.dumps(events[0], indent=2, ensure_ascii=False))
    else:
        print("\n✗ No events found.")
