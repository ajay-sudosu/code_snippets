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
    """This is for mouse hover."""
    # driver.get(url='https://www.bobology.com/public/What-is-a-Mouse-Over-or-Mouse-Hover.cfm')
    # driver.implicitly_wait(5)
    # departments = driver.find_element(By.XPATH, '//*[@id="mgtoppanel"]/li[2]/a')
    # newsletter = driver.find_element(By.XPATH, '//*[@id="mgtoppanel"]/li[2]/ul')
    # videos = driver.find_element(By.XPATH, '//*[@id="mgtoppanel"]/li[2]/ul/li[3]/a')
    # actions = ActionChains(driver)
    # actions.move_to_element(departments).move_to_element(videos).click().perform()  # Mouse hover.

    """This is for right click."""
    # driver.get(url='https://demo.guru99.com/test/simple_context_menu.html')
    # driver.implicitly_wait(5)
    # element = driver.find_element(By.XPATH, '//*[@id="authentication"]/span')
    # actions = ActionChains(driver)
    # actions.context_click(element).perform()  # Right click.

    """This is for drag and drop."""
    # driver.get(url='http://www.dhtmlgoodies.com/scripts/drag-drop-custom/demo-drag-drop-3.html')
    # driver.implicitly_wait(5)
    # source = driver.find_element(By.XPATH, '//*[@id="box4"]')
    # destination = driver.find_element(By.XPATH, '//*[@id="box104"]')
    # actions = ActionChains(driver)
    # actions.drag_and_drop(source=source, target=destination).perform()  # Drag and drop.
    # time.sleep(10)
    driver.quit()
except Exception as e_:
    print(e_)
