"""
Interactive map scraper for Greek Ministry of Culture
Clicks on map regions to collect all 968 events
URL: https://allofgreeceone.culture.gov.gr/en/
"""

from scraper_base import BaseScraper
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import json
import os
import time
import config

class CultureInteractiveMapScraper(BaseScraper):
    def __init__(self, headless=False):
        super().__init__(headless)
        self.base_url = "https://allofgreeceone.culture.gov.gr/en/"
        self.scraped_urls = set()
        self.all_event_links = set()
    
    def scrape_all_events_from_map(self, max_events=968):
        """
        Click on each region on the map to collect all events
        """
        self.setup_driver()
        all_events = []
        
        try:
            print(f"Navigating to {self.base_url}...")
            self.driver.get(self.base_url)
            time.sleep(5)
            
            print("\nLooking for interactive map regions...")
            
            # Find all clickable map markers/regions
            map_markers = self.find_map_markers()
            
            if not map_markers:
                print("No map markers found. Trying alternative approach...")
                return self.scrape_from_on_demand_page(max_events)
            
            print(f"Found {len(map_markers)} regions on the map")
            
            # Click on each marker to reveal events
            for idx, marker in enumerate(map_markers):
                try:
                    print(f"\n{'='*60}")
                    print(f"Region {idx + 1}/{len(map_markers)}")
                    print(f"{'='*60}")
                    
                    # Click the marker
                    self.click_marker(marker)
                    time.sleep(2)
                    
                    # Collect event links from this region
                    region_links = self.collect_visible_event_links()
                    new_links = [link for link in region_links if link not in self.all_event_links]
                    
                    self.all_event_links.update(new_links)
                    
                    print(f"  Found {len(new_links)} new events (Total: {len(self.all_event_links)})")
                    
                    # Close any popup/modal if it appeared
                    self.close_popup()
                    
                except Exception as e:
                    print(f"  Error with region {idx + 1}: {e}")
                    continue
            
            print(f"\n{'='*60}")
            print(f"Total unique event links: {len(self.all_event_links)}")
            print(f"{'='*60}")
            
            # Convert set to list and limit
            event_links = list(self.all_event_links)[:max_events]
            
            # Scrape each event
            print(f"\nScraping details from {len(event_links)} events...\n")
            
            for idx, link in enumerate(event_links):
                try:
                    print(f"[{idx + 1}/{len(event_links)}] {link[:70]}...")
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
    
    def find_map_markers(self):
        """Find all clickable markers on the map"""
        markers = []
        
        try:
            # Wait for map to load
            time.sleep(3)
            
            # Try different selectors for map markers
            selectors = [
                'svg circle',  # SVG circles
                'svg path',    # SVG paths
                '[class*="marker"]',
                '[class*="region"]',
                '[class*="dot"]',
                'svg g',       # SVG groups
                'map area',    # Image map areas
            ]
            
            for selector in selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        # Filter for visible, clickable elements
                        clickable = [e for e in elements if e.is_displayed()]
                        if clickable:
                            print(f"  Using selector: {selector} ({len(clickable)} markers)")
                            markers = clickable
                            break
                except:
                    continue
        
        except Exception as e:
            print(f"Error finding markers: {e}")
        
        return markers
    
    def click_marker(self, marker):
        """Click on a map marker"""
        try:
            # Try regular click
            marker.click()
        except:
            try:
                # Try JavaScript click
                self.driver.execute_script("arguments[0].click();", marker)
            except:
                try:
                    # Try ActionChains
                    actions = ActionChains(self.driver)
                    actions.move_to_element(marker).click().perform()
                except:
                    pass
    
    def collect_visible_event_links(self):
        """Collect event links currently visible on page"""
        links = []
        
        try:
            # Look for event links in various containers
            selectors = [
                'a[href*="/on-demand/"]',
                '.event-item a',
                '.modal a',
                '.popup a',
                'article a',
                '[class*="event"] a'
            ]
            
            for selector in selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    
                    for element in elements:
                        href = element.get_attribute('href')
                        
                        if (href and 
                            self.base_url in href and
                            '/on-demand/' in href and
                            href.count('/') > 5):
                            
                            if href not in links:
                                links.append(href)
                except:
                    continue
        
        except Exception as e:
            print(f"Error collecting links: {e}")
        
        return links
    
    def close_popup(self):
        """Close any popup or modal that might be open"""
        try:
            close_selectors = [
                '.close',
                '[class*="close"]',
                'button[aria-label="Close"]',
                '.modal-close',
                '[data-dismiss]'
            ]
            
            for selector in close_selectors:
                try:
                    close_btn = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if close_btn.is_displayed():
                        close_btn.click()
                        time.sleep(0.5)
                        return
                except:
                    continue
            
            # Try pressing ESC key
            from selenium.webdriver.common.keys import Keys
            self.driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)
            
        except:
            pass
    
    def scrape_from_on_demand_page(self, max_events):
        """Fallback: Scrape from On Demand page directly"""
        print("\nUsing fallback method: On Demand page...")
        
        try:
            self.driver.get(self.base_url + "on-demand/")
            time.sleep(4)
            
            # Scroll and collect all event links
            for scroll in range(50):  # Scroll up to 50 times
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(1)
                
                links = self.collect_visible_event_links()
                self.all_event_links.update(links)
                
                if scroll % 5 == 0:
                    print(f"  Scroll {scroll}: {len(self.all_event_links)} events found")
                
                if len(self.all_event_links) >= max_events:
                    break
            
            return list(self.all_event_links)[:max_events]
            
        except Exception as e:
            print(f"Fallback method failed: {e}")
            return []
    
    def scrape_event_detail(self, url):
        """Scrape detailed information from an event page"""
        try:
            self.driver.get(url)
            time.sleep(2)
            
            event = {'url': url}
            
            # Extract title
            event['title'] = self.find_text_by_selectors([
                'h1.entry-title',
                'h1',
                '.title',
                'header h1'
            ])
            
            # Extract date
            event['date'] = self.find_text_by_selectors([
                '.event-date',
                '.date',
                'time',
                '[class*="date"]'
            ])
            
            # Extract location
            event['location'] = self.find_text_by_selectors([
                '.event-location',
                '.location',
                '.venue',
                '[class*="location"]'
            ])
            
            # Extract description
            desc_elements = self.driver.find_elements(By.CSS_SELECTOR, 
                '.entry-content p, article p, .content p')
            
            description = None
            for elem in desc_elements:
                text = elem.text.strip()
                if text and len(text) > 50:
                    description = text
                    break
            event['description'] = description
            
            # Extract category
            event['category'] = self.find_text_by_selectors([
                '.category a',
                '[rel="category tag"]',
                '[class*="category"]'
            ])
            
            # Extract organizer
            event['organizer'] = self.find_text_by_selectors([
                '.organizer',
                '.institution',
                '[class*="organizer"]'
            ])
            
            # Extract price
            event['price'] = self.find_text_by_selectors([
                '.price',
                '.admission',
                '[class*="price"]'
            ])
            
            # Extract images
            try:
                images = []
                img_elements = self.driver.find_elements(By.CSS_SELECTOR, 
                    'article img, .entry-content img, .content img')
                
                for img in img_elements[:5]:
                    src = img.get_attribute('src')
                    if src and 'logo' not in src.lower():
                        images.append(src)
                
                event['images'] = images
            except:
                event['images'] = []
            
            return event if event['title'] else None
            
        except Exception as e:
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
    
    def save_events(self, events, filename='culture_gov_map_events.json'):
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
    print("Greek Ministry of Culture - Interactive Map Scraper")
    print("=" * 60)
    print("This scraper clicks on map regions to collect all 968 events")
    print("=" * 60)
    
    max_events = input("\nHow many events to scrape? (default: 968): ").strip()
    max_events = int(max_events) if max_events.isdigit() else 968
    
    scraper = CultureInteractiveMapScraper(headless=False)
    events = scraper.scrape_all_events_from_map(max_events=max_events)
    
    if events:
        filepath = scraper.save_events(events)
        print(f"\n✓ Successfully scraped {len(events)} events!")
        
        # Statistics
        print(f"\nStatistics:")
        categories = {}
        for event in events:
            cat = event.get('category', 'Unknown')
            categories[cat] = categories.get(cat, 0) + 1
        
        print(f"  Top categories:")
        for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"    - {cat}: {count}")
    else:
        print("\n✗ No events found.")
