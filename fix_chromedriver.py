"""
Script to manually download and setup the correct ChromeDriver
"""
import os
import sys
import zipfile
import requests
from pathlib import Path

def get_chrome_version():
    """Get installed Chrome version"""
    import subprocess
    try:
        # Try to get Chrome version on Windows
        result = subprocess.run(
            ['reg', 'query', 'HKEY_CURRENT_USER\\Software\\Google\\Chrome\\BLBeacon', '/v', 'version'],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            version = result.stdout.split()[-1]
            return version
    except:
        pass
    
    # Fallback: check Chrome executable
    chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    if os.path.exists(chrome_path):
        try:
            result = subprocess.run(
                [chrome_path, '--version'],
                capture_output=True,
                text=True
            )
            version = result.stdout.strip().split()[-1]
            return version
        except:
            pass
    
    return None

def download_chromedriver(version):
    """Download ChromeDriver for specific version"""
    major_version = version.split('.')[0]
    
    print(f"Chrome version: {version}")
    print(f"Major version: {major_version}")
    
    # ChromeDriver download URL for version 143
    base_url = "https://storage.googleapis.com/chrome-for-testing-public"
    
    # Try to get the exact version
    try:
        # Get available versions
        versions_url = f"{base_url}/{version}/win64/chromedriver-win64.zip"
        
        print(f"Downloading from: {versions_url}")
        
        response = requests.get(versions_url, stream=True)
        
        if response.status_code == 200:
            # Save to local directory
            zip_path = "chromedriver-win64.zip"
            
            with open(zip_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            print(f"Downloaded to {zip_path}")
            
            # Extract
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall('.')
            
            print("Extracted ChromeDriver")
            
            # Clean up
            os.remove(zip_path)
            
            driver_path = os.path.join(os.getcwd(), 'chromedriver-win64', 'chromedriver.exe')
            
            if os.path.exists(driver_path):
                print(f"\n✓ ChromeDriver installed at: {driver_path}")
                print(f"\nUpdate your .env file with:")
                print(f"CHROME_DRIVER_PATH={driver_path}")
                return driver_path
            
        else:
            print(f"Failed to download. Status code: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"Error downloading ChromeDriver: {e}")
        return None

if __name__ == "__main__":
    print("ChromeDriver Fixer")
    print("=" * 60)
    
    version = get_chrome_version()
    
    if not version:
        print("Could not detect Chrome version.")
        version = input("Enter your Chrome version (e.g., 143.0.7499.193): ").strip()
    
    if version:
        download_chromedriver(version)
    else:
        print("No version provided. Exiting.")
