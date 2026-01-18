"""
Resumable scraper for More.com events
Saves progress incrementally and can resume from where it stopped
URL: https://www.more.com/gr-en/tickets/
"""

from scraper_base import BaseScraper
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import os
import time
import config

class MoreEventsScraperResumable(BaseScraper):
    def __init__(self, headless=False):
        super().__init__(headless)
        self.base_url = "https://www.more.com"
        self.events_url = "https://www.more.com/gr-en/tickets/"
        self.scraped_urls = set()
        self.progress_file = os.path.join(config.OUTPUT_DIR, 'more_events_progress.json')
        self.output_file = os.path.join(config.OUTPUT_DIR, 'more_events.json')
    
    def load_progress(self):
        """Load previously scraped events and URLs"""
        events = []
        scraped_urls = set()
        
        if os.path.exists(self.output_file):
            try:
                with open(self.output_file, 'r', encoding='utf-8') as f:
                    events = json.load(f)
                    scraped_urls = {event['url'] for event in events}
                print(f"✓ Loaded {len(events)} previously scraped events")
            except:
                print("⚠ Could not load previous progress")
        
        return events, scraped_urls
    
    def save_event(self, event, all_events):
        """Save a single event immediately"""
        all_events.append(event)
        
        # Save to file immediately
        try:
            os.makedirs(config.OUTPUT_DIR, exist_ok=True)
            with open(self.output_file, 'w', encoding='utf-8') as f:
                json.dump(all_events, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"    ⚠ Error saving: {e}")
    
    def save_links(self, links):
        """Save collected links for resume capability"""
        try:
            os.makedirs(config.OUTPUT_DIR, exist_ok=True)
            with open(self.progress_file, 'w', encoding='utf-8') as f:
                json.dump(list(links), f, indent=2)
        except:
            pass
    
    def load_links(self):
        """Load previously collected links"""
        if os.path.exists(self.progress_file):
            try:
                with open(self.progress_file, 'r', encoding='utf-8') as f:
                    links = json.load(f)
                    print(f"✓ Loaded {len(links)} event links from previous session")
                    return set(links)
            except:
                pass
        return set()
    
    def scrape_all_events(self, max_events=5000, resume=True):
        """
        Scrape all events with resume capability
        """
        # Load previous progress
        all_events, scraped_urls = self.load_progress() if resume else ([], set())
        self.scraped_urls = scraped_urls
        
        # Try to load previously collected links
        event_links = self.load_links() if resume else set()
        
        # If no links loaded, collect them
        if not event_links:
            self.setup_driver()
            
            try:
                print(f"Navigating to {self.events_url}...")
                self.driver.get(self.events_url)
                time.sleep(5)
                
                # Scroll and load all events
                print("\nCollecting event links...")
                last_count = 0
                no_change = 0
                
                for scroll in range(100):
                    # Scroll down
                    self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(2)
                    
                    # Collect event links
                    current_links = self.find_event_links()
                    event_links.update(current_links)
                    
                    if len(event_links) == last_count:
                        no_change += 1
                        if no_change >= 5:
                            print(f"  No new events after {no_change} scrolls")
                            break
                    else:
                        no_change = 0
                        if scroll % 5 == 0:
                            print(f"  Scroll {scroll + 1}: {len(event_links)} events found")
                    
                    last_count = len(event_links)
                    
                    if len(event_links) >= max_events:
                        break
                    
                    # Try to click "Load More"
                    if scroll % 10 == 0:
                        try:
                            load_buttons = self.driver.find_elements(By.CSS_SELECTOR, 
                                'button, a[class*="load"], [class*="more"]')
                            
                            for button in load_buttons:
                                if button.is_displayed() and button.is_enabled():
                                    text = button.text.lower()
                                    if any(word in text for word in ['load', 'more', 'next']):
                                        try:
                                            button.click()
                                        except:
                                            self.driver.execute_script("arguments[0].click();", button)
                                        time.sleep(3)
                                        break
                        except:
                            pass
                
                # Save collected links
                self.save_links(event_links)
                
                print(f"\n{'='*60}")
                print(f"Total event links collected: {len(event_links)}")
                print(f"{'='*60}")
                
                self.close()
                
            except Exception as e:
                print(f"Error collecting links: {e}")
                self.close()
                return all_events
        
        # Filter out already scraped events
        remaining_links = [link for link in event_links if link not in scraped_urls]
        remaining_links = remaining_links[:max_events - len(all_events)]
        
        print(f"\n{'='*60}")
        print(f"Already scraped: {len(all_events)} events")
        print(f"Remaining to scrape: {len(remaining_links)} events")
        print(f"{'='*60}")
        
        if not remaining_links:
            print("\n✓ All events already scraped!")
            return all_events
        
        # Scrape remaining events
        self.setup_driver()
        
        try:
            print(f"\nScraping events (saving after each one)...\n")
            
            for idx, link in enumerate(remaining_links):
                try:
                    current_total = len(all_events) + 1
                    print(f"[{current_total}/{len(event_links)}] {link.split('/')[-2][:50]}...")
                    
                    event = self.scrape_event(link)
                    
                    if event and event.get('title'):
                        self.save_event(event, all_events)
                        self.scraped_urls.add(link)
                        print(f"  ✓ {event['title'][:60]} (SAVED)")
                    else:
                        print(f"  ✗ No data extracted")
                    
                    time.sleep(0.5)
                    
                except KeyboardInterrupt:
                    print(f"\n\n⚠ Interrupted by user!")
                    print(f"✓ Progress saved: {len(all_events)} events")
                    print(f"Run the script again to resume from event {len(all_events) + 1}")
                    break
                    
                except Exception as e:
                    print(f"  ✗ Error: {e}")
                    continue
            
            print(f"\n{'='*60}")
            print(f"Successfully scraped {len(all_events)} total events")
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
            selectors = [
                'a[href*="/tickets/"]',
                'a[href*="/event"]',
                'article a',
                '.event a',
                '[class*="event"] a',
                '[class*="ticket"] a',
                '.card a'
            ]
            
            for selector in selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    
                    for element in elements:
                        href = element.get_attribute('href')
                        
                        if (href and 
                            self.base_url in href and
                            ('/tickets/' in href or '/event' in href) and
                            href != self.events_url and
                            not href.endswith('/tickets/')):
                            links.add(href)
                except:
                    continue
        
        except Exception as e:
            print(f"Error finding links: {e}")
        
        return links
    
    def scrape_event(self, url):
        """Scrape ALL data from a single event"""
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
                text_elements = self.driver.find_elements(By.CSS_SELECTOR, 
                    'p, div, span, h1, h2, h3, h4, h5, h6, li, td, th, a, label, button')
                
                for elem in text_elements:
                    text = elem.text.strip()
                    if text and len(text) > 5 and text not in content:
                        content.append(text)
                
                event['content'] = content
            except:
                event['content'] = []
            
            # Extract date
            event['date'] = self.find_text_by_selectors([
                '.event-date', '.date', 'time', '[class*="date"]', '[datetime]'
            ])
            
            # Extract ALL images
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

if __name__ == "__main__":
    print("More.com Events Scraper (Resumable)")
    print("=" * 60)
    print("Features:")
    print("- Saves progress after each event")
    print("- Can resume if interrupted (Ctrl+C)")
    print("- Run again to continue from where you stopped")
    print("=" * 60)
    
    max_events = input("\nHow many events to scrape? (default: 5000): ").strip()
    max_events = int(max_events) if max_events.isdigit() else 5000
    
    resume = input("Resume from previous session? (Y/n): ").strip().lower()
    resume = resume != 'n'
    
    scraper = MoreEventsScraperResumable(headless=False)
    events = scraper.scrape_all_events(max_events=max_events, resume=resume)
    
    print(f"\n{'='*60}")
    print(f"✓ Final count: {len(events)} events")
    print(f"✓ Saved to: scraped_data/more_events.json")
    print(f"{'='*60}")
