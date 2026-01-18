"""
Scraper for Greek Ministry of Culture events using the On Demand section
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

class CultureMapScraper(BaseScraper):
    def __init__(self, headless=False):
        super().__init__(headless)
        self.base_url = "https://allofgreeceone.culture.gov.gr/en/"
        self.scraped_urls = set()
    
    def scrape_all_events(self, max_events=968):
        """
        Scrape all 968 events from the Ministry of Culture site
        """
        self.setup_driver()
        all_events = []
        
        try:
            print(f"Navigating to {self.base_url}...")
            self.driver.get(self.base_url)
            time.sleep(4)
            
            # Click on "On Demand" menu
            print("Clicking 'On Demand' menu...")
            try:
                on_demand = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.LINK_TEXT, "On Demand"))
                )
                on_demand.click()
                time.sleep(4)
                print("✓ On Demand page loaded")
            except Exception as e:
                print(f"Could not click On Demand, trying direct URL...")
                self.driver.get(self.base_url + "on-demand/")
                time.sleep(4)
            
            # Now we should be on the events page
            print("\nCollecting event links from the page...")
            
            # Scroll and load all events
            event_links = []
            last_count = 0
            no_change_count = 0
            scroll_count = 0
            max_no_change = 5
            
            while len(event_links) < max_events and no_change_count < max_no_change:
                scroll_count += 1
                
                # Scroll down to load more content
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
                
                # Find all event links
                new_links = self.get_event_links()
                
                for link in new_links:
                    if link not in event_links and link not in self.scraped_urls:
                        event_links.append(link)
                
                print(f"  Scroll {scroll_count}: {len(event_links)} events found", end='')
                
                # Check if we found new events
                if len(event_links) == last_count:
                    no_change_count += 1
                    print(f" (no new events, {no_change_count}/{max_no_change})")
                else:
                    no_change_count = 0
                    print(f" (+{len(event_links) - last_count} new)")
                
                last_count = len(event_links)
                
                # Try to find and click "Load More" or similar button
                try:
                    load_buttons = self.driver.find_elements(By.CSS_SELECTOR, 
                        'button, a[class*="load"], [class*="more"], button[class*="show"]')
                    
                    for button in load_buttons:
                        text = button.text.lower()
                        if any(word in text for word in ['load', 'more', 'show', 'view']):
                            if button.is_displayed() and button.is_enabled():
                                print(f"  Clicking button: {button.text}")
                                button.click()
                                time.sleep(2)
                                no_change_count = 0
                                break
                except:
                    pass
            
            print(f"\n{'='*60}")
            print(f"Total event links collected: {len(event_links)}")
            print(f"{'='*60}")
            
            # Limit to max_events
            event_links = event_links[:max_events]
            
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
            print(f"Error during scraping: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            self.close()
        
        return all_events
    
    def get_event_links(self):
        """Get all event links from current page state"""
        links = []
        
        try:
            # Try multiple selectors
            selectors = [
                'a[href*="/on-demand/"]',
                'article a[href]',
                '.event-item a',
                '.card a',
                '[class*="item"] a[href]',
                '[class*="post"] a[href]',
                '[class*="event"] a[href]'
            ]
            
            for selector in selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    
                    for element in elements:
                        href = element.get_attribute('href')
                        
                        if (href and 
                            self.base_url in href and
                            '/on-demand/' in href and
                            href.count('/') > 5 and  # Event pages have more path segments
                            '/category/' not in href and
                            '/tag/' not in href and
                            '/page/' not in href):
                            
                            if href not in links:
                                links.append(href)
                except:
                    continue
        
        except Exception as e:
            print(f"Error getting links: {e}")
        
        return links
    
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
                'header h1',
                'article h1'
            ])
            
            # Extract date/time
            event['date'] = self.find_text_by_selectors([
                '.event-date',
                '.date',
                'time',
                '[class*="date"]',
                '[datetime]'
            ])
            
            # Extract location/venue
            event['location'] = self.find_text_by_selectors([
                '.event-location',
                '.location',
                '.venue',
                '[class*="location"]',
                '[class*="venue"]'
            ])
            
            # Extract description - get first meaningful paragraph
            desc_elements = self.driver.find_elements(By.CSS_SELECTOR, 
                '.entry-content p, article p, .content p, main p')
            
            description = None
            for elem in desc_elements:
                text = elem.text.strip()
                if text and len(text) > 50:  # Get substantial text
                    description = text
                    break
            event['description'] = description
            
            # Extract category
            event['category'] = self.find_text_by_selectors([
                '.category a',
                '[rel="category tag"]',
                '.event-category',
                '[class*="category"]'
            ])
            
            # Extract event type
            event['event_type'] = self.find_text_by_selectors([
                '.event-type',
                '[class*="type"]',
                '.genre'
            ])
            
            # Extract organizer/institution
            event['organizer'] = self.find_text_by_selectors([
                '.organizer',
                '.institution',
                '[class*="organizer"]',
                '[class*="institution"]'
            ])
            
            # Extract price/admission
            event['price'] = self.find_text_by_selectors([
                '.price',
                '.admission',
                '[class*="price"]',
                '[class*="ticket"]',
                '[class*="admission"]'
            ])
            
            # Extract contact/booking info
            event['contact'] = self.find_text_by_selectors([
                '.contact',
                '.booking',
                '[class*="contact"]',
                '[class*="booking"]'
            ])
            
            # Extract images
            try:
                images = []
                img_selectors = [
                    'article img',
                    '.entry-content img',
                    '.content img',
                    'main img',
                    '.featured-image img'
                ]
                
                for selector in img_selectors:
                    img_elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for img in img_elements[:5]:
                        src = img.get_attribute('src')
                        if src and 'logo' not in src.lower() and 'icon' not in src.lower():
                            if src not in images:
                                images.append(src)
                    
                    if images:
                        break
                
                event['images'] = images
            except:
                event['images'] = []
            
            # Extract all metadata
            try:
                meta_elements = self.driver.find_elements(By.CSS_SELECTOR, '.event-meta, [class*="meta"]')
                metadata = []
                for meta in meta_elements:
                    text = meta.text.strip()
                    if text:
                        metadata.append(text)
                event['metadata'] = ' | '.join(metadata) if metadata else None
            except:
                event['metadata'] = None
            
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
                    if text and len(text) > 1:
                        return text
            except:
                continue
        return None
    
    def save_events(self, events, filename='culture_gov_events_complete.json'):
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
    print("Target: 968 events from allofgreeceone.culture.gov.gr")
    print("=" * 60)
    
    max_events = input("\nHow many events to scrape? (default: 968): ").strip()
    max_events = int(max_events) if max_events.isdigit() else 968
    
    scraper = CultureMapScraper(headless=False)
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
            cat = event.get('category') or event.get('event_type', 'Unknown')
            categories[cat] = categories.get(cat, 0) + 1
        
        print(f"\n  Top categories:")
        for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"    - {cat}: {count}")
        
        # Count with images
        with_images = sum(1 for e in events if e.get('images'))
        print(f"\n  Events with images: {with_images}")
        
    else:
        print("\n✗ No events found.")
