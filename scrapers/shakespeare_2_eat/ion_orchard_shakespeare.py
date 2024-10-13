import json
import os
import re
from playwright.sync_api import sync_playwright

def delete_file(target_url):
    """
    Helper function that attempts to 
    delete a file at the specified url.
    """
    try:
        os.remove(target_url)
        print(f"Deleted file at filepath: {target_url}")
    except OSError as e:
        print(f"Error deleting file at filepath: {target_url} due to {e}")

def clean_string(input_string):
    """
    Sanitizes a provided string.
    """
    cleaned_string = re.sub(r'\n+', ' ', input_string)
    cleaned_string = re.sub(r'<[^>]+>', '', cleaned_string)
    return cleaned_string.strip()

def scrape_ion_orchard(base_urls):
    """
    Scrapes the specified Ion Orchard 
    websites for the food vendor's name,
    location, description, category, and URL.
    """
    details_list = []
    errors = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        for base_url in base_urls:
            page_num = 1
            while True:
                url = f"{base_url}&page={page_num}"
                try:
                    page.goto(url)
                    page.wait_for_selector('div.cmp-dynamic-list-dine-shop-grid-item')
                    listings = page.query_selector_all('div.cmp-dynamic-list-dine-shop-grid-item')
                    if not listings:
                        errors.append("No more listings found.")
                        break
                    for listing in listings:
                        # details = listing.query_selector('div.cmp-dynamic-list-dine-shop-item-content-info').inner_text()
                        name = listing.query_selector('div.cmp-dynamic-list-dine-shop-item-content-info div.cmp-dynamic-list-dine-shop-item-content-info span.cmp-dynamic-list-dine-shop-item-content-item-title').inner_text().strip()
                        raw_location = listing.query_selector('div.cmp-dynamic-list-dine-shop-item-content-info div.cmp-dynamic-list-dine-shop-item-content-info span.cmp-dynamic-list-dine-shop-item-content-item-num').inner_text().strip()
                        clean_location = clean_string(raw_location.inner_text().strip() if raw_location else '')
                        print(name)
                        print(clean_location)
                        description = "" 
                        category = ""
                        vendor_url = base_url 
                        details = {
                            'name': name,
                            'location': clean_location,
                            'description': description,
                            'category': category,
                            'url': vendor_url
                        }
                        details_list.append(details)

                    # Check for next page
                    next_page = page.query_selector('div.cmp-dynamic-list-pagination-container span.cmp-dynamic-list-paginate-item.active')
                    if next_page:
                        page_num += 1
                    else:
                        break 

                except Exception as e:
                    errors.append(f"Error processing {url}: {e}")
                    break 

        browser.close() 
    return details_list, errors

# ----- Execution Code -----

BASE_URLS = [
    "https://www.ionorchard.com/en/dine.html?category=Casual%20Dining%20and%20Takeaways",
    "https://www.ionorchard.com/en/dine.html?category=Restaurants%20and%20Cafes"
]
TARGET_FILEPATH = "./../output/ion_orchard_dining_details.json"

details_list, errors = scrape_ion_orchard(BASE_URLS)
if errors:
    print(f"Errors encountered: {errors}")
print("Scraping complete.")
delete_file(TARGET_FILEPATH)
with open(TARGET_FILEPATH, 'w') as f:
    json.dump(details_list, f, indent=4)