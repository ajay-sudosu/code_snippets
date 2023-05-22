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

#click on 9th invoice link and open first page
driver.find_element_by_link_text('9197694715').click()

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


with open(r"C:\Users\Kajal\Downloads\quest_dispute.csv", newline='') as g:
    ereader2 = csv.DictReader(g)
    for row in ereader2:
        csv_file2 = row['Service Code'],row['Price']
        list5.append(csv_file2)

# missing elements of invoice link page number 1
for i in list4:
    if i not in list5:
        print('page no =1, invoice link 9',i)

driver.find_element_by_xpath("/html/body/table[9]/tbody/tr[1]/td/table/tbody/tr[124]/td[9]/div/input").click()
time.sleep(1)

# click on Dispute Lines.
driver.find_element_by_xpath("/html/body/table[9]/tbody/tr[2]/td/table/tbody/tr/td[14]/a/img").click()

#click on pricing Button
driver.find_element_by_xpath("/html/body/table[8]/tbody/tr/td[1]/table/tbody/tr/td/div/form/table/tbody/tr/td[2]/select/option[7]").click()

# Click on Ok button
driver.find_element_by_xpath("/html/body/table[13]/tbody/tr/td[3]/div/a[2]/img").click()


# 2nd page
next_page = driver.find_element_by_xpath("//option[@value='2']")
next_page.click()

# click on page limit
driver.find_element_by_xpath("//option[@value='125']").click()

#get all prices of page no 2
all_prices = driver.find_elements_by_xpath("//td[@style='padding-right:12px;']")
list1 = []
for i in all_prices:
    if i.text != '':
        # print(i.text)
        list1.append(i.text)


# get all service codes of page no 2
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

# missing elements of invoice link page number 2
for i in list4:
    if i not in list5:
        print('page no =2, invoice link 9',i)


driver.find_element_by_xpath("/html/body/table[9]/tbody/tr[1]/td/table/tbody/tr[102]/td[9]/div/input").click()
time.sleep(1)
driver.find_element_by_xpath("/html/body/table[9]/tbody/tr[1]/td/table/tbody/tr[104]/td[9]/div/input").click()
time.sleep(1)
driver.find_element_by_xpath("/html/body/table[9]/tbody/tr[1]/td/table/tbody/tr[122]/td[9]/div/input").click()
time.sleep(1)
driver.find_element_by_xpath("/html/body/table[9]/tbody/tr[1]/td/table/tbody/tr[144]/td[9]/div/input").click()
time.sleep(1)
driver.find_element_by_xpath("/html/body/table[9]/tbody/tr[1]/td/table/tbody/tr[146]/td[9]/div/input").click()
time.sleep(1)
driver.find_element_by_xpath("/html/body/table[9]/tbody/tr[1]/td/table/tbody/tr[180]/td[9]/div/input").click()
time.sleep(1)
driver.find_element_by_xpath("/html/body/table[9]/tbody/tr[1]/td/table/tbody/tr[182]/td[9]/div/input").click()
time.sleep(1)
driver.find_element_by_xpath("/html/body/table[9]/tbody/tr[1]/td/table/tbody/tr[182]/td[9]/div/input").click()
time.sleep(1)


# click on Dispute Lines.
driver.find_element_by_xpath("/html/body/table[9]/tbody/tr[2]/td/table/tbody/tr/td[15]/a/img").click()

#click on pricing Button
driver.find_element_by_xpath("/html/body/table[8]/tbody/tr/td[1]/table/tbody/tr/td/div/form/table/tbody/tr/td[2]/select/option[7]").click()

# Click on Ok button
driver.find_element_by_xpath("/html/body/table[13]/tbody/tr/td[3]/div/a[2]/img").click()


# 3nd page
next_page = driver.find_element_by_xpath("//option[@value='3']")
next_page.click()

# click on page limit
driver.find_element_by_xpath("//option[@value='125']").click()

#get all prices of page no 3
all_prices = driver.find_elements_by_xpath("//td[@style='padding-right:12px;']")
list1 = []
for i in all_prices:
    if i.text != '':
        # print(i.text)
        list1.append(i.text)


# get all service codes of page no 3
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

# missing elements of invoice link page number 3
for i in list4:
    if i not in list5:
        print('page no =3, invoice link 9',i)


driver.find_element_by_xpath("/html/body/table[9]/tbody/tr[1]/td/table/tbody/tr[56]/td[9]/div/input").click()
time.sleep(1)
driver.find_element_by_xpath("/html/body/table[9]/tbody/tr[1]/td/table/tbody/tr[98]/td[9]/div/input").click()
time.sleep(1)
driver.find_element_by_xpath("/html/body/table[9]/tbody/tr[1]/td/table/tbody/tr[198]/td[9]/div/input").click()
time.sleep(1)

# click on Dispute Lines.
driver.find_element_by_xpath("/html/body/table[9]/tbody/tr[2]/td/table/tbody/tr/td[13]/a/img").click()

#click on pricing Button
driver.find_element_by_xpath("/html/body/table[8]/tbody/tr/td[1]/table/tbody/tr/td/div/form/table/tbody/tr/td[2]/select/option[7]").click()

# Click on Ok button
driver.find_element_by_xpath("/html/body/table[13]/tbody/tr/td[3]/div/a[2]/img").click()



