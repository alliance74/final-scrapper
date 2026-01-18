"""
Improved scraper for Visit Greece events with pagination support
"""

from scraper_base import BaseScraper
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import os
import time
import config

class VisitGreeceImprovedScraper(BaseScraper):
    def __init__(self, headless=False):
        super().__init__(headless)
        self.base_url = "https://www.visitgreece.gr/events"
        self.scraped_urls = set()
    
    def scrape_all_events(self, max_events=200):
        """
        Scrape events with pagination support
        
        Args:
            max_events: Maximum number of events to scrape
        """
        self.setup_driver()
        all_events = []
        page = 1
        
        try:
            while len(all_events) < max_events:
                print(f"\n{'='*60}")
                print(f"Scraping page {page}...")
                print(f"{'='*60}")
                
                # Navigate to page
                if page == 1:
                    url = self.base_url
                else:
                    url = f"{self.base_url}/?pg={page}"
                
                self.driver.get(url)
                time.sleep(3)
                
                # Scroll to load content
                self.scroll_to_bottom(pause_time=1)
                
                # Get event links from this page
                event_links = self.get_event_links_from_page()
                
                if not event_links:
                    print(f"No more events found on page {page}")
                    break
                
                print(f"Found {len(event_links)} event links on page {page}")
                
                # Scrape each event
                events_scraped_this_page = 0
                for link in event_links:
                    if len(all_events) >= max_events:
                        break
                    
                    if link in self.scraped_urls:
                        continue
                    
                    try:
                        event_details = self.scrape_event_detail_page(link)
                        if event_details:
                            all_events.append(event_details)
                            self.scraped_urls.add(link)
                            events_scraped_this_page += 1
                            print(f"  [{len(all_events)}/{max_events}] ✓ {event_details.get('title', 'N/A')[:50]}")
                        
                        time.sleep(0.5)  # Be polite
                        
                    except Exception as e:
                        print(f"  ✗ Error scraping {link}: {e}")
                        continue
                
                if events_scraped_this_page == 0:
                    print("No new events on this page, stopping...")
                    break
                
                page += 1
                time.sleep(1)
            
            print(f"\n{'='*60}")
            print(f"Total unique events scraped: {len(all_events)}")
            print(f"{'='*60}")
            
        except Exception as e:
            print(f"Error during scraping: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            self.close()
        
        return all_events
    
    def get_event_links_from_page(self):
        """Extract event links from current page, excluding navigation links"""
        links = []
        
        try:
            # Find all links on the page
            all_links = self.driver.find_elements(By.TAG_NAME, 'a')
            
            for link in all_links:
                href = link.get_attribute('href')
                
                if not href:
                    continue
                
                # Filter for actual event pages
                # Include links that have /events/ followed by category and event name
                # Exclude: main events page, pagination, language switches
                if (href and 
                    '/events/' in href and 
                    href != self.base_url and
                    href != self.base_url + '/' and
                    '?pg=' not in href and
                    '/el/events/' not in href and  # Exclude Greek version
                    href.count('/') > 4):  # Event pages have more path segments
                    
                    if href not in links and href not in self.scraped_urls:
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
            
            # Extract title - try h1 first
            try:
                title_element = self.driver.find_element(By.TAG_NAME, 'h1')
                event['title'] = title_element.text.strip()
            except:
                event['title'] = None
            
            # Extract date/time
            event['date'] = self.find_text_by_selectors([
                '.event-date', 
                '[class*="date"]', 
                'time',
                '.date'
            ])
            
            # Extract location
            event['location'] = self.find_text_by_selectors([
                '.event-location',
                '[class*="location"]',
                '.location',
                '[class*="venue"]'
            ])
            
            # Extract description - get first paragraph or description div
            event['description'] = self.find_text_by_selectors([
                '.event-description',
                '[class*="description"]',
                'article p',
                '.content p',
                'p'
            ])
            
            # Extract category
            event['category'] = self.find_text_by_selectors([
                '.category',
                '[class*="category"]',
                '.tag',
                '[class*="tag"]'
            ])
            
            # Extract price/cost
            event['price'] = self.find_text_by_selectors([
                '.price',
                '[class*="price"]',
                '.cost',
                '[class*="cost"]',
                '[class*="ticket"]'
            ])
            
            # Extract contact info
            event['contact'] = self.find_text_by_selectors([
                '.contact',
                '[class*="contact"]',
                '.phone',
                '[class*="phone"]',
                '.email',
                '[class*="email"]'
            ])
            
            # Extract website/link
            event['website'] = self.find_attribute_by_selectors([
                'a[href*="http"]'
            ], 'href')
            
            # Extract images - get main event image
            try:
                images = []
                img_elements = self.driver.find_elements(By.CSS_SELECTOR, 'img')
                for img in img_elements[:5]:  # Get first 5 images
                    src = img.get_attribute('src')
                    if src and 'logo' not in src.lower() and 'icon' not in src.lower():
                        images.append(src)
                event['images'] = images
            except:
                event['images'] = []
            
            return event if event['title'] else None
            
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
                    if text and len(text) > 2:  # Avoid empty or very short strings
                        return text
            except:
                continue
        return None
    
    def find_attribute_by_selectors(self, selectors, attribute):
        """Try multiple selectors to find an attribute"""
        for selector in selectors:
            try:
                element = self.driver.find_element(By.CSS_SELECTOR, selector)
                attr = element.get_attribute(attribute)
                if attr:
                    return attr
            except:
                continue
        return None
    
    def save_events(self, events, filename='visitgreece_all_events.json'):
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
    print("Visit Greece Improved Events Scraper")
    print("=" * 60)
    print("This scraper will:")
    print("1. Navigate through all event pages")
    print("2. Extract unique event links")
    print("3. Scrape detailed information from each event")
    print("=" * 60)
    
    max_events = input("\nHow many events to scrape? (default: 200): ").strip()
    max_events = int(max_events) if max_events.isdigit() else 200
    
    scraper = VisitGreeceImprovedScraper(headless=False)
    events = scraper.scrape_all_events(max_events=max_events)
    
    if events:
        filepath = scraper.save_events(events)
        print(f"\n✓ Successfully scraped {len(events)} unique events!")
        
        # Show summary
        print(f"\nEvent categories:")
        categories = {}
        for event in events:
            cat = event.get('category', 'Unknown')
            categories[cat] = categories.get(cat, 0) + 1
        
        for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
            print(f"  - {cat}: {count}")
    else:
        print("\n✗ No events found.")
