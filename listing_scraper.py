import re
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from popup_handler import close_popup_if_exists

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
    import time
    time.sleep(0.8)
    next_button.click()
    time.sleep(3)
    return True
