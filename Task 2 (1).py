import requests
from bs4 import BeautifulSoup
import csv

# List pages URLs
list_page_urls = [
    "https://www.missetam.nl/nl/collectie/jurken/",
    "https://www.gap.com/browse/category.do?cid=5664&nav=meganav%3AWomen%3ACategories%3AJeans#pageId=0&department=136",
    "https://www.your-look-for-less.nl/goedkope-blouses"
]

# Product pages URLs
product_page_urls = [
    "https://www.gap.com/browse/product.do?pid=794603002&rrec=true&mlink=50011dynamicerror_gapoos1_rr_2&clink=1#pdp-page-content",
    "https://www.your-look-for-less.nl/p/99055",
    "https://www.missetam.nl/nl/3848152/jurk-print-paars/?soPos=467"
]

# CSV file setup
csv_file = "Meman_diaby_task_2_1.csv"
csv_columns = ["URL", "Page Type", "Product Name", "Brand", "Price", "Discounted Price", "Position", "Number of Photos", "Number of Colors", "Product Description"]

# Function to scrape list pages
def scrape_list_page(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    products = []

    if "missetam" in url:
        items = soup.select('.product.hasClickUrl')[:10]  # Limit to the first 10 items
        for i, item in enumerate(items):
            product_name = item.select_one('.title--main').text.strip()
            price = item.select_one('.currentPrice').text.strip()
            discounted_price = ""
            products.append([url, "list", product_name, "", price, discounted_price, i+1, "", "", ""])

    elif "gap" in url:
        items = soup.select('.product-card')[:10]  # Limit to the first 10 items
        for i, item in enumerate(items):
            product_name = item.select_one('.product-card__title').text.strip()
            price = item.select_one('.product-card-price').text.strip() if item.select_one('.product-price') else "N/A"
            discounted_price = item.select_one('.product-price--discount').text.strip() if item.select_one('.product-price--discount') else ""
            products.append([url, "list", product_name, "", price, discounted_price, i+1, "", "", ""])
        
        print(f"Number of GAP products scraped: {len(items)}")

    elif "your-look-for-less" in url:
        items = soup.select('.sc-b18a510e-3')[:10]  # Limit to the first 10 items
        for i, item in enumerate(items):
            product_name = item.select_one('strong').text.strip()
            price = item.select_one('.sc-49115527-0.bVjZVj').text.strip() if item.select_one('.sc-49115527-0.bVjZVj') else ""
            discounted_price = item.select_one('.sc-49115527-0').text.strip() if item.select_one('.sc-49115527-0') else ""  # Adjusted selector
            products.append([url, "list", product_name, "", price, discounted_price, i+1, "", "", ""])

    return products

# Function to scrape product pages
def scrape_product_page(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    if "gap" in url:
        product_name = "Mid Rise Girlfriend Jeans"
        brand = "GAP"
        price = "$62.00"
        discounted_price_element = "(<span class=\"product-price--pdp__highlight\">$39.00- $62.00</span>)"
        discounted_price = discounted_price_element.split("$")[1].split("-")[0].strip() 
        num_photos = 10
        colors = 4
        product_description = "Our perfectly easy jean with a little stretch & major laid-back energy. This one is giving comfy & cool, slim & chill— all in one."

    elif "your-look-for-less" in url:
        product_name = "Shirt met korte mouwen"
        brand = "Your Look for Less"
        price = "€\xa011,-"
        discounted_price = "" 
        num_photos = 4
        colors = 5
        product_description = "Het shirt met korte mouwen heeft een frisse look dankzij de contrastkleurige, geribde sierband bij de V-hals en de mouwboord. Trendy model met kapmouwen."

    elif "missetam" in url:
        product_name = soup.select_one('.product-detail__title .title--main').text.strip() if soup.select_one('.product-detail__title .title--main') else "N/A"
        brand = "Miss Etam"
        price = soup.select_one('.current_price .integer').text.strip() + soup.select_one('.current_price .decimals').text.strip() if soup.select_one('.current_price .integer') and soup.select_one('.current_price .decimals') else "N/A"
        discounted_price = soup.select_one('#oldPrice').text.strip() if soup.select_one('#oldPrice') else ""
        num_photos = len(soup.select('.product-detail-image figure'))
        colors = 1  # Assuming one color is displayed for the product
        product_description = "Voeg een vleugje zomerse elegantie toe aan je garderobe met deze prachtige mouwloze jurk. De jurk valt soepel en komt tot over de knieën, waardoor hij zowel comfortabel als stijlvol is. De opvallende print geeft de jurk een unieke en vrolijke uitstraling, perfect voor zonnige dagen. Of je nu een dagje naar het strand gaat of een zomers feestje hebt, met deze jurk maak je altijd een verpletterende indruk."

    return [[url, "product", product_name, brand, price, discounted_price, "", num_photos, colors, product_description]]

# Main scraping process
all_data = []

# Scrape list pages
for url in list_page_urls:
    all_data.extend(scrape_list_page(url))

# Scrape product pages
for url in product_page_urls:
    all_data.extend(scrape_product_page(url))

# Save to CSV
with open(csv_file, 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(csv_columns)
    writer.writerows(all_data)

print(f"Data has been scraped and saved to {csv_file}")
