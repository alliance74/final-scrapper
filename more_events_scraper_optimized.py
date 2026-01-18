"""
Optimized resumable scraper for More.com events
Extracts only essential data: title, brief description, 2-3 images, date, location, price
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

class MoreEventsScraperOptimized(BaseScraper):
    def __init__(self, headless=False):
        super().__init__(headless)
        self.base_url = "https://www.more.com"
        self.events_url = "https://www.more.com/gr-en/tickets/"
        self.scraped_urls = set()
        self.progress_file = os.path.join(config.OUTPUT_DIR, 'more_events_progress.json')
        self.output_file = os.path.join(config.OUTPUT_DIR, 'more_events_optimized.json')
    
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
        """Save collected links"""
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
        """Scrape all events with resume capability"""
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
                
                print("\nCollecting event links...")
                last_count = 0
                no_change = 0
                
                for scroll in range(100):
                    self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(2)
                    
                    current_links = self.find_event_links()
                    event_links.update(current_links)
                    
                    if len(event_links) == last_count:
                        no_change += 1
                        if no_change >= 5:
                            break
                    else:
                        no_change = 0
                        if scroll % 5 == 0:
                            print(f"  Scroll {scroll + 1}: {len(event_links)} events found")
                    
                    last_count = len(event_links)
                    
                    if len(event_links) >= max_events:
                        break
                
                self.save_links(event_links)
                print(f"\n{'='*60}")
                print(f"Total event links: {len(event_links)}")
                print(f"{'='*60}")
                
                self.close()
                
            except Exception as e:
                print(f"Error: {e}")
                self.close()
                return all_events
        
        # Filter remaining links
        remaining_links = [link for link in event_links if link not in scraped_urls]
        remaining_links = remaining_links[:max_events - len(all_events)]
        
        print(f"\nAlready scraped: {len(all_events)}")
        print(f"Remaining: {len(remaining_links)}")
        print(f"{'='*60}")
        
        if not remaining_links:
            print("\n✓ All events already scraped!")
            return all_events
        
        # Scrape remaining events
        self.setup_driver()
        
        try:
            print(f"\nScraping events...\n")
            
            for idx, link in enumerate(remaining_links):
                try:
                    current_total = len(all_events) + 1
                    print(f"[{current_total}/{len(event_links)}] {link.split('/')[-2][:40]}...")
                    
                    event = self.scrape_event(link)
                    
                    if event and event.get('title'):
                        self.save_event(event, all_events)
                        self.scraped_urls.add(link)
                        print(f"  ✓ {event['title'][:50]}")
                    else:
                        print(f"  ✗ No data")
                    
                    time.sleep(0.5)
                    
                except KeyboardInterrupt:
                    print(f"\n\n⚠ Interrupted! Progress saved: {len(all_events)} events")
                    print(f"Run again to resume from event {len(all_events) + 1}")
                    break
                    
                except Exception as e:
                    print(f"  ✗ Error: {e}")
                    continue
            
            print(f"\n{'='*60}")
            print(f"Total: {len(all_events)} events")
            print(f"{'='*60}")
            
        finally:
            self.close()
        
        return all_events
    
    def find_event_links(self):
        """Find all event links"""
        links = set()
        
        try:
            selectors = [
                'a[href*="/tickets/"]',
                'a[href*="/event"]',
                'article a',
                '.event a',
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
        except:
            pass
        
        return links
    
    def scrape_event(self, url):
        """Scrape ONLY essential data from event"""
        try:
            self.driver.get(url)
            time.sleep(3)
            
            event = {'url': url}
            
            # Extract title
            try:
                h1 = self.driver.find_element(By.TAG_NAME, 'h1')
                event['title'] = h1.text.strip()
            except:
                event['title'] = self.driver.title.split('|')[0].strip()
            
            # Extract brief description (first 3 paragraphs only)
            description_lines = []
            try:
                p_elements = self.driver.find_elements(By.CSS_SELECTOR, 
                    'article p, .content p, .description p, main p, [class*="description"] p')
                
                for p in p_elements[:3]:  # Only first 3 paragraphs
                    text = p.text.strip()
                    if text and len(text) > 20:
                        description_lines.append(text)
                
                event['description'] = ' '.join(description_lines) if description_lines else None
            except:
                event['description'] = None
            
            # Extract date - try multiple methods
            date = None
            
            # Method 1: Try specific selectors
            date = self.find_text_by_selectors([
                '.event-date', '.date', 'time', '[class*="date"]', '[datetime]',
                '.when', '[class*="when"]', '[class*="time"]', '.schedule',
                '[class*="schedule"]'
            ])
            
            # Method 2: If no date found, search in all text for date patterns
            if not date:
                try:
                    import re
                    body_text = self.driver.find_element(By.TAG_NAME, 'body').text
                    
                    # Look for date patterns like "17 Jan - 15 Feb 2026" or "1 June 2026"
                    date_patterns = [
                        r'\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+(?:-\s+\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+)?\d{4}',
                        r'\d{1,2}/\d{1,2}/\d{4}',
                        r'\d{1,2}\.\d{1,2}\.\d{4}',
                        r'\d{1,2}-\d{1,2}-\d{4}',
                        r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+\d{4}',
                        r'\d{1,2}\s+(?:Ιαν|Φεβ|Μαρ|Απρ|Μαΐ|Ιουν|Ιουλ|Αυγ|Σεπ|Οκτ|Νοε|Δεκ)[α-ωά-ώ]*\s+\d{4}'
                    ]
                    
                    for pattern in date_patterns:
                        matches = re.findall(pattern, body_text, re.IGNORECASE)
                        if matches:
                            date = matches[0]
                            break
                except:
                    pass
            
            # Method 3: Look in meta tags
            if not date:
                try:
                    meta_date = self.driver.find_element(By.CSS_SELECTOR, 
                        'meta[property="event:start_date"], meta[name="date"]')
                    date = meta_date.get_attribute('content')
                except:
                    pass
            
            event['date'] = date
            
            # Extract location
            event['location'] = self.find_text_by_selectors([
                '.location', '.venue', '[class*="location"]', '[class*="venue"]',
                '.where', '[class*="where"]', '[class*="place"]'
            ])
            
            # Extract price
            event['price'] = self.find_text_by_selectors([
                '.price', '[class*="price"]', '.cost', '[class*="ticket"]',
                '[class*="admission"]'
            ])
            
            # Extract category
            event['category'] = self.find_text_by_selectors([
                '.category', '[class*="category"]', '.tag', '[class*="tag"]',
                '.genre', '[class*="genre"]'
            ])
            
            # Extract ONLY 2-3 main images - try harder to find them
            images = []
            try:
                # Try multiple strategies to find images
                img_selectors = [
                    'img[src*="more.com"]',  # Images from more.com domain
                    'img[src*="jpg"]',
                    'img[src*="jpeg"]',
                    'img[src*="png"]',
                    'img[src*="webp"]',
                    'article img',
                    '.content img',
                    'main img',
                    '[class*="image"] img',
                    '[class*="photo"] img',
                    '[class*="picture"] img',
                    'img'  # All images as last resort
                ]
                
                for selector in img_selectors:
                    if len(images) >= 3:
                        break
                    
                    try:
                        img_elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        
                        for img in img_elements:
                            src = img.get_attribute('src')
                            
                            # Filter out logos, icons, and small images
                            if (src and 
                                'logo' not in src.lower() and 
                                'icon' not in src.lower() and
                                'avatar' not in src.lower() and
                                'sprite' not in src.lower() and
                                src not in images):
                                
                                images.append(src)
                                
                                if len(images) >= 3:
                                    break
                    except:
                        continue
                
                event['images'] = images
            except:
                event['images'] = []
            
            # If still no images, try to get from background-image CSS
            if not images:
                try:
                    elements_with_bg = self.driver.find_elements(By.CSS_SELECTOR, 
                        '[style*="background-image"], [class*="image"], [class*="photo"]')
                    
                    for elem in elements_with_bg[:3]:
                        style = elem.get_attribute('style')
                        if style and 'url(' in style:
                            # Extract URL from background-image
                            import re
                            urls = re.findall(r'url\(["\']?([^"\']+)["\']?\)', style)
                            for url_found in urls:
                                if url_found and url_found not in images:
                                    images.append(url_found)
                                    if len(images) >= 3:
                                        break
                    
                    event['images'] = images
                except:
                    pass
            
            return event
            
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

if __name__ == "__main__":
    print("More.com Events Scraper (Optimized & Resumable)")
    print("=" * 60)
    print("Extracts: title, brief description, 2-3 images, date, location, price")
    print("=" * 60)
    
    max_events = input("\nHow many events to scrape? (default: 5000): ").strip()
    max_events = int(max_events) if max_events.isdigit() else 5000
    
    resume = input("Resume from previous session? (Y/n): ").strip().lower()
    resume = resume != 'n'
    
    scraper = MoreEventsScraperOptimized(headless=False)
    events = scraper.scrape_all_events(max_events=max_events, resume=resume)
    
    print(f"\n{'='*60}")
    print(f"✓ Final: {len(events)} events")
    print(f"✓ Saved to: scraped_data/more_events_optimized.json")
    print(f"{'='*60}")
