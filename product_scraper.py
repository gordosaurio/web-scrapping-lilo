import os
import time
from selenium.webdriver.common.by import By

from popup_handler import close_popup_if_exists
from utils import extract_text, extract_attribute, extract_number, sanitize_filename
from download import download_image

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
