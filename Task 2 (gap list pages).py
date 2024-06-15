import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException

# Initialize the Chrome driver
driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))

# Open the specified URL
url = "https://www.gap.com/browse/category.do?cid=5664&nav=meganav%3AWomen%3ACategories%3AJeans#pageId=0&department=136"
driver.get(url)

# Wait for the promotional banner to appear and close it
try:
    print("Waiting for the promotional banner to appear...")
    banner_close_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "svg[viewBox='0 0 10.126 10.313']"))
    )
    print("Promotional banner found. Closing...")
    banner_close_button.click()
    print("Promotional banner closed successfully.")
except Exception as e:
    print(f"Failed to close promotional banner: {e}")

# Function to scroll down and load more products
def load_more_products(driver):
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

# Load more products to ensure we have at least 10
load_more_products(driver)

# Find the product elements
product_elements = driver.find_elements(By.CLASS_NAME, "product-card")

# Retry loading more products if less than 10 are retrieved
retry_count = 0
while len(product_elements) < 10 and retry_count < 3:
    load_more_products(driver)
    product_elements = driver.find_elements(By.CLASS_NAME, "product-card")
    retry_count += 1

# Limit to the first 10 products
product_elements = product_elements[:10]

# List to hold product information
products = []

# Iterate over the first 10 product elements
for idx, product in enumerate(product_elements, start=1):
    product_info = {}
    try:
        product_name = product.find_element(By.CSS_SELECTOR, "a > div.category-page-ozrboz").text
    except Exception as e:
        product_name = "N/A"
        print(f"Failed to retrieve product name: {e}")
    product_info["Position"] = idx
    product_info["Product Name"] = product_name
    
    try:
        # Try to find the price element
        price_element = product.find_element(By.CSS_SELECTOR, ".product-price__highlight, .product-price__markdown > span, span:not([class])")
        product_price = price_element.text
        product_info["Price"] = product_price
    except NoSuchElementException:
        product_info["Price"] = "N/A"
        print("Failed to retrieve price information.")
    
    try:
        # Find the discount price within the markdown section if available
        try:
            discounted_price_element = product.find_element(By.CSS_SELECTOR, ".product-price__markdown .product-price__strike")
            discounted_price = discounted_price_element.text
        except NoSuchElementException:
            discounted_price = "N/A"
        
        if discounted_price == "N/A":
            try:
                # If no strike element, try finding any highlighted discount
                highlighted_discounted_price_element = product.find_element(By.CSS_SELECTOR, ".product-price__highlight")
                discounted_price = highlighted_discounted_price_element.text
            except NoSuchElementException:
                discounted_price = "N/A"
        
        product_info["Discounted Price"] = discounted_price
    except NoSuchElementException:
        product_info["Discounted Price"] = "N/A"
        print("Failed to retrieve discounted price information.")
    
    products.append(product_info)

# Close the browser
driver.quit()

# Convert the list of dictionaries to a pandas DataFrame
df = pd.DataFrame(products)

# Save the DataFrame to an Excel file

df.to_excel("gap_products1.xlsx", index=False)

print("Data has been successfully scraped and saved to 'gap_products.xlsx'")
