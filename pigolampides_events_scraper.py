"""
Scraper for Pigolampides events
URL: https://pigolampides.gr/events/
"""

from scraper_base import BaseScraper
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import os
import time
import config

class PigolampidesEventsScraper(BaseScraper):
    def __init__(self, headless=False):
        super().__init__(headless)
        self.base_url = "https://pigolampides.gr"
        self.events_url = "https://pigolampides.gr/events/"
        self.scraped_urls = set()
    
    def scrape_all_events(self, max_events=200):
        """
        Scrape all events from Pigolampides
        """
        self.setup_driver()
        all_events = []
        event_links = set()
        
        try:
            print(f"Navigating to {self.events_url}...")
            self.driver.get(self.events_url)
            time.sleep(4)
            
            # Scroll and load all events
            print("\nLoading all events...")
            last_count = 0
            no_change = 0
            
            for scroll in range(50):
                # Scroll down
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
                
                # Collect event links
                current_links = self.find_event_links()
                event_links.update(current_links)
                
                if len(event_links) == last_count:
                    no_change += 1
                    if no_change >= 3:
                        print(f"  No new events after {no_change} scrolls")
                        break
                else:
                    no_change = 0
                    print(f"  Scroll {scroll + 1}: {len(event_links)} events found")
                
                last_count = len(event_links)
                
                if len(event_links) >= max_events:
                    break
                
                # Try to click "Load More" or pagination
                try:
                    load_buttons = self.driver.find_elements(By.CSS_SELECTOR, 
                        'button, a[class*="load"], [class*="more"], .pagination a, [class*="next"]')
                    
                    for button in load_buttons:
                        if button.is_displayed() and button.is_enabled():
                            text = button.text.lower()
                            if any(word in text for word in ['load', 'more', 'next', 'περισσότερα']):
                                print(f"  Clicking: {button.text}")
                                button.click()
                                time.sleep(2)
                                break
                except:
                    pass
            
            print(f"\n{'='*60}")
            print(f"Total event links collected: {len(event_links)}")
            print(f"{'='*60}")
            
            # Limit to max_events
            event_links = list(event_links)[:max_events]
            
            # Scrape each event
            print(f"\nScraping {len(event_links)} events...\n")
            
            for idx, link in enumerate(event_links):
                if link in self.scraped_urls:
                    continue
                
                try:
                    print(f"[{idx + 1}/{len(event_links)}] {link.split('/')[-2][:50]}...")
                    event = self.scrape_event(link)
                    
                    if event and event.get('title'):
                        all_events.append(event)
                        self.scraped_urls.add(link)
                        print(f"  ✓ {event['title'][:60]}")
                    else:
                        print(f"  ✗ No data extracted")
                    
                    time.sleep(0.5)
                    
                except Exception as e:
                    print(f"  ✗ Error: {e}")
                    continue
            
            print(f"\n{'='*60}")
            print(f"Successfully scraped {len(all_events)} events")
            print(f"{'='*60}")
            
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            self.close()
        
        return all_events
    
    def find_event_links(self):
        """Find all event links on current page"""
        links = set()
        
        try:
            # Try multiple selectors for events
            selectors = [
                'article a',
                '.event a',
                '.event-item a',
                '[class*="event"] a',
                'a[href*="/events/"]',
                '.card a',
                '[class*="card"] a'
            ]
            
            for selector in selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    
                    for element in elements:
                        href = element.get_attribute('href')
                        
                        # Filter for actual event pages
                        if (href and 
                            self.base_url in href and
                            '/events/' in href and
                            href != self.events_url and
                            not href.endswith('/events/')):
                            links.add(href)
                except:
                    continue
        
        except Exception as e:
            print(f"Error finding links: {e}")
        
        return links
    
    def scrape_event(self, url):
        """Scrape ALL data from a single event in simple format"""
        try:
            self.driver.get(url)
            time.sleep(3)
            
            event = {'url': url}
            
            # Extract title
            try:
                h1 = self.driver.find_element(By.TAG_NAME, 'h1')
                event['title'] = h1.text.strip()
            except:
                event['title'] = self.driver.title
            
            # Extract ALL text content as array
            content = []
            try:
                # Get all text-containing elements
                text_elements = self.driver.find_elements(By.CSS_SELECTOR, 
                    'p, div, span, h1, h2, h3, h4, h5, h6, li, td, th, a, label, button')
                
                for elem in text_elements:
                    text = elem.text.strip()
                    # Only add if text is substantial and not already in content
                    if text and len(text) > 5 and text not in content:
                        content.append(text)
                
                event['content'] = content
            except:
                event['content'] = []
            
            # Extract date - try to find it in the content
            event['date'] = self.find_text_by_selectors([
                '.event-date',
                '.date',
                'time',
                '[class*="date"]',
                '[datetime]',
                '.event-time',
                '[class*="time"]'
            ])
            
            # Extract ALL images (just URLs)
            images = []
            try:
                img_elements = self.driver.find_elements(By.TAG_NAME, 'img')
                
                for img in img_elements:
                    src = img.get_attribute('src')
                    if src:
                        images.append(src)
                
                event['images'] = images
            except:
                event['images'] = []
            
            # Extract FULL page text
            try:
                body = self.driver.find_element(By.TAG_NAME, 'body')
                event['full_text'] = body.text
            except:
                event['full_text'] = None
            
            return event
            
        except Exception as e:
            print(f"    Error scraping {url}: {e}")
            return None
    
    def find_text_by_selectors(self, selectors):
        """Try multiple selectors to find text"""
        for selector in selectors:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                for element in elements:
                    text = element.text.strip()
                    if text and len(text) > 1:
                        return text
            except:
                continue
        return None
    
    def save_events(self, events, filename='pigolampides_events.json'):
        """Save events to JSON"""
        os.makedirs(config.OUTPUT_DIR, exist_ok=True)
        filepath = os.path.join(config.OUTPUT_DIR, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(events, f, indent=2, ensure_ascii=False)
        
        print(f"\n{'='*60}")
        print(f"✓ Events saved to: {filepath}")
        print(f"{'='*60}")
        return filepath

if __name__ == "__main__":
    print("Pigolampides Events Scraper")
    print("=" * 60)
    print("URL: https://pigolampides.gr/events/")
    print("=" * 60)
    
    max_events = input("\nHow many events to scrape? (default: 200): ").strip()
    max_events = int(max_events) if max_events.isdigit() else 200
    
    scraper = PigolampidesEventsScraper(headless=False)
    events = scraper.scrape_all_events(max_events=max_events)
    
    if events:
        filepath = scraper.save_events(events)
        print(f"\n✓ Successfully scraped {len(events)} events!")
        
        # Show statistics
        print(f"\nStatistics:")
        print(f"  Total events: {len(events)}")
        
        # Count by category
        categories = {}
        for event in events:
            cat = event.get('category', 'Unknown')
            categories[cat] = categories.get(cat, 0) + 1
        
        if categories:
            print(f"\n  Top categories:")
            for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True)[:5]:
                print(f"    - {cat}: {count}")
        
        # Count with images
        with_images = sum(1 for e in events if e.get('images'))
        print(f"\n  Events with images: {with_images}")
        
    else:
        print("\n✗ No events scraped")
