"""
Direct scraper for Greek Ministry of Culture events
Goes directly to the events listing page
"""

from scraper_base import BaseScraper
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import os
import time
import config

class CultureDirectScraper(BaseScraper):
    def __init__(self, headless=False):
        super().__init__(headless)
        self.base_url = "https://allofgreeceone.culture.gov.gr"
        self.scraped_urls = set()
    
    def scrape_all_events(self, max_events=968):
        """
        Scrape all events by navigating through the site
        """
        self.setup_driver()
        all_events = []
        event_links = set()
        
        try:
            # Try multiple entry points
            urls_to_try = [
                f"{self.base_url}/en/on-demand/",
                f"{self.base_url}/en/",
                f"{self.base_url}/on-demand/",
            ]
            
            for url in urls_to_try:
                print(f"\nTrying URL: {url}")
                self.driver.get(url)
                time.sleep(4)
                
                # Check if we're on the right page
                page_title = self.driver.title
                print(f"Page title: {page_title}")
                
                # Save page source for debugging
                if len(event_links) == 0:
                    print("Analyzing page structure...")
                    self.analyze_page_structure()
                
                # Try to find event links
                links = self.find_event_links_comprehensive()
                
                if links:
                    event_links.update(links)
                    print(f"✓ Found {len(links)} event links from this URL")
                    print(f"Total unique links: {len(event_links)}")
                    
                    # If we found events, continue scrolling on this page
                    if len(event_links) < max_events:
                        print("\nScrolling to load more events...")
                        additional_links = self.scroll_and_collect(max_events - len(event_links))
                        event_links.update(additional_links)
                        print(f"After scrolling: {len(event_links)} total links")
                    
                    break  # Found events, no need to try other URLs
            
            if not event_links:
                print("\n✗ Could not find any event links")
                print("Saving page HTML for manual inspection...")
                with open('page_debug.html', 'w', encoding='utf-8') as f:
                    f.write(self.driver.page_source)
                print("Saved to: page_debug.html")
                return []
            
            print(f"\n{'='*60}")
            print(f"Total event links collected: {len(event_links)}")
            print(f"{'='*60}")
            
            # Convert to list and limit
            event_links = list(event_links)[:max_events]
            
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
    
    def analyze_page_structure(self):
        """Analyze page to understand structure"""
        try:
            # Count different element types
            print("\nPage structure analysis:")
            
            # Check for common containers
            containers = {
                'articles': len(self.driver.find_elements(By.TAG_NAME, 'article')),
                'divs with class containing "event"': len(self.driver.find_elements(By.CSS_SELECTOR, '[class*="event"]')),
                'divs with class containing "item"': len(self.driver.find_elements(By.CSS_SELECTOR, '[class*="item"]')),
                'divs with class containing "post"': len(self.driver.find_elements(By.CSS_SELECTOR, '[class*="post"]')),
                'links': len(self.driver.find_elements(By.TAG_NAME, 'a')),
            }
            
            for name, count in containers.items():
                print(f"  {name}: {count}")
            
            # Sample some links
            all_links = self.driver.find_elements(By.TAG_NAME, 'a')
            print(f"\nSample links (first 10):")
            for i, link in enumerate(all_links[:10]):
                href = link.get_attribute('href')
                text = link.text.strip()[:50]
                if href:
                    print(f"  {i+1}. {href} | {text}")
        
        except Exception as e:
            print(f"Error analyzing page: {e}")
    
    def find_event_links_comprehensive(self):
        """Try every possible way to find event links"""
        links = set()
        
        try:
            # Get ALL links on the page
            all_links = self.driver.find_elements(By.TAG_NAME, 'a')
            
            print(f"  Analyzing {len(all_links)} links on page...")
            
            for link in all_links:
                href = link.get_attribute('href')
                
                if not href:
                    continue
                
                # Filter for event-related URLs
                # Look for patterns that indicate event pages
                if (self.base_url in href and
                    any(keyword in href.lower() for keyword in [
                        '/on-demand/',
                        '/event',
                        '/production',
                        '/performance',
                        '/exhibition',
                        '/concert',
                        '/theater',
                        '/theatre'
                    ]) and
                    # Exclude navigation/category pages
                    '/category/' not in href and
                    '/tag/' not in href and
                    '/page/' not in href and
                    '/author/' not in href and
                    href != self.base_url and
                    href != self.base_url + '/' and
                    href != self.base_url + '/en/' and
                    href != self.base_url + '/en/on-demand/'):
                    
                    links.add(href)
        
        except Exception as e:
            print(f"Error finding links: {e}")
        
        return links
    
    def scroll_and_collect(self, max_additional):
        """Scroll page and collect more event links"""
        additional_links = set()
        last_count = 0
        no_change_count = 0
        
        for scroll in range(100):  # Max 100 scrolls to get all 968 events
            # Scroll down in smaller increments
            self.driver.execute_script("window.scrollBy(0, 500);")
            time.sleep(1)
            
            # Every 5 scrolls, scroll to bottom
            if scroll % 5 == 0:
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
                
                # Collect links
                new_links = self.find_event_links_comprehensive()
                additional_links.update(new_links)
                
                # Check progress
                if len(additional_links) == last_count:
                    no_change_count += 1
                    if no_change_count >= 5:
                        print(f"  No new links after {no_change_count} checks, stopping")
                        break
                else:
                    no_change_count = 0
                    print(f"  Check {scroll // 5 + 1}: {len(additional_links)} links")
                
                last_count = len(additional_links)
                
                if len(additional_links) >= max_additional:
                    break
            
            # Try to click "Load More" button every 10 scrolls
            if scroll % 10 == 0:
                try:
                    load_buttons = self.driver.find_elements(By.CSS_SELECTOR, 
                        'button, a[class*="load"], [class*="more"], [class*="show"]')
                    
                    for button in load_buttons:
                        if button.is_displayed() and button.is_enabled():
                            text = button.text.lower()
                            if any(word in text for word in ['load', 'more', 'show']):
                                print(f"  Clicking: {button.text}")
                                button.click()
                                time.sleep(2)
                                break
                except:
                    pass
        
        return additional_links
    
    def scrape_event_detail(self, url):
        """Scrape detailed information from an event page"""
        try:
            self.driver.get(url)
            
            # Wait for page to load
            time.sleep(3)
            
            # Wait for content to appear
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "h1"))
                )
            except:
                pass
            
            event = {'url': url}
            
            # Extract title - try multiple approaches
            title = None
            try:
                title = self.driver.find_element(By.TAG_NAME, 'h1').text.strip()
            except:
                pass
            
            if not title:
                title = self.find_text_by_selectors([
                    '.entry-title',
                    '.title',
                    'header h1',
                    'article h1',
                    '[class*="title"]'
                ])
            
            event['title'] = title
            
            # Extract date
            event['date'] = self.find_text_by_selectors([
                '.date',
                'time',
                '[class*="date"]',
                '.event-date',
                '[datetime]'
            ])
            
            # Extract location
            event['location'] = self.find_text_by_selectors([
                '.location',
                '.venue',
                '[class*="location"]',
                '[class*="venue"]',
                '[class*="place"]'
            ])
            
            # Extract description - get all paragraphs
            descriptions = []
            try:
                p_elements = self.driver.find_elements(By.CSS_SELECTOR, 
                    'p, .content, .description, [class*="content"]')
                
                for elem in p_elements:
                    text = elem.text.strip()
                    if text and len(text) > 30 and text not in descriptions:
                        descriptions.append(text)
                        if len(descriptions) >= 3:  # Get first 3 paragraphs
                            break
                
                event['description'] = ' '.join(descriptions) if descriptions else None
            except:
                event['description'] = None
            
            # Extract category
            event['category'] = self.find_text_by_selectors([
                '.category a',
                '[rel="category"]',
                '[class*="category"]',
                '.tag'
            ])
            
            # Extract organizer
            event['organizer'] = self.find_text_by_selectors([
                '.organizer',
                '.institution',
                '[class*="organizer"]',
                '[class*="institution"]'
            ])
            
            # Extract all text as fallback
            try:
                body = self.driver.find_element(By.TAG_NAME, 'body')
                event['full_text'] = body.text[:2000]  # First 2000 chars
            except:
                event['full_text'] = None
            
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
            
            return event if event['title'] else None
            
        except Exception as e:
            print(f"    Error details: {e}")
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
    
    def save_events(self, events, filename='culture_gov_direct_events.json'):
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
    print("Greek Ministry of Culture - Direct Scraper")
    print("=" * 60)
    print("Comprehensive scraper with page analysis")
    print("=" * 60)
    
    max_events = input("\nHow many events to scrape? (default: 968): ").strip()
    max_events = int(max_events) if max_events.isdigit() else 968
    
    scraper = CultureDirectScraper(headless=False)
    events = scraper.scrape_all_events(max_events=max_events)
    
    if events:
        filepath = scraper.save_events(events)
        print(f"\n✓ Successfully scraped {len(events)} events!")
    else:
        print("\n✗ No events found. Check page_debug.html for page structure.")
