import os
from dotenv import load_dotenv

load_dotenv()

# Chrome settings
CHROME_DRIVER_PATH = os.getenv('CHROME_DRIVER_PATH', 'auto')
HEADLESS_MODE = os.getenv('HEADLESS_MODE', 'False').lower() == 'true'

# Scraping settings
TIMEOUT = int(os.getenv('TIMEOUT', 10))
RETRY_ATTEMPTS = int(os.getenv('RETRY_ATTEMPTS', 3))

# Output settings
OUTPUT_DIR = 'scraped_data'
