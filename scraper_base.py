from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import config

try:
    from webdriver_manager.chrome import ChromeDriverManager
    WEBDRIVER_MANAGER_AVAILABLE = True
except:
    WEBDRIVER_MANAGER_AVAILABLE = False

class BaseScraper:
    def __init__(self, headless=config.HEADLESS_MODE):
        self.driver = None
        self.headless = headless
        self.wait_timeout = config.TIMEOUT
        
    def setup_driver(self):
        """Initialize Chrome driver with options"""
        chrome_options = Options()
        
        if self.headless:
            chrome_options.add_argument('--headless=new')
        
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36')
        
        # Disable automation flags
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        print("Setting up Chrome driver...")
        
        # Use the ChromeDriver from config
        try:
            if config.CHROME_DRIVER_PATH and config.CHROME_DRIVER_PATH != 'auto':
                service = ChromeService(executable_path=config.CHROME_DRIVER_PATH)
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
                print(f"✓ Using ChromeDriver from: {config.CHROME_DRIVER_PATH}")
            else:
                self.driver = webdriver.Chrome(options=chrome_options)
                print("✓ Using system ChromeDriver")
        except Exception as e:
            print(f"✗ Failed to initialize Chrome: {e}")
            raise
        
        # Try to maximize window, but don't fail if it doesn't work
        try:
            self.driver.maximize_window()
        except:
            pass
        
    def wait_for_element(self, by, value, timeout=None):
        """Wait for element to be present"""
        timeout = timeout or self.wait_timeout
        return WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located((by, value))
        )
    
    def wait_for_elements(self, by, value, timeout=None):
        """Wait for elements to be present"""
        timeout = timeout or self.wait_timeout
        return WebDriverWait(self.driver, timeout).until(
            EC.presence_of_all_elements_located((by, value))
        )
    
    def scroll_to_bottom(self, pause_time=2):
        """Scroll to bottom of page to load dynamic content"""
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        
        while True:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(pause_time)
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            
            if new_height == last_height:
                break
            last_height = new_height
    
    def close(self):
        """Close the browser"""
        if self.driver:
            self.driver.quit()
