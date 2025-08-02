import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

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
