from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from pathlib import Path
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import ActionChains
import time

BASE_DIR = Path(__file__).resolve().parent

chrome_path = f"{BASE_DIR}/chromedriver.exe"
chrome_options = Options()
chrome_service = Service(executable_path=chrome_path)
driver = webdriver.Chrome(options=chrome_options, service=chrome_service)
driver.maximize_window()

try:
    driver.get(url='https://www.amazon.com/')
    driver.implicitly_wait(5)
    # get all cookies.
    cookies_list = driver.get_cookies()
    print('Total cookies.', len(cookies_list))

    # adding a cookie
    cookie_to_add = {"name": "my_cookie", "value": "test_cookie"}
    driver.add_cookie(cookie_to_add)
    cookies_after_adding_new = len(driver.get_cookies())
    print('Total cookies after adding new one.', cookies_after_adding_new)

    # deleting a cookie
    driver.delete_cookie(name="my_cookie")
    print('Total cookies after deleting.', len(driver.get_cookies()))

    driver.quit()
except Exception as e_:
    print(e_)
