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
    driver.get(url='https://www.w3schools.com/html/html_iframe.asp')
    driver.implicitly_wait(5)
    driver.switch_to.frame(driver.find_element(By.XPATH, '//*[@id="main"]/div[3]/iframe'))
    html_link = driver.find_element(By.LINK_TEXT, "HTML")
    html_link.click()
    driver.switch_to.default_content()
    next_ele = driver.find_element(By.LINK_TEXT, "Next ❯")
    next_ele.click()
    time.sleep(5)
    driver.quit()
except Exception as e_:
    print(e_)
