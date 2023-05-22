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
    driver.get(url='https://demo.automationtesting.in/Windows.html')
    driver.implicitly_wait(5)
    current_window = driver.current_window_handle  # return some id of current window.
    button = driver.find_element(By.XPATH, '//*[@id="Tabbed"]/a/button')
    button.click()
    all_tabs = driver.window_handles # return ids of all open tabs.
    for id in all_tabs:
        driver.switch_to.window(id)
        print(driver.title)
    driver.quit()
except Exception as e_:
    print(e_)
