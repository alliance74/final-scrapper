"""
Final working scraper for Greek Ministry of Culture
Properly extracts data from event pages
"""

from scraper_base import BaseScraper
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import os
import time
import config

class CultureFinalScraper(BaseScraper):
    def __init__(self, headless=False):
        super().__init__(headless)
        self.base_url = "https://allofgreeceone.culture.gov.gr"
        self.scraped_urls = set()
    
    def scrape_all_events(self, max_events=968):
        """Scrape all events"""
        self.setup_driver()
        all_events = []
        event_links = set()
        
        try:
            # Go to On Demand page
            url = f"{self.base_url}/en/on-demand/"
            print(f"Navigating to {url}...")
            self.driver.get(url)
            time.sleep(5)
            
            # Scroll and click "Read more" to load all events
            print("\nLoading all events...")
            clicks = 0
            for i in range(50):  # Try up to 50 times
                # Scroll down
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
                
                # Count current links before clicking
                current_links = len(self.driver.find_elements(By.CSS_SELECTOR, 'a[href*="/on-demand/"]'))
                
                # Try to click "Read more" button
                try:
                    # Try multiple selectors for the button
                    button_found = False
                    
                    for selector in [
                        "//button[contains(text(), 'Read more')]",
                        "//a[contains(text(), 'Read more')]",
                        "//button[contains(@class, 'load')]",
                        "//button[contains(@class, 'more')]",
                        "//*[contains(text(), 'Read more')]"
                    ]:
                        try:
                            read_more = self.driver.find_element(By.XPATH, selector)
                            
                            if read_more.is_displayed() and read_more.is_enabled():
                                print(f"  Click {clicks + 1}: Found button, clicking...")
                                
                                # Try to click
                                try:
                                    read_more.click()
                                except:
                                    # Try JavaScript click
                                    self.driver.execute_script("arguments[0].click();", read_more)
                                
                                clicks += 1
                                button_found = True
                                time.sleep(3)
                                
                                # Check if new links appeared
                                new_links = len(self.driver.find_elements(By.CSS_SELECTOR, 'a[href*="/on-demand/"]'))
                                print(f"    Links: {current_links} -> {new_links}")
                                
                                break
                        except:
                            continue
                    
                    if not button_found:
                        print(f"  No more 'Read more' button found after {clicks} clicks")
                        break
                        
                except Exception as e:
                    print(f"  Error clicking button: {e}")
                    break
            
            print(f"\nTotal clicks: {clicks}")
            
            # Wait a bit more for final content to load
            time.sleep(3)
            
            # Now collect all event links
            print("\nCollecting event links...")
            
            # Try multiple ways to find links
            event_links_found = set()
            
            # Method 1: Find all links with /on-demand/ in href
            links_method1 = self.driver.find_elements(By.CSS_SELECTOR, 'a[href*="/on-demand/"]')
            print(f"  Method 1 (CSS selector): {len(links_method1)} links")
            
            for link in links_method1:
                href = link.get_attribute('href')
                # Event pages have format: .../en/on-demand/event-name
                # Main page is: .../en/on-demand/
                if (href and 
                    href != f"{self.base_url}/en/on-demand/" and
                    href != f"{self.base_url}/on-demand/" and
                    not href.endswith('/on-demand/')):
                    event_links_found.add(href)
            
            # Method 2: Get ALL links and filter
            all_links = self.driver.find_elements(By.TAG_NAME, 'a')
            print(f"  Method 2 (all links): {len(all_links)} total links on page")
            
            for link in all_links:
                href = link.get_attribute('href')
                
                if (href and 
                    self.base_url in href and
                    '/on-demand/' in href and
                    href != f"{self.base_url}/en/on-demand/" and
                    href != f"{self.base_url}/on-demand/" and
                    not href.endswith('/on-demand/')):
                    event_links_found.add(href)
            
            event_links = list(event_links_found)
            print(f"\nTotal unique event links: {len(event_links)}")
            
            # If still no links, save page for debugging
            if len(event_links) == 0:
                print("\n⚠ No links found! Saving page HTML for debugging...")
                with open('debug_page.html', 'w', encoding='utf-8') as f:
                    f.write(self.driver.page_source)
                print("Saved to: debug_page.html")
                
                # Print some sample links for debugging
                print("\nSample of ALL links on page:")
                for i, link in enumerate(all_links[:20]):
                    href = link.get_attribute('href')
                    text = link.text.strip()[:40]
                    print(f"  {i+1}. {href} | {text}")
                
                return []
            
            # Limit to max_events
            event_links = list(event_links)[:max_events]
            
            # Scrape each event
            print(f"\nScraping {len(event_links)} events...\n")
            
            for idx, link in enumerate(event_links):
                if link in self.scraped_urls:
                    continue
                
                try:
                    print(f"[{idx + 1}/{len(event_links)}] {link.split('/')[-1][:50]}...")
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
    
    def scrape_event(self, url):
        """Scrape a single event page"""
        try:
            self.driver.get(url)
            
            # Wait for page to load
            time.sleep(4)
            
            event = {'url': url}
            
            # Get the entire page text first
            page_text = self.driver.find_element(By.TAG_NAME, 'body').text
            
            # Extract title - it's usually the first h1
            try:
                h1_elements = self.driver.find_elements(By.TAG_NAME, 'h1')
                for h1 in h1_elements:
                    text = h1.text.strip()
                    if text and len(text) > 3:
                        event['title'] = text
                        break
            except:
                pass
            
            # If no title found, try other methods
            if not event.get('title'):
                # Try to get from page title
                page_title = self.driver.title
                if page_title and '|' in page_title:
                    event['title'] = page_title.split('|')[0].strip()
                else:
                    event['title'] = page_title
            
            # Extract all visible text elements
            try:
                # Get all text from divs and paragraphs
                text_elements = self.driver.find_elements(By.CSS_SELECTOR, 
                    'p, div, span, h2, h3, h4')
                
                all_text = []
                for elem in text_elements:
                    text = elem.text.strip()
                    if text and len(text) > 10 and text not in all_text:
                        all_text.append(text)
                
                event['content'] = all_text[:20]  # First 20 text blocks
            except:
                event['content'] = []
            
            # Try to extract date patterns from text
            import re
            date_pattern = r'\d{1,2}[./]\d{1,2}[./]\d{2,4}'
            dates_found = re.findall(date_pattern, page_text)
            event['date'] = dates_found[0] if dates_found else None
            
            # Extract images
            try:
                images = []
                img_elements = self.driver.find_elements(By.TAG_NAME, 'img')
                
                for img in img_elements[:10]:
                    src = img.get_attribute('src')
                    if src and 'logo' not in src.lower() and 'icon' not in src.lower():
                        images.append(src)
                
                event['images'] = images
            except:
                event['images'] = []
            
            # Store full page text for reference
            event['full_text'] = page_text[:3000]  # First 3000 chars
            
            return event
            
        except Exception as e:
            print(f"    Error scraping {url}: {e}")
            return None
    
    def save_events(self, events, filename='culture_gov_final_events.json'):
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
    print("Greek Ministry of Culture - Final Scraper")
    print("=" * 60)
    
    max_events = input("\nHow many events to scrape? (default: 968): ").strip()
    max_events = int(max_events) if max_events.isdigit() else 968
    
    scraper = CultureFinalScraper(headless=False)
    events = scraper.scrape_all_events(max_events=max_events)
    
    if events:
        filepath = scraper.save_events(events)
        print(f"\n✓ Successfully scraped {len(events)} events!")
        
        # Show sample
        if events:
            print(f"\nSample event:")
            print(json.dumps(events[0], indent=2, ensure_ascii=False)[:500])
    else:
        print("\n✗ No events scraped")
