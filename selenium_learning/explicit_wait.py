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
    driver.get(url='https://www.railyatri.in/')
    driver.implicitly_wait(10)
    # driver.execute_script("document.getElementsById('from_stn_input').value='from_stn_input'")
    # _from = driver.find_element(By.ID, 'from_stn_input')  # from
    _from = driver.find_element(By.ID, 'from_stn_input')
    _from.send_keys('BAREILLY')
    time.sleep(2)
    _from.send_keys(Keys.DOWN)
    _from.send_keys(Keys.ENTER)
    # _from.submit()
    # time.sleep(10)
    _to = driver.find_element(By.ID, 'to_stn_input')  # to
    _to.send_keys('LUCKNOW')
    time.sleep(2)
    _to.send_keys(Keys.DOWN)
    _to.send_keys(Keys.ENTER)
    date = driver.find_element(By.ID, 'datepicker_train')  # date
    date.click()
    date_select = driver.find_element(By.XPATH, '/html/body/div[7]/div[1]/table/tbody/tr[4]/td[5]')
    date_select.click()
    # date.send_keys(Keys.BACKSPACE * 15)
    # date.send_keys('29/11/2022')
    # driver.find_element(By.ID, 'datepicker_train').send_keys('29/11/2022')  # date
    # time.sleep(10)
    driver.find_element(By.ID, 'search_btn_dweb').click()  # search button
    wait = WebDriverWait(driver, 10)

    try:
        wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="ttb_tbs_result"]/div/div/div[1]/div/div/div[2]/label[1]/span[2]'))).click()
        time.sleep(1)
    except Exception:
        wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="ui-panel-12-content"]/div/table/tr/td[1]/label'))).click()
        time.sleep(1)
    driver.quit()
except Exception as e_:
    print(e_)

