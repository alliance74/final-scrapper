"""
Fixed scraper for Greek Ministry of Culture events
URL: https://allofgreeceone.culture.gov.gr/en/
"""

from scraper_base import BaseScraper
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import json
import os
import time
import config

class CultureGovFixedScraper(BaseScraper):
    def __init__(self, headless=False):
        super().__init__(headless)
        self.base_url = "https://allofgreeceone.culture.gov.gr/en/"
        self.scraped_urls = set()
    
    def scrape_all_events(self, max_events=200):
        """
        Scrape all events from the site
        """
        self.setup_driver()
        all_events = []
        
        try:
            print(f"Navigating to {self.base_url}...")
            self.driver.get(self.base_url)
            time.sleep(4)
            
            # Click on "On Demand" or "Events" menu
            print("Looking for events menu...")
            
            # Try to find and click the events/on-demand menu
            menu_clicked = False
            menu_selectors = [
                'a[href*="on-demand"]',
                'a:contains("On Demand")',
                'a[href*="events"]',
                '.menu a',
                'nav a'
            ]
            
            for selector in menu_selectors:
                try:
                    menu_items = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for item in menu_items:
                        text = item.text.strip().lower()
                        href = item.get_attribute('href')
                        
                        if 'on demand' in text or 'events' in text or (href and 'on-demand' in href):
                            print(f"Clicking menu: {item.text}")
                            item.click()
                            time.sleep(3)
                            menu_clicked = True
                            break
                    
                    if menu_clicked:
                        break
                except:
                    continue
            
            if not menu_clicked:
                print("Could not find events menu, trying direct URL...")
                self.driver.get(self.base_url + "on-demand/")
                time.sleep(3)
            
            # Now scrape events from the page
            print("\nCollecting event links...")
            event_links = []
            scroll_attempts = 0
            max_scrolls = 20
            
            while scroll_attempts < max_scrolls and len(event_links) < max_events:
                # Scroll to load more content
                last_count = len(event_links)
                
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
                
                # Find all event cards/links
                links = self.find_all_event_links()
                
                for link in links:
                    if link not in event_links and link not in self.scraped_urls:
                        event_links.append(link)
                
                print(f"  Scroll {scroll_attempts + 1}: Found {len(event_links)} total events")
                
                # Check if we got new links
                if len(event_links) == last_count:
                    scroll_attempts += 1
                else:
                    scroll_attempts = 0  # Reset if we found new content
                
                # Try to click "Load More" button if exists
                try:
                    load_more = self.driver.find_element(By.CSS_SELECTOR, 'button[class*="load"], .load-more, button:contains("Load")')
                    if load_more.is_displayed():
                        load_more.click()
                        time.sleep(2)
                        scroll_attempts = 0
                except:
                    pass
            
            print(f"\n{'='*60}")
            print(f"Total event links found: {len(event_links)}")
            print(f"{'='*60}")
            
            # Limit to max_events
            event_links = event_links[:max_events]
            
            # Scrape each event
            for idx, link in enumerate(event_links):
                try:
                    print(f"\n[{idx + 1}/{len(event_links)}] Scraping: {link[:70]}...")
                    event_details = self.scrape_event_detail(link)
                    
                    if event_details:
                        all_events.append(event_details)
                        self.scraped_urls.add(link)
                        print(f"  ✓ {event_details.get('title', 'N/A')[:60]}")
                    
                    time.sleep(0.5)
                    
                except Exception as e:
                    print(f"  ✗ Error: {e}")
                    continue
            
            print(f"\n{'='*60}")
            print(f"Successfully scraped {len(all_events)} events")
            print(f"{'='*60}")
            
        except Exception as e:
            print(f"Error during scraping: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            self.close()
        
        return all_events
    
    def find_all_event_links(self):
        """Find all event links on current page"""
        links = []
        
        try:
            # Try multiple selectors for event cards
            selectors = [
                'article a',
                '.event a',
                '.card a',
                '[class*="event"] a',
                '[class*="item"] a',
                '.post a',
                '[class*="post"] a'
            ]
            
            for selector in selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        href = element.get_attribute('href')
                        
                        # Filter for actual event pages
                        if (href and 
                            self.base_url in href and
                            href != self.base_url and
                            '/news/' not in href and
                            '/category/' not in href and
                            '/tag/' not in href and
                            len(href.split('/')) > 5):  # Event pages have more segments
                            
                            if href not in links:
                                links.append(href)
                except:
                    continue
        
        except Exception as e:
            print(f"Error finding links: {e}")
        
        return links
    
    def scrape_event_detail(self, url):
        """Scrape details from an event page"""
        try:
            self.driver.get(url)
            time.sleep(2)
            
            event = {'url': url}
            
            # Extract title
            event['title'] = self.find_text_by_selectors([
                'h1',
                '.entry-title',
                '.title',
                'header h1',
                'article h1'
            ])
            
            # Extract date
            event['date'] = self.find_text_by_selectors([
                '.date',
                'time',
                '[class*="date"]',
                '.event-date',
                '[datetime]'
            ])
            
            # Extract location/venue
            event['location'] = self.find_text_by_selectors([
                '.location',
                '.venue',
                '[class*="location"]',
                '[class*="venue"]',
                '.place'
            ])
            
            # Extract description
            event['description'] = self.find_text_by_selectors([
                '.entry-content p',
                'article p',
                '.description',
                '.content p',
                'main p'
            ])
            
            # Extract category
            event['category'] = self.find_text_by_selectors([
                '.category',
                '[class*="category"]',
                '.tag',
                '[rel="category"]'
            ])
            
            # Extract event type
            event['event_type'] = self.find_text_by_selectors([
                '.event-type',
                '[class*="type"]',
                '.genre'
            ])
            
            # Extract organizer
            event['organizer'] = self.find_text_by_selectors([
                '.organizer',
                '[class*="organizer"]',
                '.organization'
            ])
            
            # Extract price/admission
            event['price'] = self.find_text_by_selectors([
                '.price',
                '.admission',
                '[class*="price"]',
                '[class*="ticket"]'
            ])
            
            # Extract images
            try:
                images = []
                img_elements = self.driver.find_elements(By.CSS_SELECTOR, 'article img, .content img, main img')
                for img in img_elements[:5]:
                    src = img.get_attribute('src')
                    if src and 'logo' not in src.lower() and 'icon' not in src.lower():
                        images.append(src)
                event['images'] = images
            except:
                event['images'] = []
            
            return event if event['title'] else None
            
        except Exception as e:
            print(f"Error scraping {url}: {e}")
            return None
    
    def find_text_by_selectors(self, selectors):
        """Try multiple selectors to find text"""
        for selector in selectors:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                for element in elements:
                    text = element.text.strip()
                    if text and len(text) > 2:
                        return text
            except:
                continue
        return None
    
    def save_events(self, events, filename='culture_gov_all_events.json'):
        """Save events to JSON file"""
        os.makedirs(config.OUTPUT_DIR, exist_ok=True)
        filepath = os.path.join(config.OUTPUT_DIR, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(events, f, indent=2, ensure_ascii=False)
        
        print(f"\n{'='*60}")
        print(f"✓ Events saved to: {filepath}")
        print(f"{'='*60}")
        return filepath

if __name__ == "__main__":
    print("Greek Ministry of Culture Events Scraper (Fixed)")
    print("=" * 60)
    print("URL: https://allofgreeceone.culture.gov.gr/en/")
    print("=" * 60)
    
    max_events = input("\nHow many events to scrape? (default: 200): ").strip()
    max_events = int(max_events) if max_events.isdigit() else 200
    
    scraper = CultureGovFixedScraper(headless=False)
    events = scraper.scrape_all_events(max_events=max_events)
    
    if events:
        filepath = scraper.save_events(events)
        print(f"\n✓ Successfully scraped {len(events)} events!")
        
        # Show categories
        print(f"\nEvent types found:")
        types = {}
        for event in events:
            etype = event.get('event_type') or event.get('category', 'Unknown')
            types[etype] = types.get(etype, 0) + 1
        
        for etype, count in sorted(types.items(), key=lambda x: x[1], reverse=True):
            print(f"  - {etype}: {count}")
    else:
        print("\n✗ No events found.")
