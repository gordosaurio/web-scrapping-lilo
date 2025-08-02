import re
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

def sanitize_filename(name):
    return "".join(c for c in name if c.isalnum() or c in (' ', '-', '_')).rstrip().replace(" ", "_")

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
