from pathlib import Path
import time
import urllib.requestimport Ex
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from email.message import EmailMessage

URL = "https://vahan.parivahan.gov.in/vahan4dashboard/vahan/view/reportview.xhtml"


def common():
    BASE_DIR = Path(__file__).resolve().parent
    chrome_path = f"{BASE_DIR}/chromedriver"
    # fox_path = f"{BASE_DIR}/geckodriver.exe"
    chrome_options = Options()
    # fox_options = FirefoxOptions()
    chrome_service = Service(executable_path=chrome_path)
    driver = webdriver.Chrome(options=chrome_options, service=chrome_service)
    data = 'logo'
    driver.maximize_window()
    wait = WebDriverWait(driver, 10)
    # driver = webdriver.Firefox(options=chrome_options, service=chrome_service)
    # driver = webdriver.Firefox()
    driver.implicitly_wait(10)
    driver.get(url=URL)
    return driver


def get_states(drivers, start=1):
    drivers.find_element(By.XPATH, '//*[@id="j_idt31_label"]').click()
    states = drivers.find_elements(By.XPATH, "//div[@id='j_idt31_panel']/div/ul/li")
    return states[start:]


def get_rto(drivers, start=1):
    drivers.find_element(By.XPATH, '//*[@id="selectedRto"]').click()
    rto_items = drivers.find_elements(By.XPATH, '//*[@id="selectedRto_panel"]/div/ul/li')
    return rto_items[start:]


def get_y_axis_items(drivers, axis=None):
    if not axis:
        drivers.find_element(By.XPATH, '//*[@id="yaxisVar"]').click()
        y_axis_items = drivers.find_elements(By.XPATH, '//div[@id="yaxisVar_panel"]/div/ul/li')
        for item in y_axis_items:
            if item.text == "Maker":
                print('y_axis_items', y_axis_items)
                time.sleep(2)
                item.click()
                break
                # return y_axis_items


def get_x_axis_items(drivers, axis=None, value="Month Wise"):
    if not axis:
        drivers.find_element(By.XPATH, '//*[@id="xaxisVar"]').click()
        x_axis_items = drivers.find_elements(By.XPATH, '//div[@id="xaxisVar_panel"]/div/ul/li')
        for item in x_axis_items:
            if item.text == value:
                time.sleep(2)
                item.click()
                break
                # return x_axis_items


def click_refresh_button(drivers):
    drivers.find_element(By.ID, 'j_idt61').click()


def click_toggle(drivers):
    drivers.find_element(By.XPATH, '//div[@id="filterLayout-toggler"]/span/a/span').click()


try:
    driver = common()
    # get all or single state
    all_states = get_states(driver, start=1)
    for state in all_states:
        state.click()
        time.sleep(3)
        all_rtos = get_rto(driver, start=1)
        time.sleep(3)
        for rto in all_rtos:
            rto.click()
            time.sleep(3)
            get_y_axis_items(driver)
            time.sleep(5)
            get_x_axis_items(driver, value="Month Wise")
            time.sleep(5)
            click_refresh_button(driver)
            click_toggle(driver)

            sidebar_tables = driver.find_elements(By.XPATH, '//div[@id="j_idt67_content"]/div')
            for table in range(0, len(sidebar_tables), 2):
                print(table)
                table_items = driver.find_elements(By.XPATH, f'//div[@id="j_idt67_content"]/div[{table}]/div/div/div/table')
                print(table_items)

            print("here")
    driver.quit()


except Exception as e_:
    print(e_)
