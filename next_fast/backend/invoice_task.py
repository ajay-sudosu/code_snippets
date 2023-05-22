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


# click on first invoice link 
driver.find_element_by_xpath("/html/body/table[7]/tbody/tr[1]/td/table/tbody/tr[2]/td[5]/a").click()

# page limit
driver.find_element_by_xpath('/html/body/table[9]/tbody/tr[2]/td/table/tbody/tr/td[4]/select/option[5]').click()

# service = driver.find_elements_by_xpath("//td[@width='46%']")

time.sleep(1)

#get all prices
all_prices = driver.find_elements_by_xpath("//td[@style='padding-right:12px;']")
list1 = []
for i in all_prices:
    # print(i.text)
    if i.text != '':
        # print(i.text)
        list1.append(i.text)

# print(len(list1))
# get all service codes
all_services = driver.find_elements_by_xpath("//*[@style='padding-left:3px;' and @width='20%']")
list2 = []
for i in all_services:
    # print(i.text)
    list2.append(i.text)
# print(len(list2))

list_dict = {'Service Code':list1, 'Price':list2} 
df = pd.DataFrame(list_dict) 
df.to_csv('example.csv', index=False) 
# print(df)

list4 = []
list5 = []
with open(r"example.csv", newline='') as f:
    ereader1 = csv.DictReader(f)
    for row in ereader1:
        csv_file1 = row['Price'],row['Service Code']
        list4.append(csv_file1)

# print('list4',list4)
with open(r"C:\Users\Kajal\Downloads\quest_dispute.csv", newline='') as g:
    ereader2 = csv.DictReader(g)
    for row in ereader2:
        csv_file2 = row['Service Code'],row['Price']
        list5.append(csv_file2)

# print('list5',list5)

# missing elements of invoice link page number 1
for i in list4:
    if i not in list5:
        print('page no = 1, invoice link 1',i)

# time.sleep(2)

# first page invoice no 1 checkbox selected
# td_elements = driver.find_element_by_xpath("/html/body/table[9]/tbody/tr[1]/td/table/tbody/tr[124]/td[9]/div")
# td_elements.click()

time.sleep(1)

# go back invoices page one
driver.find_element_by_xpath("//a[@class='navOn']").click()

#click on 4th invoice link and open first page
driver.find_element_by_xpath("/html/body/table[7]/tbody/tr[1]/td/table/tbody/tr[8]/td[5]/a").click()

# click on page limit
driver.find_element_by_xpath("//option[@value='125']").click()

#get all prices of page no 1
all_prices = driver.find_elements_by_xpath("//td[@style='padding-right:12px;']")
list1 = []
for i in all_prices:
    if i.text != '':
        # print(i.text)
        list1.append(i.text)

# print(len(list1))

# get all service codes of page no 1
all_services = driver.find_elements_by_xpath("//*[@style='padding-left:3px;' and @width='20%']")
list2 = []
for i in all_services:
    # print(i.text)
    list2.append(i.text)
# print(len(list2))

list_dict = {'Service Code':list1, 'Price':list2} 
df = pd.DataFrame(list_dict) 
df.to_csv('example.csv', index=False) 
# print(df)

list4 = []
list5 = []
with open(r"example.csv", newline='') as f:
    ereader1 = csv.DictReader(f)
    for row in ereader1:
        csv_file1 = row['Price'],row['Service Code']
        list4.append(csv_file1)


# print('list4',list4)
with open(r"C:\Users\Kajal\Downloads\quest_dispute.csv", newline='') as g:
    ereader2 = csv.DictReader(g)
    for row in ereader2:
        csv_file2 = row['Service Code'],row['Price']
        list5.append(csv_file2)

# print('list5',list5)

# missing elements of invoice link page number 1
for i in list4:
    if i not in list5:
        print('page no  = 1, invoice_no = 4',i)

# first page invoice no 4 checkbox selected
driver.find_element_by_xpath("/html/body/table[9]/tbody/tr[1]/td/table/tbody/tr[56]/td[9]/div/input").click()
time.sleep(2)

# go back invoices page one
driver.find_element_by_xpath("//a[@class='navOn']").click()


#click on 5th invoice link and open first page
driver.find_element_by_xpath("/html/body/table[7]/tbody/tr[1]/td/table/tbody/tr[10]/td[5]/a").click()

# click on page limit
driver.find_element_by_xpath("//option[@value='125']").click()

#get all prices of page no 1
all_prices = driver.find_elements_by_xpath("//td[@style='padding-right:12px;']")
list1 = []
for i in all_prices:
    if i.text != '':
        # print(i.text)
        list1.append(i.text)

# print(len(list1))

# get all service codes of page no 1
all_services = driver.find_elements_by_xpath("//*[@style='padding-left:3px;' and @width='20%']")
list2 = []
for i in all_services:
    # print(i.text)
    list2.append(i.text)
# print(len(list2))

list_dict = {'Service Code':list1, 'Price':list2} 
df = pd.DataFrame(list_dict) 
df.to_csv('example.csv', index=False) 
# print(df)

list4 = []
list5 = []
with open(r"example.csv", newline='') as f:
    ereader1 = csv.DictReader(f)
    for row in ereader1:
        csv_file1 = row['Price'],row['Service Code']
        list4.append(csv_file1)


# print('list4',list4)
with open(r"C:\Users\Kajal\Downloads\quest_dispute.csv", newline='') as g:
    ereader2 = csv.DictReader(g)
    for row in ereader2:
        csv_file2 = row['Service Code'],row['Price']
        list5.append(csv_file2)

# print('list5',list5)

# missing elements of invoice link 5 and page number 1
for i in list4:
    if i not in list5:
        print('page no  = 1, invoice_no = 5',i)


driver.find_element_by_xpath("/html/body/table[9]/tbody/tr[1]/td/table/tbody/tr[204]/td[9]/div/input").click()






# driver.find_element_by_xpath("/html/body/table[9]/tbody/tr[2]/td/table/tbody/tr/td[12]/a").click()
# driver.find_element_by_xpath("/html/body/table[9]/tbody/tr[1]/td/table/tbody/tr[88]/td[9]/div/input").click()

# ------------------------------------------------------------------------------------
# search for a tag for downloading CSVS
# csv_files = driver.find_elements_by_tag_name("a")
# for i in csv_files:
#     if i.text == 'CSV':
#         i.click()

# # Go to 2nd page    
# second_page = driver.find_element_by_xpath("//option[@value='2']")
# second_page.click()

# # Set page limit
# driver.find_element_by_xpath("/html/body/table[7]/tbody/tr[2]/td/table[1]/tbody/tr/td[4]/select/option[5]").click()

# # Go to 2nd page    
# second_page = driver.find_element_by_xpath("//option[@value='2']")
# second_page.click()
# time.sleep(3)

# # search for a tag for downloading CSVS
# csv_files = driver.find_elements_by_tag_name("a")
# for i in csv_files:
#     if i.text == 'CSV':
#         i.click()

# # Go to 3rd page    
# third_page = driver.find_element_by_xpath("//option[@value='3']")
# third_page.click()

# # Set page limit
# driver.find_element_by_xpath("/html/body/table[7]/tbody/tr[2]/td/table[1]/tbody/tr/td[4]/select/option[5]").click()

# # Go to 3rd page    
# third_page = driver.find_element_by_xpath("//option[@value='3']")
# third_page.click()
# time.sleep(3)

# csv_files = driver.find_elements_by_tag_name("a")
# for i in csv_files:
#     if i.text == 'CSV':
#         i.click()
#--------------------------------------------------------------------------------------






# list1 = []
# list2 = []
# with open(r"C:\Users\Kajal\Downloads\quest_dispute.csv", newline='') as f:
#     ereader1 = csv.DictReader(f)
#     for row in ereader1:
#         csv_file1 = row['Service Code'],row['Price']
#         list1.append(csv_file1)
#         csvvv = row['Price']

# with open(r"C:\Users\Kajal\Downloads\invoice (1).csv", newline='') as g:
#     ereader2 = csv.DictReader(g)
#     for row in ereader2:
#         csv_file2 = row['Service Code'],row['Price']
#         list2.append(csv_file2)

# for i in list2:
#     if i not in list1:
#         print(i)








