import os
import time
import re
import requests
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import (
    TimeoutException, NoSuchElementException, ElementClickInterceptedException
)
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def init_driver():
    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-popup-blocking")
    driver = webdriver.Chrome(options=options)
    driver.set_page_load_timeout(30)
    return driver

def close_popup_if_exists(driver):
    try:
        close_button = WebDriverWait(driver, 2).until(
            EC.element_to_be_clickable(
                (By.XPATH, '//*[@id="topOfPage"]/div[16]/div/div[2]/div/div/div/div/div/button')
            )
        )
        close_button.click()
        time.sleep(0.8)
        WebDriverWait(driver, 5).until(
            EC.invisibility_of_element_located(
                (By.XPATH, '//*[@id="topOfPage"]/div[16]/div/div[2]/div/div/div/div/div')
            )
        )
        print("Popup closed.")
    except TimeoutException:
        print("No popup found.")

def sanitize_filename(name):
    return "".join(c for c in name if c.isalnum() or c in (' ', '-', '_')).rstrip().replace(" ", "_")

def download_image(image_url, folder, filename):
    if not os.path.exists(folder):
        os.makedirs(folder)
    try:
        response = requests.get(image_url, timeout=10)
        if response.status_code == 200:
            filepath = os.path.join(folder, filename)
            with open(filepath, "wb") as f:
                f.write(response.content)
            return filepath
    except Exception:
        pass
    return None

def extract_text(driver, xpath):
    try:
        element = driver.find_element(By.XPATH, xpath)
        return " ".join(element.text.strip().split())
    except NoSuchElementException:
        return "N/A"

def extract_attribute(driver, xpath, attribute):
    try:
        element = driver.find_element(By.XPATH, xpath)
        val = element.get_attribute(attribute)
        return val if val else "N/A"
    except NoSuchElementException:
        return "N/A"

def extract_number(text, default="N/A"):
    match = re.search(r'(\d+(?:\.\d+)?)', text)
    return match.group(1) if match else default

def scrape_listing_page(driver):
    close_popup_if_exists(driver)
    container_xpath = '//*[@id="topOfPage"]/div[6]/div/div[1]/main/div/div[3]/div[2]'
    container = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, container_xpath))
    )
    products = container.find_elements(By.XPATH, './/a[contains(@class, "product")]')
    listing_data = []
    for product in products:
        try:
            title = product.find_element(By.XPATH, './/h4/a').text.strip()
        except Exception:
            title = ''
        try:
            url = product.get_attribute('href')
        except Exception:
            url = ''
        try:
            price_text = product.text
        except Exception:
            price_text = ''
        prices = re.findall(r'\$\s*([\d,]+(?:\.\d{2})?)', price_text)
        prices = [float(p.replace(',', '').strip()) for p in prices]
        price = min(prices) if prices else ''
        listing_data.append({"title": title, "url": url, "price": price})
    return listing_data

def click_next_page(driver):
    next_button_xpath = "//a[contains(@class, 'ns-next') and @aria-label='Next']"
    next_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, next_button_xpath))
    )
    classes = next_button.get_attribute('class').lower()
    if "disabled" in classes:
        return False
    close_popup_if_exists(driver)
    time.sleep(0.8)
    next_button.click()
    time.sleep(3)
    return True

def scrape_product_detail(driver, url, images_folder):
    driver.get(url)
    time.sleep(3)
    close_popup_if_exists(driver)

    def safe_text(xpath):
        return extract_text(driver, xpath)

    def safe_attr(xpath, attr):
        return extract_attribute(driver, xpath, attr)

    title = safe_text('//h1[contains(@class, "productView-title") and @itemprop="name"]')

    reviews_text = safe_text('//button[contains(@class, "yotpo-sr-bottom-line-button")]//span[contains(@class, "yotpo-sr-bottom-line-text")]')
    if reviews_text == "N/A":
        try:
            btn = driver.find_element(By.XPATH, '//button[contains(@class, "yotpo-sr-bottom-line-button")]')
            aria_label = btn.get_attribute('aria-label') or ''
            reviews_text = extract_number(aria_label)
        except Exception:
            reviews_text = "N/A"
    else:
        reviews_text = extract_number(reviews_text)

    stars_text = "N/A"
    try:
        btn = driver.find_element(By.XPATH, '//button[contains(@class, "yotpo-sr-bottom-line-button")]')
        aria_label = btn.get_attribute('aria-label') or ''
        stars_text = extract_number(aria_label)
    except Exception:
        pass

    price_raw = safe_text('//span[contains(@class, "price--withoutTax") and contains(@class,"price--main")]')
    if price_raw == "N/A":
        price_val = safe_attr('//meta[@itemprop="price"]', 'content')
        currency = safe_attr('//meta[@itemprop="priceCurrency"]', 'content')
        price_val_num = extract_number(price_val)
        if price_val != "N/A" and currency != "N/A":
            price = f"{currency} {price_val_num}"
        else:
            price = "N/A"
    else:
        price_num = extract_number(price_raw)
        price = price_num if price_num != "N/A" else price_raw

    sku = safe_text('//dd[contains(@class, "productView-info-value--sku")]')
    upc = safe_text('//dd[contains(@class, "productView-info-value--upc")]')
    mpn = safe_text('//dd[contains(@class, "productView-info-value--mpn")]')
    condition = safe_text('//dd[contains(@class, "productView-info-value--condition")]')
    description = safe_text('//div[contains(@class,"productView-description")]')
    if description == "N/A":
        description = safe_text('//div[contains(@class,"productView-product")]')
    description = description.replace('\n', ' ').replace('\r', ' ')

    image_url = safe_attr('//li[contains(@class, "productView-imageCarousel-main-item") and contains(@class,"slick-current")]//img', 'src')
    if image_url == "N/A":
        image_url = safe_attr('//meta[@itemprop="image"]', 'content')

    image_filename_base = sanitize_filename(title) or "product_image"
    img_ext = os.path.splitext(image_url)[1].split('?')[0] if image_url != "N/A" else ".jpg"
    image_filename = image_filename_base + img_ext
    image_path = download_image(image_url, images_folder, image_filename) if image_url != "N/A" else "N/A"

    return {
        "title": title,
        "url": url,
        "price": price,
        "reviews": reviews_text,
        "stars": stars_text,
        "sku": sku,
        "upc": upc,
        "mpn": mpn,
        "condition": condition,
        "description": description,
        "image": image_filename if image_path else "N/A"
    }

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

    df = pd.DataFrame(all_products)
    df = df.sort_values(by="price", ascending=True, na_position="last")
    df.to_csv("prima_coffee_products.csv", index=False, encoding="utf-8-sig")
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
    detailed_df.to_csv("prima_coffee_top5_detailed.csv", index=False, encoding="utf-8-sig")
    print("Detailed scraping complete for top 5 products.")
    driver.quit()

if __name__ == "__main__":
    main()
