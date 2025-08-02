import os
import time
import pandas as pd

from driver_setup import init_driver
from listing_scraper import scrape_listing_page, click_next_page
from product_scraper import scrape_product_detail


def main():
    driver = init_driver()
    base_url = "https://prima-coffee.com/brew/coffee"
    driver.get(base_url)
    time.sleep(5)

    all_products = []
    page_number = 1

    while True:
        print(f"Scraping page {page_number}")
        products_data = scrape_listing_page(driver)
        all_products.extend(products_data)
        print(f"Page {page_number} scraped: {len(products_data)} products found, total collected: {len(all_products)}")

        try:
            if not click_next_page(driver):
                break
            page_number += 1
        except Exception as e:
            print(f"Could not advance to next page: {e}")
            break

    csv_folder = "csv"
    if not os.path.exists(csv_folder):
        os.makedirs(csv_folder)

    df = pd.DataFrame(all_products)
    df = df.sort_values(by="price", ascending=True, na_position="last")
    df.to_csv(os.path.join(csv_folder, "prima_coffee_products.csv"), index=False, encoding="utf-8-sig")
    print(f"Listing scraping complete: {len(all_products)} products collected.")

    detailed_data_list = []
    images_directory = "product_images"
    top_five = df.head(5)

    for idx, product_row in enumerate(top_five.itertuples(), 1):
        print(f"Scraping details for product {idx}: {product_row.title}")
        product_details = scrape_product_detail(driver, product_row.url, images_directory)
        detailed_data_list.append(product_details)

    detailed_df = pd.DataFrame(
        detailed_data_list,
        columns=[
            'title', 'url', 'price', 'reviews', 'stars',
            'sku', 'upc', 'mpn', 'condition', 'description', 'image'
        ]
    )
    detailed_df.to_csv(os.path.join(csv_folder, "prima_coffee_top5_detailed.csv"), index=False, encoding="utf-8-sig")
    print("Detailed scraping complete for top 5 products.")
    driver.quit()


if __name__ == "__main__":
    main()
