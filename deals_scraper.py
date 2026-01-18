from scraper_base import BaseScraper
from selenium.webdriver.common.by import By
import json
import os
import config

class DealsScraper(BaseScraper):
    def __init__(self, headless=config.HEADLESS_MODE):
        super().__init__(headless)
        
    def scrape_deals(self, url, selectors):
        """
        Scrape deals from a website
        
        Args:
            url: Website URL to scrape
            selectors: Dictionary with CSS selectors for deal elements
                Example: {
                    'container': '.deal-card',
                    'title': '.deal-title',
                    'price': '.deal-price',
                    'discount': '.deal-discount',
                    'description': '.deal-description'
                }
        """
        self.setup_driver()
        deals = []
        
        try:
            self.driver.get(url)
            self.scroll_to_bottom()
            
            # Wait for deal containers to load
            deal_elements = self.wait_for_elements(By.CSS_SELECTOR, selectors['container'])
            
            for element in deal_elements:
                deal = {}
                
                for key, selector in selectors.items():
                    if key == 'container':
                        continue
                    
                    try:
                        deal[key] = element.find_element(By.CSS_SELECTOR, selector).text
                    except:
                        deal[key] = None
                
                deals.append(deal)
            
            print(f"Scraped {len(deals)} deals")
            
        except Exception as e:
            print(f"Error scraping deals: {e}")
        
        finally:
            self.close()
        
        return deals
    
    def save_deals(self, deals, filename='deals.json'):
        """Save deals to JSON file"""
        os.makedirs(config.OUTPUT_DIR, exist_ok=True)
        filepath = os.path.join(config.OUTPUT_DIR, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(deals, f, indent=2, ensure_ascii=False)
        
        print(f"Deals saved to {filepath}")
