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
    driver.get(url='https://www.w3schools.com/html/html_tables.asp')
    driver.implicitly_wait(5)
    rows = len(driver.find_elements(By.XPATH, '//*[@id="customers"]/tbody/tr'))
    columns = len(driver.find_elements(By.XPATH, '//*[@id="customers"]/tbody/tr[1]/th'))
    for r in range(2, rows+1):
        row_ = []
        for c in range(1, columns+1):
            value = driver.find_element(By.XPATH, f'//*[@id="customers"]/tbody/tr[{r}]/td[{c}]').text
            row_.append(value)
        print(row_)
        print()
    a = 10
    driver.quit()
except Exception as e_:
    print(e_)
