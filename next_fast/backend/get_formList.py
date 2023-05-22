# selenium 4
from re import I
from time import sleep
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from fake_useragent import UserAgent
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.options import Options
import time
from selenium.webdriver.support.ui import Select


options = Options()
ua = UserAgent()
userAgent = ua.random
options.add_argument(f'user-agent={userAgent}')

username = "nextmedical"
password = "2022JoinNext!"
# patient_id_number = "97956611"
# member_id = "03858568"
# street = "10220 W 123rd St S"
# city = "oktaha"
# drug_quantity = 0.75
# drug_days_supply = "28"
# primary_diagnosis = "E66.01"
sex = 1
doctor_name = "MARCJONATHAN SEROTA?"
SCROLL_PAUSE_TIME = 0.5
first_name = "evely"
last_name = "perrella"
dob = "04011974"
zip_code = "08805"
RxBIN = "004336"
RxPCN = "rx7434"
RxGroup = "adv"
member_id = "w209309281"
street = "601 W Union Ave"
find_your_medication = "Ozempic (0.25 or 0.5 MG/DOSE) 2MG/1.5ML pen-injectors"
city = "Bound Brook"
durg_quantity = "0.75"
drug_days_supply = "28"
primary_diagnosis = "E66.01"
patient_id_number = "97956611"
#/html/body/div[1]/div[1]/div/div[2]/div/div[2]/div[2]/button/p

# {
#     "patient_id": "97956611",
#     "first_name": "evely",
#     "last_name": "perrella",
#     "sex": "1",
#     "dob": "04011974",
#     "zip_code": "08805",
#     "RxBIN": "004336",
#     "RxPCN": "rx7434",
#     "RxGroup": "adv",
#     "member_id": "w209309281",
#     "street": "601 W Union Ave",
#     "city": "Bound Brook",
#     "durg_quantity": "0.75",
#     "drug_days_supply": 28,
#     "primary_diagnosis": "E66.01",
#     "find_your_medication": "Ozempic (0.25 or 0.5 MG/DOSE) 2MG/1.5ML pen-injectors",
#     "doctor_name": "MARCJONATHAN_SEROTA"
# }




driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()),options=options)
wait = WebDriverWait(driver, 20)
url = "https://account.covermymeds.com"
driver.get(url)
input_username = wait.until(EC.visibility_of_element_located((By.NAME,"username")))
input_username.send_keys(username)
input_password = wait.until(EC.visibility_of_element_located((By.NAME,"password"))) 
input_password.send_keys(password)
btn_sign_in = wait.until(EC.visibility_of_element_located((By.NAME,"commit"))) 
btn_sign_in.click()
wait.until(EC.visibility_of_element_located((By.ID,"new-request"))).click()

request_medication = wait.until(EC.visibility_of_element_located((By.ID,"s2id_autogen6_search")))
request_medication.send_keys(find_your_medication)
wait.until(EC.visibility_of_element_located((By.ID,"select2-result-label-7"))).click()
patient_fname = wait.until(EC.visibility_of_element_located((By.ID,"patient_fname")))
patient_fname.send_keys(first_name)
patient_lname = wait.until(EC.visibility_of_element_located((By.ID,"patient_lname")))
patient_lname.send_keys(last_name)

if sex == 0:
    driver.find_element(By.XPATH,"//*[@id='male']").click()
elif sex == 1:
    driver.find_element(By.XPATH,"//*[@id='female']").click()
else:
    wait.until(EC.visibility_of_element_located((By.ID,"unspecified"))).click()

patient_dob = wait.until(EC.visibility_of_element_located((By.ID,"patient_dob")))
patient_dob.send_keys(dob)
patient_address_zip = wait.until(EC.visibility_of_element_located((By.ID,"patient_address_zip")))
patient_address_zip.send_keys(zip_code)
time.sleep(4)
driver.execute_script("window.scrollTo(100,document.body.scrollHeight);")
# Wait to load page
time.sleep(SCROLL_PAUSE_TIME)
driver.find_element(By.XPATH,"//*[@id='patient-details']/div[7]/button[2]").click()

time.sleep(6)
driver.find_element(By.ID, "continue-to-insurance-search-button").click()
time.sleep(SCROLL_PAUSE_TIME)

bin = wait.until(EC.visibility_of_element_located((By.ID,"bin")))
bin.send_keys(RxBIN)
pcn = wait.until(EC.visibility_of_element_located((By.ID,"pcn")))
pcn.send_keys(RxPCN)
group_id = wait.until(EC.visibility_of_element_located((By.ID,"group_id")))
group_id.send_keys(RxGroup)
time.sleep(4)
driver.execute_script("window.scrollBy(0,500)")
# Wait to load page
time.sleep(SCROLL_PAUSE_TIME)
all_forms_list = driver.find_elements_by_xpath("//button[@class='button choose-form']")
print("length of all forms list",len(all_forms_list))
for i in range(1,len(all_forms_list)):
    print("Processing request :::::::::", i)
    time.sleep(SCROLL_PAUSE_TIME)

    # check = wait.until(EC.visibility_of_element_located((By.XPATH, "//*[@id='formpick-form-results']/li["+str(i)+"]/div[2]/div/button[2]")))
    # time.sleep(3)
    # ActionChains(driver).move_to_element(check).click().perform()
    # print("2")
    # time.sleep(3)
    all_li = driver.find_element_by_xpath("//*[@id='formpick-form-results']/li["+str(i)+"]/div[2]/div/button[2]")
    print(all_li.text)
    all_li.click()
    patient_id_number = driver.find_element(By.XPATH, "/html/body/div[3]/div[2]/div/div[3]/section[2]/div[1]/div[4]/div[2]/div[1]/div/div/input")
    patient_id_number.send_keys(patient_id_number)
    time.sleep(5)
    patient_address1 = driver.find_element(By.NAME, "patient_address1")
    patient_address1.send_keys(street)
    patient_city = driver.find_element(By.NAME, "patient_city")
    patient_city.send_keys(city)
    drug_quantity = driver.find_element(By.NAME, "drug_quantity")
    drug_quantity.send_keys(drug_quantity)
    select = Select(driver.find_element(By.NAME, "drug_quantity_qualifier"))
    select.select_by_value("C28254")
    days_supply = driver.find_element(By.ID, "answer_text")
    days_supply.send_keys(drug_days_supply)
    icd10 = driver.find_element(By.NAME, "icd10")
    icd10.send_keys("E66.01 - Morbid (severe) obesity due to excess calories")
    address_book = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "#provider-section > header > div.summary > div > div > a > div"))).click()
    # address_book.send_keys("MARCJONATHAN SEROTA?")
    el = driver.find_element(By.XPATH, "//*[@id='provider-section']/header/div[2]/div/div/a/ul")
    for li in el.find_elements_by_tag_name("li"):
            print(li.text)

    selectItem = "MARCJONATHAN SEROTA"
    wait.until(EC.visibility_of_element_located((By.XPATH,"//*[@id='provider-section']/header/div[2]/div/div/a/ul/li[1]/span[1][text()='"+ selectItem +"']"))).click()
    time.sleep(2)

# patient_id_number = "97956611"
# member_id = "03858568"
# street = "10220 W 123rd St S"
# city = "oktaha"
# drug_quantity = 0.75
# drug_days_supply = "28"
# primary_diagnosis = "E66.01"


