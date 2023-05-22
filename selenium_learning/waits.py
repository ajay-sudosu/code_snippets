from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from pathlib import Path

chrome_options = Options()
BASE_DIR = Path(__file__).resolve().parent
chrome_path = f"{BASE_DIR}/chromedriver"
chrome_service = Service(executable_path=chrome_path)
driver = webdriver.Chrome(options=chrome_options, service=chrome_service)
driver.get("https://www.flipkart.com/mobile-phones-store")
driver.implicitly_wait(10)
driver.quit()
