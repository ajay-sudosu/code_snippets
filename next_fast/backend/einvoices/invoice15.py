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


#click on 15th invoice link and open first page
driver.find_element_by_link_text('9197319116').click()

# click on page limit
driver.find_element_by_xpath("//option[@value='125']").click()


#get all prices of page no 1
all_prices = driver.find_elements_by_xpath("//td[@style='padding-right:12px;']")
list1 = []
for i in all_prices:
    if i.text != '':
        # print(i.text)
        list1.append(i.text)


# get all service codes of page no 1
all_services = driver.find_elements_by_xpath("//*[@style='padding-left:3px;' and @width='20%']")
list2 = []
for i in all_services:
    list2.append(i.text)

list_dict = {'Service Code':list1, 'Price':list2} 
df = pd.DataFrame(list_dict) 
df.to_csv('example.csv', index=False) 

list4 = []
list5 = []
with open(r"example.csv", newline='') as f:
    ereader1 = csv.DictReader(f)
    for row in ereader1:
        csv_file1 = row['Price'],row['Service Code']
        list4.append(csv_file1)


print('list4',list4)
with open(r"C:\Users\Kajal\Downloads\quest_dispute.csv", newline='') as g:
    ereader2 = csv.DictReader(g)
    for row in ereader2:
        csv_file2 = row['Service Code'],row['Price']
        list5.append(csv_file2)

# missing elements of invoice link page number 1.
for i in list4:
    if i not in list5:
        print('page no =1, invoice link 15',i)



driver.find_element_by_xpath("/html/body/table[9]/tbody/tr[1]/td/table/tbody/tr[4]/td[9]/div/input").click()
time.sleep(1)
driver.find_element_by_xpath("/html/body/table[9]/tbody/tr[1]/td/table/tbody/tr[70]/td[9]/div/input").click()
time.sleep(1)
driver.find_element_by_xpath("/html/body/table[9]/tbody/tr[1]/td/table/tbody/tr[70]/td[9]/div/input").click()
time.sleep(1)


# click on Dispute Lines.
driver.find_element_by_xpath("/html/body/table[9]/tbody/tr[2]/td/table/tbody/tr/td[7]/a/img").click()

#click on pricing Button
driver.find_element_by_xpath("/html/body/table[8]/tbody/tr/td[1]/table/tbody/tr/td/div/form/table/tbody/tr/td[2]/select/option[7]").click()

# Click on Ok button
driver.find_element_by_xpath("/html/body/table[13]/tbody/tr/td[3]/div/a[2]/img").click()

