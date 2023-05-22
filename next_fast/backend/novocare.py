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

logger = logging.getLogger('novocare')

chromedriver_path = 'C:\\chromedriver.exe'

class NovoCarePatientFillForm(BaseModel):
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

class NewNovoCarePatientFillForm:
    
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

    def novocare(self, order_details):
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

        self.driver.get("https://www.novocare.com/wegovy/cost-navigator.html")
        self.driver.maximize_window()
        time.sleep(999)


def novo_care_fill_form(order_details: NovoCarePatientFillForm):
    order = NewNovoCarePatientFillForm()
    novocare_order = order_details.dict()
    logger.info(f"fil form for covermeds Patient: {novocare_order}")
    order.novocare(novocare_order)


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
    novo_care = NovoCarePatientFillForm(**data)
    novo_care_fill_form(novo_care)














