from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from pathlib import Path
import time
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

BASE_DIR = Path(__file__).resolve().parent

chrome_path = f"{BASE_DIR}/chromedriver.exe"
chrome_options = Options()
chrome_service = Service(executable_path=chrome_path)
driver = webdriver.Chrome(options=chrome_options, service=chrome_service)
driver.maximize_window()

try:
    driver.get(url='https://www.globalsqa.com/demo-site/select-dropdown-menu/')
    driver.implicitly_wait(10)
    dropdown_element = driver.find_element(By.XPATH, "//div[@class='single_tab_div resp-tab-content resp-tab-content-active']/p/select")
    dropdown = Select(dropdown_element)
    print(len(dropdown.options))
    all_options = dropdown.options
    by_value = dropdown.select_by_value(value="IND")
    by_text = dropdown.select_by_visible_text(text="Italy")

    #  links
    all_links = driver.find_elements(By.TAG_NAME, 'a')
    print(len(all_links))
    for link in all_links:
        print(link.text)
    driver.find_element(By.LINK_TEXT, 'Home').click()
    time.sleep(30)
    driver.quit()
except Exception as e_:
    print(e_)
