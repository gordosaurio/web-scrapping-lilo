import time
import re
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def close_popup_if_exists(driver):
    try:
        button_close = WebDriverWait(driver, 2).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="topOfPage"]/div[16]/div/div[2]/div/div/div/div/div/button'))
        )
        button_close.click()
        time.sleep(1)
        WebDriverWait(driver, 5).until(
            EC.invisibility_of_element_located((By.XPATH, '//*[@id="topOfPage"]/div[16]/div/div[2]/div/div/div/div/div'))
        )
    except TimeoutException:
        pass


try:
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")

    driver = webdriver.Chrome(options=chrome_options)

    url = 'https://prima-coffee.com/brew/coffee'
    driver.get(url)
    time.sleep(5)

    data = []
    current_page = 1

    while True:
        close_popup_if_exists(driver)

        container = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="topOfPage"]/div[6]/div/div[1]/main/div/div[3]/div[2]'))
        )

        products = container.find_elements(By.XPATH, './/a[contains(@class, "product")]')

        for product in products:
            try:
                title = product.find_element(By.XPATH, './/h4/a').text.strip()
            except:
                title = ''

            try:
                url = product.get_attribute('href')
            except:
                url = ''

            try:
                price_block = product.text
            except:
                price_block = ''

            prices_found = re.findall(r'\$\s*[\d,]+(?:\.\d{2})?', price_block)
            prices_found = [float(p.replace('$', '').replace(',', '').strip()) for p in prices_found]

            price = ''
            if prices_found:
                price = str(min(prices_found))

            data.append({
                'title': title,
                'url': url,
                'price': price
            })

        print(f"Page {current_page}: {len(products)} products found. Total products collected: {len(data)}")

        try:
            next_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//a[contains(@class, 'ns-next') and @aria-label='Next']"))
            )
            next_class = next_button.get_attribute('class').lower()
            if 'disabled' in next_class:
                break

            close_popup_if_exists(driver)

            time.sleep(1)
            next_button.click()
            current_page += 1
            time.sleep(5)
        except (TimeoutException, NoSuchElementException, ElementClickInterceptedException):
            break

    df = pd.DataFrame(data)
    df.to_csv('prima_coffee_products.csv', index=False, encoding='utf-8-sig')

    print(f"Scraping complete. Total products extracted: {len(data)}")

except Exception as err:
    print(f"Error detected: {err}")
finally:
    try:
        driver.quit()
    except:
        pass
