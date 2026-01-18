"""
Scraper for Greek Ministry of Culture events
URL: https://allofgreeceone.culture.gov.gr/en/
"""

from scraper_base import BaseScraper
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import os
import time
import config

class CultureGovScraper(BaseScraper):
    def __init__(self, headless=False):
        super().__init__(headless)
        self.base_url = "https://allofgreeceone.culture.gov.gr/en/"
        self.events_url = "https://allofgreeceone.culture.gov.gr/en/events"
        self.scraped_urls = set()
    
    def scrape_events(self, max_events=200):
        """
        Scrape events from Greek Ministry of Culture website
        
        Args:
            max_events: Maximum number of events to scrape
        """
        self.setup_driver()
        all_events = []
        
        try:
            # Navigate directly to events page
            print(f"Navigating to events page...")
            self.driver.get(self.events_url)
            time.sleep(4)
            
            # Collect event links from all pages
            event_links = []
            page = 1
            
            while len(event_links) < max_events:
                print(f"\n{'='*60}")
                print(f"Loading page {page}...")
                print(f"{'='*60}")
                
                # Scroll to load content
                self.scroll_to_bottom(pause_time=2)
                
                # Get event links from current page
                page_links = self.find_event_links()
                
                if not page_links:
                    print(f"No more events found on page {page}")
                    break
                
                new_links = [link for link in page_links if link not in event_links]
                event_links.extend(new_links)
                
                print(f"Found {len(new_links)} new events (Total: {len(event_links)})")
                
                # Try to find and click "Next" or "Load More" button
                if not self.load_next_page():
                    print("No more pages available")
                    break
                
                page += 1
                time.sleep(2)
            
            print(f"\n{'='*60}")
            print(f"Total event links collected: {len(event_links)}")
            print(f"{'='*60}")
            
            # Limit to max_events
            event_links = event_links[:max_events]
            
            # Scrape each event
            for idx, link in enumerate(event_links):
                if link in self.scraped_urls:
                    continue
                
                try:
                    print(f"\n[{idx + 1}/{len(event_links)}] Scraping: {link[:80]}...")
                    event_details = self.scrape_event_detail(link)
                    
                    if event_details:
                        all_events.append(event_details)
                        self.scraped_urls.add(link)
                        print(f"  ✓ {event_details.get('title', 'N/A')[:60]}")
                    
                    time.sleep(1)  # Be polite to the server
                    
                except Exception as e:
                    print(f"  ✗ Error: {e}")
                    continue
            
            print(f"\n{'='*60}")
            print(f"Total events scraped: {len(all_events)}")
            print(f"{'='*60}")
            
        except Exception as e:
            print(f"Error during scraping: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            self.close()
        
        return all_events
    
    def find_event_links(self):
        """Find event links on the current page"""
        links = []
        
        try:
            # Try to find event cards or links
            possible_selectors = [
                'a[href*="/events/"]',
                'a[href*="/event/"]',
                '.event-card a',
                '.event-item a',
                'article a',
                '.card a',
                '[class*="event"] a',
                '.item a',
                '[data-event] a'
            ]
            
            for selector in possible_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        for element in elements:
                            href = element.get_attribute('href')
                            # Filter for actual event detail pages
                            if (href and 
                                href not in links and 
                                self.base_url in href and
                                '/events/' in href and
                                href != self.events_url and
                                href != self.events_url + '/'):
                                links.append(href)
                        
                        if links:
                            print(f"  Using selector: {selector}")
                            break
                except:
                    continue
        
        except Exception as e:
            print(f"Error finding event links: {e}")
        
        return links
    
    def load_next_page(self):
        """Try to load the next page of events"""
        try:
            # Try to find and click pagination buttons
            next_selectors = [
                'a[rel="next"]',
                '.next',
                '.pagination-next',
                'button:contains("Next")',
                'a:contains("Next")',
                '[class*="next"]',
                '.load-more',
                'button[class*="load"]'
            ]
            
            for selector in next_selectors:
                try:
                    next_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if next_button.is_displayed() and next_button.is_enabled():
                        next_button.click()
                        time.sleep(2)
                        return True
                except:
                    continue
            
            # Try scrolling to trigger infinite scroll
            last_height = self.driver.execute_script("return document.body.scrollHeight")
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            
            return new_height > last_height
            
        except Exception as e:
            return False
    
    def find_events_alternative(self):
        """Alternative method to find events"""
        links = []
        
        try:
            # Get all links on the page
            all_links = self.driver.find_elements(By.TAG_NAME, 'a')
            
            for link in all_links:
                href = link.get_attribute('href')
                text = link.text.strip()
                
                # Filter for event-related links
                if href and (
                    'event' in href.lower() or
                    'exhibition' in href.lower() or
                    'festival' in href.lower() or
                    'concert' in href.lower() or
                    (text and len(text) > 10)  # Links with substantial text
                ):
                    if href not in links and self.base_url in href:
                        links.append(href)
        
        except Exception as e:
            print(f"Error in alternative search: {e}")
        
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
                '.title',
                '[class*="title"]',
                'header h1',
                'header h2'
            ])
            
            # Extract date
            event['date'] = self.find_text_by_selectors([
                '.date',
                '[class*="date"]',
                'time',
                '.event-date',
                '[class*="time"]'
            ])
            
            # Extract location
            event['location'] = self.find_text_by_selectors([
                '.location',
                '[class*="location"]',
                '.venue',
                '[class*="venue"]',
                '.place',
                '[class*="place"]'
            ])
            
            # Extract description
            event['description'] = self.find_text_by_selectors([
                '.description',
                '[class*="description"]',
                'article p',
                '.content p',
                'main p',
                'p'
            ])
            
            # Extract category/type
            event['category'] = self.find_text_by_selectors([
                '.category',
                '[class*="category"]',
                '.type',
                '[class*="type"]',
                '.tag'
            ])
            
            # Extract organizer
            event['organizer'] = self.find_text_by_selectors([
                '.organizer',
                '[class*="organizer"]',
                '.organization',
                '[class*="organization"]'
            ])
            
            # Extract contact
            event['contact'] = self.find_text_by_selectors([
                '.contact',
                '[class*="contact"]',
                '.phone',
                '.email'
            ])
            
            # Extract price
            event['price'] = self.find_text_by_selectors([
                '.price',
                '[class*="price"]',
                '.cost',
                '[class*="admission"]'
            ])
            
            # Extract images
            try:
                images = []
                img_elements = self.driver.find_elements(By.TAG_NAME, 'img')
                for img in img_elements[:5]:
                    src = img.get_attribute('src')
                    if src and 'logo' not in src.lower():
                        images.append(src)
                event['images'] = images
            except:
                event['images'] = []
            
            # Get full text as backup
            try:
                body = self.driver.find_element(By.TAG_NAME, 'body')
                event['full_text'] = body.text[:1500]
            except:
                event['full_text'] = None
            
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
    
    def save_page_structure(self):
        """Save page HTML for debugging"""
        try:
            html = self.driver.page_source
            with open('page_structure.html', 'w', encoding='utf-8') as f:
                f.write(html)
            print("Page structure saved to page_structure.html")
        except Exception as e:
            print(f"Could not save page structure: {e}")
    
    def save_events(self, events, filename='culture_gov_events.json'):
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
    print("Greek Ministry of Culture Events Scraper")
    print("=" * 60)
    print("URL: https://allofgreeceone.culture.gov.gr/en/")
    print("=" * 60)
    
    max_events = input("\nHow many events to scrape? (default: 200): ").strip()
    max_events = int(max_events) if max_events.isdigit() else 200
    
    scraper = CultureGovScraper(headless=False)
    events = scraper.scrape_events(max_events=max_events)
    
    if events:
        filepath = scraper.save_events(events)
        print(f"\n✓ Successfully scraped {len(events)} events!")
        
        # Show sample event
        if events:
            print(f"\nSample event:")
            print("="*60)
            print(json.dumps(events[0], indent=2, ensure_ascii=False))
    else:
        print("\n✗ No events found.")
        print("The page structure has been saved for analysis.")
