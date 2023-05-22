import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from pathlib import Path
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options


BASE_DIR = Path(__file__).resolve().parent
chromedriver_path = f"{BASE_DIR}/chromedriver"
chrome_service = Service(chromedriver_path)

driver = webdriver.Chrome(options=Options(), service=chrome_service)

# driver.get('https://www.flipkart.com/mobile-phones-store')
driver.get('http://practice.cybertekschool.com/radio_buttons')
print(driver.title)  # returns the title of the page
print(driver.current_url)  # returns the url of the page


# driver.find_element(By.XPATH, '//*[@id="container"]/div/div[3]/div[2]/div[2]/div[1]/div/div/div/div[1]/div/div[1]/div/a/p').click()
# time.sleep(5)

# navigation commands
# new_url = driver.current_url
# driver.get(f"{new_url}")
# print(driver.current_url)
# driver.back()
# print(driver.current_url)
# driver.forward()
# print(driver.current_url)

# conditional commands (returns True or False)
# is_selected is used only for radio and checkbox buttons

blue_radio = driver.find_element(By.XPATH, '//*[@id="blue"]')
print(blue_radio.is_selected())
print(blue_radio.is_displayed())






driver.quit()  # closes all the tabs/ browsers
# driver.close()  # closes one tab at a time (parent tab)




