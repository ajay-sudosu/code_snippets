# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.keys import Keys
# from pathlib import Path
# import time
# from selenium.webdriver.support.ui import Select
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
#
# BASE_DIR = Path(__file__).resolve().parent
#
# chrome_path = f"{BASE_DIR}/chromedriver.exe"
# chrome_options = Options()
# chrome_service = Service(executable_path=chrome_path)
# driver = webdriver.Chrome(options=chrome_options, service=chrome_service)
# driver.maximize_window()
#
# try:
#     driver.get(url='https://www.nationsonline.org/oneworld/countries_of_the_world.htm')
#     driver.implicitly_wait(5)
#
#     # scroll down by pixel
#     driver.execute_script("window.scrollBy(0, 1000)")
#     time.sleep(3)
#
#     # scroll down till element is visible.
#     flag = driver.find_element(By.XPATH, '/html/body/div[7]/div/table[3]/tbody/tr[11]/td[2]/a')
#     driver.execute_script("arguments[0].scrollIntoView();", flag)
#     time.sleep(3)
#
#     # scroll down till the page end.
#     driver.execute_script("window.scrollBy(0, document.body.scrollHeight)")
#     time.sleep(3)
#     driver.quit()
# except Exception as e_:
#     print(e_)
