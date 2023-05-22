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

first_page = driver.find_element_by_xpath("//option[@value='1']")

second_page = driver.find_element_by_xpath("//option[@value='2']")

third_page = driver.find_element_by_xpath("//option[@value='3']")

#click on 29th invoice link and open first page
# driver.find_element_by_link_text('9196322366').click()

data = driver.find_elements_by_xpath("//*[contains(text(),'919')]")
for i in data:
    print('data',i.text)
    # invoice = driver.find_element_by_link_text('9196352190').is_displayed()
    if i.text == '9196022750':
        driver.find_element_by_link_text('9196022750').click()
        # click on page limit
        driver.find_element_by_xpath("//option[@value='125']").click()


        # logic here



        # click on Dispute Lines.
        driver.find_element_by_xpath("/html/body/table[9]/tbody/tr[2]/td/table/tbody/tr/td[7]/a/img").click()

        #click on pricing Button
        driver.find_element_by_xpath("/html/body/table[8]/tbody/tr/td[1]/table/tbody/tr/td/div/form/table/tbody/tr/td[2]/select/option[7]").click()

        # Click on Ok button
        driver.find_element_by_xpath("/html/body/table[13]/tbody/tr/td[3]/div/a[2]/img").click()

        driver.close()



second_page.click()
data1 = driver.find_elements_by_xpath("//*[contains(text(),'919')]")
for i in data1:
    if i.text == '9195954070':
        driver.find_element_by_link_text('9195954070').click()
        # click on page limit
        driver.find_element_by_xpath("//option[@value='125']").click()


        # logic here



        # click on Dispute Lines.
        driver.find_element_by_xpath("/html/body/table[9]/tbody/tr[2]/td/table/tbody/tr/td[7]/a/img").click()

        #click on pricing Button
        driver.find_element_by_xpath("/html/body/table[8]/tbody/tr/td[1]/table/tbody/tr/td/div/form/table/tbody/tr/td[2]/select/option[7]").click()

        # Click on Ok button
        driver.find_element_by_xpath("/html/body/table[13]/tbody/tr/td[3]/div/a[2]/img").click()

        driver.close()

        
        
    
# Go to 3rd page    
third_page = driver.find_element_by_xpath("//option[@value='3']")
third_page.click()


data1 = driver.find_elements_by_xpath("//*[contains(text(),'919')]")
for i in data1:
    if i.text == '9196022750':
        driver.find_element_by_link_text('9196022750').click()
        # click on page limit
        driver.find_element_by_xpath("//option[@value='125']").click()


        # logic here



        # click on Dispute Lines.
        driver.find_element_by_xpath("/html/body/table[9]/tbody/tr[2]/td/table/tbody/tr/td[7]/a/img").click()

        #click on pricing Button
        driver.find_element_by_xpath("/html/body/table[8]/tbody/tr/td[1]/table/tbody/tr/td/div/form/table/tbody/tr/td[2]/select/option[7]").click()

        # Click on Ok button
        driver.find_element_by_xpath("/html/body/table[13]/tbody/tr/td[3]/div/a[2]/img").click()

        driver.close()










