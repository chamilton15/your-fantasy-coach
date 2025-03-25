import os
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By

# Initialize the WebDriver
driver = webdriver.Chrome()

# Open the webpage
url = "https://www.pro-football-reference.com/years/2024/index.htm"
driver.get(url)

# Wait for page to load
time.sleep(3)

# Create directory to store CSV files
output_dir = "football_data"
os.makedirs(output_dir, exist_ok=True)

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

        # Adjust headers if they don't match row length
        max_cols = max(len(row) for row in data) if data else 0
        if len(headers) != max_cols:
            headers = [f"Column_{i+1}" for i in range(max_cols)]

        # Convert to DataFrame
        df = pd.DataFrame(data, columns=headers)

        # Save table to CSV
        csv_filename = os.path.join(output_dir, f"{table_id}.csv")
        df.to_csv(csv_filename, index=False)
        print(f"Saved: {csv_filename}")

    except Exception as e:
        print(f"Error processing table {idx+1}: {e}")

# Close the WebDriver
driver.quit()
