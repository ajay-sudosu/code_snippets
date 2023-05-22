from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from pathlib import Path
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

BASE_DIR = Path(__file__).resolve().parent


chrome_path = f"{BASE_DIR}/chromedriver.exe"
# fox_path = f"{BASE_DIR}/geckodriver.exe"
chrome_options = Options()
# fox_options = FirefoxOptions()

chrome_service = Service(executable_path=chrome_path)

driver = webdriver.Chrome(options=chrome_options, service=chrome_service)
# driver = webdriver.Firefox(options=chrome_options, service=chrome_service)
# driver = webdriver.Firefox()

driver.maximize_window()

try:
    driver.get(url='https://www.roboform.com/filling-test-all-fields')
    driver.implicitly_wait(10)
    driver.find_element(By.NAME, '05_company')
    print('hello')
except Exception as e_:
    print(e_)

