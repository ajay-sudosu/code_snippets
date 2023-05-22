# from cProfile import label
from asyncio.log import logger
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import logging
from pydantic import BaseModel
import random
import sys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver import ActionChains
from selenium.common.exceptions import NoSuchElementException
# random_number = random.randint(1, 1)

logger = logging.getLogger('covermymeds')

chromedriver_path = 'C:\\chromedriver.exe'

class CoverMedsPatientFillForm(BaseModel):
    patient_id: str
    first_name: str
    last_name: str
    sex: str
    dob: str
    zip_code: str
    RxBIN: str
    RxPCN: str
    RxGroup: str
    member_id: str
    street: str
    city: str
    durg_quantity: str
    drug_days_supply: int
    primary_diagnosis: str
    find_your_medication: str
    doctor_name: str

class NewCoverMedsPatientFillForm:
    
    def __init__(self):
        logger.debug("Initializing object...")
        chrome_options = Options()
        # chrome_options.add_argument("no-sandbox")
        # chrome_options.add_argument("--disable-extensions")
        # chrome_options.add_argument("--headless")
        # chrome_options.add_argument('--start-maximized')
        # chrome_options.add_argument('--window-size=2560,1440')
        #chrome_options.add_experimental_option('w3c', False)
        self.driver = webdriver.Chrome(options=chrome_options, executable_path=chromedriver_path)
        self.driver.implicitly_wait(10)

    def covermeds(self, order_details):
        logger.debug("CoverMeds Order")
        first_name = order_details.get('first_name')
        last_name = order_details.get('last_name')
        sex = order_details.get("sex")
        dob = order_details.get("dob")
        zip_code = order_details.get("zip_code")
        RxBIN = order_details.get("RxBIN")
        RxPCN = order_details.get("RxPCN")
        RxGroup = order_details.get("RxGroup")
        member_id = order_details.get("member_id")
        street = order_details.get("street")
        city = order_details.get("city")
        durg_quantity = order_details.get("durg_quantity")
        drug_days_supply = order_details.get("drug_days_supply")
        primary_diagnosis = order_details.get("primary_diagnosis")
        find_your_medication = order_details.get("find_your_medication")
        doctor_name = order_details.get("doctor_name")

        self.driver.get("https://account.covermymeds.com/")
        self.driver.maximize_window()
        username = self.driver.find_element_by_name("username")
        password = self.driver.find_element_by_name("password")
        username.send_keys("nextmedical")
        password.send_keys("2022JoinNext!")
        #  Login button
        self.driver.find_element_by_name("commit").click()

        self.driver.find_element_by_xpath("//a[@id='new-request']").click()

        find_medication_button = self.driver.find_element_by_xpath("/html/body/div[5]/div/input")

        find_medication_button.send_keys(find_your_medication)
        time.sleep(2)

        ozempic_button = self.driver.find_element_by_xpath("//*[@id='select2-results-6']/li")

        ozempic_button.click()

        first_name_input = self.driver.find_element_by_xpath("//*[@id='patient_fname']")

        first_name_input.send_keys(first_name)

        last_name_input = self.driver.find_element_by_name("patient_lname")

        last_name_input.send_keys(last_name)

        if sex == "0":
            self.driver.find_element_by_xpath("//*[@id='male']").click()
        elif sex == "1":
            self.driver.find_element_by_xpath("//*[@id='female']").click()
        else:
            self.driver.find_element_by_xpath("//*[@id='unspecified']").click()
        time.sleep(1)

        dob_input = self.driver.find_element_by_name("patient_dob")
        dob_input.send_keys(dob)

        patient_zip_code = self.driver.find_element_by_name("patient_address_zip")
        patient_zip_code.send_keys(zip_code)

        self.driver.find_element_by_xpath("/html/body/div[1]/div[1]/div/div[2]/div/form/div[3]/div[1]/fieldset/div[7]/button[2]").click()
        time.sleep(4)

        #need to add condition here

        RxBIN_button = self.driver.find_element_by_name("bin")
        
        # show_more_forms = self.driver.find_element_by_xpath("//*[@id='show-more-forms']")

        # print('---------------------ssss',self.driver.find_element_by_xpath("//*[@id='show-more-forms']"))
        try:
            if self.driver.find_element_by_xpath("//*[@id='show-more-forms']"):
                # show_more_forms = self.driver.find_element_by_xpath("//*[@id='show-more-forms']")
                self.driver.find_element_by_xpath("//*[@id='show-more-forms']").click()
                time.sleep(2)
                all_forms_list = self.driver.find_elements_by_xpath("//button[@class='button choose-form']")
                print("length of all forms list",len(all_forms_list))
                # for i in range(2,len(all_forms_list)):
                #     print("Processing request :::::::::", i)
                #     all_li = self.driver.find_element_by_xpath("//*[@id='formpick-form-results']/li["+str(i)+"]/div[2]/div/button[2]")
                #     print(all_li.text)
                #     all_li.click()
                   


                # logger.info("Finished")

        except NoSuchElementException:

            RxBIN_button.send_keys(RxBIN)
            time.sleep(4)

            RxPCN_button = self.driver.find_element_by_name("pcn")
            time.sleep(2)

            RxPCN_button.send_keys(RxPCN)
            time.sleep(4)

            RxGroup_button = self.driver.find_element_by_name("group_id")
            time.sleep(2)
            RxGroup_button.send_keys(RxGroup)
            time.sleep(4)

            self.driver.find_element_by_xpath("/html/body/div[1]/div[1]/div/div[2]/div/div[2]/div[2]/ul/li[2]/div[2]/div/button[2]").click()
            time.sleep(2)

    
        
       


def cover_my_meds_fill_form(order_details: CoverMedsPatientFillForm):
    order = NewCoverMedsPatientFillForm()
    covermeds_order = order_details.dict()
    logger.info(f"fil form for covermeds Patient: {covermeds_order}")
    order.covermeds(covermeds_order)


if __name__ == '__main__':
    data = {
    "patient_id": "103498772",
    "first_name": "Ebonie",
    "last_name": "Sampson",
    "sex": "1",
    "dob": "08201979",
    "zip_code": "85711",
    "RxBIN": "004336",
    "RxPCN": "RX7391",
    "RxGroup": "ADV",
    "member_id": "985864208",
    "street": "Home Visit",
    "city": "Newyork ",
    "durg_quantity": "0.75",
    "drug_days_supply": 28,
    "primary_diagnosis": "E66.01",
    "find_your_medication": "Ozempic (0.25 or 0.5 MG/DOSE) 2MG/1.5ML pen-injectors",
    "doctor_name": "MARCJONATHAN_SEROTA"
}
    cover_meds = CoverMedsPatientFillForm(**data)
    cover_my_meds_fill_form(cover_meds)






