# from cProfile import label
from selenium import webdriver
# from selenium.webdriver.common.keys import Keys
import time
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.chrome.options import Options
import pandas as pd
import csv


driver = webdriver.Chrome(executable_path='C:\\Users\\Kajal\\Downloads\\chromedriver_win32 (1)\\chromedriver.exe')
driver.get('https://einvoice.questdiagnostics.com/einv/engine/quest/login')
driver.maximize_window()

username = driver.find_element_by_name("userID")

password = driver.find_element_by_name("password")

username.send_keys("frank.joinnextmed")

password.send_keys("2deMtxeNnioJ!")

# Login button
button_key = driver.find_element_by_class_name("button").click()
time.sleep(1)

# Set page limit
driver.find_element_by_xpath("/html/body/table[7]/tbody/tr[2]/td/table[1]/tbody/tr/td[4]/select/option[5]").click()

# driver.find_element_by_xpath("/html/body/table[9]/tbody/tr[2]/td/table/tbody/tr/td[12]/a").click()
# driver.find_element_by_xpath("/html/body/table[9]/tbody/tr[1]/td/table/tbody/tr[88]/td[9]/div/input").click()

# search for a tag for downloading CSVS
csv_files = driver.find_elements_by_tag_name("a")
for i in csv_files:
    if i.text == 'CSV':
        i.click()

# Go to 2nd page    
second_page = driver.find_element_by_xpath("//option[@value='2']")
second_page.click()

# Set page limit
driver.find_element_by_xpath("/html/body/table[7]/tbody/tr[2]/td/table[1]/tbody/tr/td[4]/select/option[5]").click()

# Go to 2nd page    
second_page = driver.find_element_by_xpath("//option[@value='2']")
second_page.click()
time.sleep(3)

# search for a tag for downloading CSVS
csv_files = driver.find_elements_by_tag_name("a")
for i in csv_files:
    if i.text == 'CSV':
        i.click()

# Go to 3rd page    
third_page = driver.find_element_by_xpath("//option[@value='3']")
third_page.click()

# Set page limit
driver.find_element_by_xpath("/html/body/table[7]/tbody/tr[2]/td/table[1]/tbody/tr/td[4]/select/option[5]").click()

# Go to 3rd page    
third_page = driver.find_element_by_xpath("//option[@value='3']")
third_page.click()
time.sleep(3)

csv_files = driver.find_elements_by_tag_name("a")
for i in csv_files:
    if i.text == 'CSV':
        i.click()




