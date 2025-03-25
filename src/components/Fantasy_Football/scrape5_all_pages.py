import os
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Selenium WebDriver Setup
options = Options()
options.add_argument("--headless")  # Run in headless mode for speed
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("start-maximized")
options.add_argument("window-size=1920x1080")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

# Initialize the WebDriver with a 45-second page load timeout
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
driver.set_page_load_timeout(45)

# Read URLs from file
url_file = "pro_football_urls.txt"
if not os.path.exists(url_file):
    print(f"File {url_file} not found. Exiting...")
    driver.quit()
    exit()

with open(url_file, "r") as f:
    urls = [line.strip() for line in f.readlines() if line.strip()]

# Create directory to store CSV files
output_dir = "football_data"
os.makedirs(output_dir, exist_ok=True)

for url in urls:
    print(f"Scraping: {url}")

    # Open the webpage
    try:
        driver.get(url)
    except TimeoutException:
        print(f"Page {url} took too long to load. Skipping...")
        continue

    # Wait for tables to load (max 20 seconds)
    try:
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, "table_container")))
    except TimeoutException:
        print(f"Tables took too long to load on {url}. Skipping...")
        continue

    # Find all table containers
    table_containers = driver.find_elements(By.CLASS_NAME, "table_container")

    for idx, container in enumerate(table_containers):
        try:
            # Get the table element
            table = container.find_element(By.TAG_NAME, "table")
            table_id = table.get_attribute("id") or f"table_{idx+1}"

            # Extract headers (get only the last header row)
            header_rows = table.find_elements(By.TAG_NAME, "thead")
            headers = []
            if header_rows:
                last_header_row = header_rows[-1].find_elements(By.TAG_NAME, "th")
                headers = [th.text.strip() for th in last_header_row]

            # Extract table rows
            rows = table.find_elements(By.TAG_NAME, "tr")
            data = []
            for row in rows:
                cols = row.find_elements(By.TAG_NAME, "td")
                first_col = row.find_elements(By.TAG_NAME, "th")  # Some tables use <th> for first column

                # Ensure the first column is included
                row_data = [col.text.strip() for col in first_col + cols]
                if row_data:
                    data.append(row_data)

            # Remove duplicate headers (if first row matches headers)
            if data and data[0] == headers:
                data.pop(0)

            # Adjust headers if they don't match row length
            max_cols = max(len(row) for row in data) if data else 0
            if len(headers) != max_cols:
                headers = [f"Column_{i+1}" for i in range(max_cols)]

            # Convert to DataFrame
            df = pd.DataFrame(data, columns=headers)

            # Generate a filename based on URL and table ID
            url_part = url.split("/")[-1].replace(".htm", "").replace("-", "_")
            csv_filename = os.path.join(output_dir, f"{url_part}_{table_id}.csv")
            df.to_csv(csv_filename, index=False)
            print(f"Saved: {csv_filename}")

        except (TimeoutException, NoSuchElementException) as e:
            print(f"Error processing table {idx+1} on {url}: {e}")

# Close the WebDriver
driver.quit()
