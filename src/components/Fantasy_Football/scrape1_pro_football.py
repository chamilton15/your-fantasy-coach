from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from collections import deque
import time
import re
import os

# Selenium WebDriver Setup
options = Options()
options.add_argument("--headless")  # Run in headless mode for speed
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("start-maximized")
options.add_argument("window-size=1920x1080")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Base URL
base_url = 'https://www.pro-football-reference.com/years/2024/index.htm'
visited_urls = set()
url_queue = deque([base_url])  # Use a queue for iterative processing
output_file = 'pro_football_urls.txt'

def is_valid_url(url):
    """Check if URL is valid (on pro-football-reference, and either has '2024' or no year)."""
    return 'pro-football-reference.com' in url and ('2024' in url or not re.search(r'\d{4}', url))

# Clear output file if it exists
if os.path.exists(output_file):
    os.remove(output_file)

# Scraping Loop
while url_queue:
    url = url_queue.popleft()  # Get next URL from queue
    if url in visited_urls:
        continue
    
    try:
        driver.get(url)
        print(f"Scraping: {url}")

        # Extract links from the page
        links = driver.find_elements(By.TAG_NAME, 'a')
        new_urls = set()  # Store valid URLs found on the page

        for link in links:
            href = link.get_attribute('href')
            if href and href not in visited_urls and is_valid_url(href):
                new_urls.add(href)

        # Add new URLs to queue and visited set
        url_queue.extend(new_urls)
        visited_urls.update(new_urls)

        # Batch write new URLs to the file
        with open(output_file, 'a') as f:
            for new_url in new_urls:
                f.write(new_url + '\n')

    except Exception as e:
        print(f"Error scraping {url}: {e}")

    time.sleep(1)  # Reduce sleep time

# Close the driver
driver.quit()
