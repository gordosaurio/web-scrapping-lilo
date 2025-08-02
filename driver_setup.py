from selenium import webdriver
from selenium.webdriver.chrome.options import Options

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
