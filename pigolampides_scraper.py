"""
Scraper for Pigolampides blog
URL: https://pigolampides.gr/blog/
"""

from scraper_base import BaseScraper
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import os
import time
import config

class PigolampidesScraper(BaseScraper):
    def __init__(self, headless=False):
        super().__init__(headless)
        self.base_url = "https://pigolampides.gr"
        self.blog_url = "https://pigolampides.gr/blog/"
        self.scraped_urls = set()
    
    def scrape_all_posts(self, max_posts=200):
        """
        Scrape all blog posts from Pigolampides
        """
        self.setup_driver()
        all_posts = []
        post_links = set()
        
        try:
            print(f"Navigating to {self.blog_url}...")
            self.driver.get(self.blog_url)
            time.sleep(4)
            
            # Scroll and load all posts
            print("\nLoading all blog posts...")
            last_count = 0
            no_change = 0
            
            for scroll in range(50):
                # Scroll down
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
                
                # Collect post links
                current_links = self.find_post_links()
                post_links.update(current_links)
                
                if len(post_links) == last_count:
                    no_change += 1
                    if no_change >= 3:
                        print(f"  No new posts after {no_change} scrolls")
                        break
                else:
                    no_change = 0
                    print(f"  Scroll {scroll + 1}: {len(post_links)} posts found")
                
                last_count = len(post_links)
                
                if len(post_links) >= max_posts:
                    break
                
                # Try to click "Load More" or pagination
                try:
                    load_more = self.driver.find_element(By.CSS_SELECTOR, 
                        'button, a[class*="load"], [class*="more"], .pagination a')
                    
                    if load_more.is_displayed():
                        print(f"  Clicking: {load_more.text}")
                        load_more.click()
                        time.sleep(2)
                except:
                    pass
            
            print(f"\n{'='*60}")
            print(f"Total post links collected: {len(post_links)}")
            print(f"{'='*60}")
            
            # Limit to max_posts
            post_links = list(post_links)[:max_posts]
            
            # Scrape each post
            print(f"\nScraping {len(post_links)} blog posts...\n")
            
            for idx, link in enumerate(post_links):
                if link in self.scraped_urls:
                    continue
                
                try:
                    print(f"[{idx + 1}/{len(post_links)}] {link.split('/')[-2][:50]}...")
                    post = self.scrape_post(link)
                    
                    if post and post.get('title'):
                        all_posts.append(post)
                        self.scraped_urls.add(link)
                        print(f"  ✓ {post['title'][:60]}")
                    else:
                        print(f"  ✗ No data extracted")
                    
                    time.sleep(0.5)
                    
                except Exception as e:
                    print(f"  ✗ Error: {e}")
                    continue
            
            print(f"\n{'='*60}")
            print(f"Successfully scraped {len(all_posts)} posts")
            print(f"{'='*60}")
            
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            self.close()
        
        return all_posts
    
    def find_post_links(self):
        """Find all blog post links on current page"""
        links = set()
        
        try:
            # Try multiple selectors for blog posts
            selectors = [
                'article a',
                '.post a',
                '.blog-post a',
                '[class*="post"] a',
                '[class*="article"] a',
                'a[href*="/blog/"]'
            ]
            
            for selector in selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    
                    for element in elements:
                        href = element.get_attribute('href')
                        
                        # Filter for actual blog post pages
                        if (href and 
                            self.base_url in href and
                            '/blog/' in href and
                            href != self.blog_url and
                            not href.endswith('/blog/')):
                            links.add(href)
                except:
                    continue
        
        except Exception as e:
            print(f"Error finding links: {e}")
        
        return links
    
    def scrape_post(self, url):
        """Scrape a single blog post"""
        try:
            self.driver.get(url)
            time.sleep(3)
            
            post = {'url': url}
            
            # Extract title
            try:
                h1 = self.driver.find_element(By.TAG_NAME, 'h1')
                post['title'] = h1.text.strip()
            except:
                post['title'] = self.driver.title.split('|')[0].strip()
            
            # Extract date
            post['date'] = self.find_text_by_selectors([
                '.date',
                'time',
                '[class*="date"]',
                '[datetime]',
                '.published',
                '[class*="published"]'
            ])
            
            # Extract author
            post['author'] = self.find_text_by_selectors([
                '.author',
                '[class*="author"]',
                '[rel="author"]',
                '.byline'
            ])
            
            # Extract category/tags
            categories = []
            try:
                cat_elements = self.driver.find_elements(By.CSS_SELECTOR, 
                    '.category, .tag, [rel="category"], [rel="tag"]')
                
                for cat in cat_elements:
                    text = cat.text.strip()
                    if text:
                        categories.append(text)
                
                post['categories'] = categories
            except:
                post['categories'] = []
            
            # Extract content
            content_paragraphs = []
            try:
                p_elements = self.driver.find_elements(By.CSS_SELECTOR, 
                    'article p, .content p, .post-content p, .entry-content p, main p')
                
                for p in p_elements:
                    text = p.text.strip()
                    if text and len(text) > 20:
                        content_paragraphs.append(text)
                
                post['content'] = content_paragraphs
            except:
                post['content'] = []
            
            # Extract excerpt/summary
            post['excerpt'] = self.find_text_by_selectors([
                '.excerpt',
                '.summary',
                '[class*="excerpt"]',
                '[class*="summary"]'
            ])
            
            # Extract images
            try:
                images = []
                img_elements = self.driver.find_elements(By.CSS_SELECTOR, 
                    'article img, .content img, .post-content img, main img')
                
                for img in img_elements[:10]:
                    src = img.get_attribute('src')
                    alt = img.get_attribute('alt')
                    
                    if src and 'logo' not in src.lower() and 'icon' not in src.lower():
                        images.append({
                            'src': src,
                            'alt': alt
                        })
                
                post['images'] = images
            except:
                post['images'] = []
            
            # Extract full text as backup
            try:
                body = self.driver.find_element(By.TAG_NAME, 'body')
                post['full_text'] = body.text[:2000]
            except:
                post['full_text'] = None
            
            return post
            
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
    
    def save_posts(self, posts, filename='pigolampides_blog_posts.json'):
        """Save posts to JSON"""
        os.makedirs(config.OUTPUT_DIR, exist_ok=True)
        filepath = os.path.join(config.OUTPUT_DIR, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(posts, f, indent=2, ensure_ascii=False)
        
        print(f"\n{'='*60}")
        print(f"✓ Posts saved to: {filepath}")
        print(f"{'='*60}")
        return filepath

if __name__ == "__main__":
    print("Pigolampides Blog Scraper")
    print("=" * 60)
    print("URL: https://pigolampides.gr/blog/")
    print("=" * 60)
    
    max_posts = input("\nHow many posts to scrape? (default: 200): ").strip()
    max_posts = int(max_posts) if max_posts.isdigit() else 200
    
    scraper = PigolampidesScraper(headless=False)
    posts = scraper.scrape_all_posts(max_posts=max_posts)
    
    if posts:
        filepath = scraper.save_posts(posts)
        print(f"\n✓ Successfully scraped {len(posts)} blog posts!")
        
        # Show statistics
        print(f"\nStatistics:")
        print(f"  Total posts: {len(posts)}")
        
        # Count by category
        all_categories = {}
        for post in posts:
            for cat in post.get('categories', []):
                all_categories[cat] = all_categories.get(cat, 0) + 1
        
        if all_categories:
            print(f"\n  Top categories:")
            for cat, count in sorted(all_categories.items(), key=lambda x: x[1], reverse=True)[:5]:
                print(f"    - {cat}: {count}")
        
        # Count with images
        with_images = sum(1 for p in posts if p.get('images'))
        print(f"\n  Posts with images: {with_images}")
        
    else:
        print("\n✗ No posts scraped")
