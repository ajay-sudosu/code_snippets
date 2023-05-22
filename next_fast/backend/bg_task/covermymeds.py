# from asyncio.log import logger
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
from selenium.webdriver.support.ui import Select
import platform
from webdriver_manager.chrome import ChromeDriverManager
from utils import send_text_email
from config import CMM_USERNAME, CMM_PASSWORD

logger = logging.getLogger('fastapi')

chromedriver_path = './chromedriver.exe'
which_os = platform.system()
if which_os == 'Windows':
    chromedriver_path = '../chromedriver.exe'


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
    medication: str
    icd_code: str
    # durg_quantity: str
    # drug_days_supply: int
    # primary_diagnosis: str
    # find_your_medication: str
    # doctor_name: str


def retry(f):
    """
    Retry decorator function.
    :param f: function
    :return:
    """

    def wrapper(*args, **kwargs):
        MAX_ATTEMPTS = 3
        for attempt in range(1, MAX_ATTEMPTS + 1):
            try:
                return f(*args, **kwargs)
            except Exception as e:
                logger.exception(f"Attempt {attempt}/{MAX_ATTEMPTS} failed : {e}")
                time.sleep(2 * attempt)

        logger.critical(f"All {MAX_ATTEMPTS} attempts failed!!!")
        raise Exception("Somthing went wrong")

    return wrapper


class NewCoverMedsPatientFillForm:

    def __init__(self):
        logger.debug("Initializing object...")
        self.next_y_coord = 1700
        chrome_options = Options()
        if which_os != 'Windows':
            chrome_options.add_argument("no-sandbox")
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--headless")
        chrome_options.add_argument('--start-maximized')
        chrome_options.add_argument('--window-size=2560,1440')
        # chrome_options.add_experimental_option('w3c', False)
        # self.driver = webdriver.Chrome(options=chrome_options, executable_path=chromedriver_path)
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options,)

        self.driver.implicitly_wait(20)
        self.wait = WebDriverWait(self.driver, 20)

    @retry
    def login(self):
        logger.debug("Login...")
        self.driver.get("https://account.covermymeds.com/")
        username = self.wait.until(EC.element_to_be_clickable((By.NAME, "username")))
        username.send_keys(CMM_USERNAME)
        password = self.wait.until(EC.element_to_be_clickable((By.NAME, "password")))
        password.send_keys(CMM_PASSWORD)
        #  Login button
        button = self.wait.until(EC.element_to_be_clickable((By.NAME, "commit")))
        button.click()

    @retry
    def new_request(self, medication):
        logger.debug(f"New Request for {medication}")
        self.wait.until(EC.visibility_of_element_located((By.ID, "ga-start-new-pa"))).click()

        request_medication = self.wait.until(EC.visibility_of_element_located((By.ID, "s2id_autogen6_search")))
        request_medication.send_keys(medication)
        time.sleep(4)
        request_medication.send_keys(Keys.RETURN)

    @retry
    def prior_authorization(self):
        logger.debug("Prior Authorization...")
        button = self.wait.until(EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, "START PA")))
        button.click()

    @retry
    def patient_details(self, first_name, last_name, sex, dob, zip_code):
        logger.debug("Patient Details...")
        # self.wait.until(EC.visibility_of_element_located((By.ID, "select2-result-label-7"))).click()
        patient_fname = self.wait.until(EC.element_to_be_clickable((By.ID, "patient_fname")))
        patient_fname.clear()
        patient_fname.send_keys(first_name)
        patient_lname = self.wait.until(EC.element_to_be_clickable((By.ID, "patient_lname")))
        patient_lname.clear()
        patient_lname.send_keys(last_name)

        if sex == 0 or sex == "0":
            button = self.driver.find_element(By.XPATH, "//*[@id='male']")
            button.click()
        elif sex == 1 or sex == "1":
            #button = self.wait.until(EC.element_to_be_clickable((By.ID, "female")))
            button = self.driver.find_element(By.XPATH, "//*[@id='female']")
            button.click()
        else:
            button = self.driver.find_element(By.XPATH, "//*[@id='unspecified']")
            button.click()
        # time.sleep(3)
        patient_dob = self.wait.until(EC.element_to_be_clickable((By.ID, "patient_dob")))
        patient_dob.send_keys(dob)
        # time.sleep(3)
        patient_address_zip = self.wait.until(EC.element_to_be_clickable((By.ID, "patient_address_zip")))
        patient_address_zip.send_keys(zip_code)
        # time.sleep(3)
        self.driver.execute_script("window.scrollTo(100,document.body.scrollHeight);")
        # Wait to load page
        # time.sleep(2)
        # self.driver.find_element(By.XPATH, "//*[@id='patient-details']/div[7]/button[2]").click()
        button = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@id='patient-details']/div[7]/button[2]")))
        button.click()
        # time.sleep(5)

    def patient_insurance_search(self, bin_n, pcn_n, group_id_n):
        logger.debug("Insurance search...")
        bins = self.wait.until(EC.element_to_be_clickable((By.ID, 'bin')))
        bins.send_keys(bin_n)
        pcn = self.wait.until(EC.element_to_be_clickable((By.ID, 'pcn')))
        pcn.send_keys(pcn_n)
        group_id = self.wait.until(EC.element_to_be_clickable((By.ID, 'group_id')))
        group_id.send_keys(group_id_n)

    @retry
    def first_search_form(self):
        logger.debug("First Search Form...")
        time.sleep(5)
        self.driver.execute_script("window.scrollTo(100,2200);")
        f = self.driver.find_element(By.ID, "form-search-results")
        b = f.find_elements_by_tag_name("button")
        b[1].click()

    @retry
    def check_eligibility(self):
        self.next_y_coord = 2400
        a = self.wait.until(EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, "Check Eligibility")))
        a.click()
        time.sleep(1)
        e = self.driver.find_element(By.CLASS_NAME, 'eligibility')
        lis = e.find_elements_by_tag_name('li')
        button = lis[0].find_element(By.CLASS_NAME, 'button')
        button.click()

    def patient_information(self, member_id, address1, city):
        logger.debug("Patient Info...")
        # time.sleep(5)
        patient_id_number = self.driver.find_element(By.NAME, "patient_id_number")
        patient_id_number.send_keys(member_id)
        patient_address1 = self.driver.find_element(By.NAME, "patient_address1")
        patient_address1.send_keys(address1)
        patient_city = self.driver.find_element(By.NAME, "patient_city")
        patient_city.send_keys(city)
        try:
            self.driver.find_element(By.PARTIAL_LINK_TEXT, "Check Eligibility")
            self.check_eligibility()
        except Exception as e:
            logger.exception(e)

    @retry
    def prescriber_information(self, doctor='MARC JONATHAN SEROTA'):
        logger.debug("Prescriber Info...")
        self.driver.find_element(By.XPATH, '//*[@id="prescriber-information-section"]/header/span[3]')
        # time.sleep(5)
        js = f"window.scrollTo(0, {self.next_y_coord});"
        self.driver.execute_script(js)
        time.sleep(2)
        button = self.driver.find_element(By.PARTIAL_LINK_TEXT, "Provider address book")
        button.click()
        time.sleep(2)
        try:
            prescriber_list = self.driver.find_element(By.XPATH,
                '//*[@id="prescriber-information-section"]/header/div[2]/div/div/a/ul')
        except:
            prescriber_list = self.driver.find_element(By.XPATH,
                '//*[@id="provider-section"]/header/div[2]/div/div/a/ul')
        items = prescriber_list.find_elements_by_class_name("entry-name")
        for i in items:
            if i.text == doctor:
                i.click()
                break

    def drug_information(self, drug_quantity, drug_form, drug_days_supply, primary_diagnosis):
        logger.debug("Drug Info...")
        # time.sleep(5)
        quantity = self.wait.until(EC.element_to_be_clickable((By.NAME, "drug_quantity")))
        quantity.send_keys(drug_quantity)
        quantity_qualifier = self.wait.until(EC.element_to_be_clickable((By.NAME, 'drug_quantity_qualifier')))
        select = Select(quantity_qualifier)
        select.select_by_visible_text(drug_form)
        days_supply = self.wait.until(EC.element_to_be_clickable((By.NAME, "drug_days_supply")))
        days_supply.clear()
        days_supply.click()
        time.sleep(1)
        days_supply.send_keys(drug_days_supply)
        icd10 = primary_diagnosis[:5]

        diagnosis = self.wait.until(EC.element_to_be_clickable((By.NAME, "icd10")))
        diagnosis.send_keys(icd10)
        time.sleep(1)
        e = self.driver.find_element(By.CLASS_NAME, "ui-menu-item")
        if e.text == primary_diagnosis:
            e.click()

    @retry
    def type_of_review(self, urgent=False):
        logger.debug("Type of Review...")
        if urgent:
            xpath = '//*[@id="type-of-review-section"]/div[1]/div/div[2]/div[1]/div[3]/div/div/label[1]/input'
        else:
            xpath = '//*[@id="type-of-review-section"]/div[1]/div/div[2]/div[1]/div[3]/div/div/label[2]/input'

        a = self.wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
        a.click()

    @retry
    def send_to_plan(self):
        logger.debug("Send to Plan...")
        a = self.wait.until(EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, "Send to Plan")))
        a.click()
        time.sleep(15)
        #self.driver.get('https://www.covermymeds.com/request/list')

    def workflow(self, order_details):
        medication_dict = {
            "Ozempic (0.25 or 0.5 MG/DOSE) 2MG/1.5ML": {
                'drug_quantity': "1.5",
                'drug_form': 'Milliliter',
                'drug_days_supply': 28,
                'primary_diagnosis': 'E11.9 - Type 2 diabetes mellitus without complications'
            },
            'Mounjaro 2.5MG/0.5ML': {
                'drug_quantity': "2",
                'drug_form': 'Milliliter',
                'drug_days_supply': 28,
                'primary_diagnosis': 'E11.9 - Type 2 diabetes mellitus without complications'
            },
            'Saxenda 18MG/3ML': {  # 'PA'
                'drug_quantity': "15",
                'drug_form': 'Milliliter',
                'drug_days_supply': 30,
                'primary_diagnosis': 'E66.9 - Obesity, unspecified'
            },
            'Rybelsus 3MG': {
                'drug_quantity': "30",
                'drug_form': 'Tablet',
                'drug_days_supply': 30,
                'primary_diagnosis': 'E11.9 - Type 2 diabetes mellitus without complications'
            },
            'Wegovy 0.25MG/0.5ML': {  # 'PA'
                'drug_quantity': "2",
                'drug_form': 'Milliliter',
                'drug_days_supply': 28,
                'primary_diagnosis': 'E66.9 - Obesity, unspecified'
            },
        }
        first_name = order_details.get('first_name')
        last_name = order_details.get('last_name')
        sex = order_details.get("sex")
        dob = order_details.get("dob")
        zip_code = order_details.get("zip_code")
        bins = order_details.get("RxBIN")
        pcn = order_details.get("RxPCN")
        group_id = order_details.get("RxGroup")
        member_id = order_details.get("member_id")
        street = order_details.get("street")
        city = order_details.get("city")
        medication = order_details.get("medication")
        primary_diagnosis = order_details.get("icd_code")

        # for drug in medication.keys():
        try:
            self.login()
            self.new_request(medication)
            if medication == 'Wegovy 0.25MG/0.5ML' or medication == 'Saxenda 18MG/3ML':
                time.sleep(3)
                self.prior_authorization()
            self.patient_details(first_name, last_name, sex, dob, zip_code)
            self.patient_insurance_search(bins, pcn, group_id)
            self.first_search_form()
            self.patient_information(member_id, street, city)
            self.prescriber_information()
            self.drug_information(medication_dict[medication]['drug_quantity'],
                                  medication_dict[medication]['drug_form'],
                                  medication_dict[medication]['drug_days_supply'],
                                  primary_diagnosis
                                  )
            # self.type_of_review()
            self.send_to_plan()
        except Exception as e:
            logger.exception(e)
            self.driver.quit()
            subject = "PA Request Error."
            content = f"{order_details}"
            send_text_email(
                sender='team@joinnextmed.com',
                recipient='team@joinnextmed.com',
                subject=subject,
                content=content
            )
        # time.sleep(3000)

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
        durg_quantity = "0.75"
        drug_days_supply = "28"
        primary_diagnosis = "E66.01 - Morbid (severe) obesity due to excess calories"
        find_your_medication = ["Rybelsus", "Ozempic", "Wegovy", "Mounjaro", "Saxenda"]
        doctor_name = "MARC JONATHAN SEROTA"

        for meds in find_your_medication:
            self.driver.get("https://account.covermymeds.com/")
            self.driver.maximize_window()
            wait = WebDriverWait(self.driver, 20)
            username = self.driver.find_element_by_name("username")
            password = self.driver.find_element_by_name("password")
            username.send_keys("nextmedical")
            password.send_keys("2022JoinNext!")
            #  Login button
            self.driver.find_element_by_name("commit").click()
            wait.until(EC.visibility_of_element_located((By.ID, "new-request"))).click()

            request_medication = wait.until(EC.visibility_of_element_located((By.ID, "s2id_autogen6_search")))
            request_medication.send_keys(meds)
            wait.until(EC.visibility_of_element_located((By.ID, "select2-result-label-7"))).click()
            patient_fname = wait.until(EC.visibility_of_element_located((By.ID, "patient_fname")))
            patient_fname.send_keys(first_name)
            patient_lname = wait.until(EC.visibility_of_element_located((By.ID, "patient_lname")))
            patient_lname.send_keys(last_name)
            time.sleep(5)

            if sex == 0:
                time.sleep(5)
                self.driver.find_element(By.XPATH,
                                         "/html/body/div[1]/div[1]/div/div[2]/div/form/div[3]/div[1]/fieldset/div[3]/div/label[1]").click()
            elif sex == 1:
                time.sleep(5)
                self.driver.find_element(By.XPATH,
                                         "/html/body/div[1]/div[1]/div/div[2]/div/form/div[3]/div[1]/fieldset/div[3]/div/label[2]").click()
            else:
                time.sleep(5)
                self.driver.find_element(By.XPATH, "//*[@id='unspecified']").click()
            time.sleep(5)
            patient_dob = wait.until(EC.visibility_of_element_located((By.ID, "patient_dob")))
            patient_dob.send_keys(dob)
            time.sleep(5)
            patient_address_zip = wait.until(EC.visibility_of_element_located((By.ID, "patient_address_zip")))
            patient_address_zip.send_keys(zip_code)
            time.sleep(10)
            self.driver.execute_script("window.scrollTo(100,document.body.scrollHeight);")
            # Wait to load page
            time.sleep(2)
            self.driver.find_element(By.XPATH, "//*[@id='patient-details']/div[7]/button[2]").click()
            time.sleep(5)
            try:
                self.driver.find_element(By.XPATH, "//*[@id='continue-to-insurance-search-button']").click()
                time.sleep(10)
                bin = wait.until(EC.visibility_of_element_located((By.ID, "bin")))
                bin.send_keys(RxBIN)
                pcn = wait.until(EC.visibility_of_element_located((By.ID, "pcn")))
                pcn.send_keys(RxPCN)
                group_id = wait.until(EC.visibility_of_element_located((By.ID, "group_id")))
                group_id.send_keys(RxGroup)
                time.sleep(5)
                # Count the total number of forms.
                getAllForms = self.driver.find_element(By.ID, "formpick-form-results")
                items = getAllForms.find_elements_by_tag_name("li")
                for i in range(1, len(items)):
                    print("Processing form 1: gh", i)
                    self.driver.get("https://formpick.covermymeds.com/")
                    # Now again filling all formsrequest_medication = wait.until(EC.visibility_of_element_located((By.ID,"s2id_autogen6_search")))
                    request_medication = wait.until(EC.visibility_of_element_located((By.ID, "s2id_autogen6_search")))
                    request_medication.send_keys(meds)
                    wait.until(EC.visibility_of_element_located((By.ID, "select2-result-label-7"))).click()
                    patient_fname = wait.until(EC.visibility_of_element_located((By.ID, "patient_fname")))
                    patient_fname.send_keys(first_name)
                    patient_lname = wait.until(EC.visibility_of_element_located((By.ID, "patient_lname")))
                    patient_lname.send_keys(last_name)

                    if sex == 0:
                        time.sleep(5)
                        self.driver.find_element(By.XPATH,
                                                 "/html/body/div[1]/div[1]/div/div[2]/div/form/div[3]/div[1]/fieldset/div[3]/div/label[1]").click()
                    elif sex == 1:
                        time.sleep(5)
                        self.driver.find_element(By.XPATH,
                                                 "/html/body/div[1]/div[1]/div/div[2]/div/form/div[3]/div[1]/fieldset/div[3]/div/label[2]").click()
                    else:
                        time.sleep(5)
                        self.driver.find_element(By.XPATH, "//*[@id='unspecified']").click()
                    time.sleep(5)
                    patient_dob = wait.until(EC.visibility_of_element_located((By.ID, "patient_dob")))
                    patient_dob.send_keys(dob)
                    time.sleep(5)
                    patient_address_zip = wait.until(EC.visibility_of_element_located((By.ID, "patient_address_zip")))
                    patient_address_zip.send_keys(zip_code)
                    time.sleep(10)
                    self.driver.execute_script("window.scrollTo(100,document.body.scrollHeight);")
                    time.sleep(5)
                    self.driver.find_element(By.XPATH, "//*[@id='patient-details']/div[7]/button[2]").click()
                    time.sleep(5)
                    wait.until(EC.visibility_of_element_located(
                        (By.XPATH, "//*[@id='formpick-form-results']/li[" + str(i) + "]/div[2]/div/button[2]"))).click()
                    time.sleep(5)
                    patient_id_number = self.driver.find_element(By.NAME, "patient_id_number")
                    patient_id_number.send_keys(member_id)
                    patient_address1 = self.driver.find_element(By.NAME, "patient_address1")
                    patient_address1.send_keys(street)
                    patient_city.send_keys(city)
                    patient_city = self.driver.find_element(By.NAME, "patient_city")
                    # CLICKING ON BUTTON TO CHECK ELIGIBILITY:
                    time.sleep(5)
                    self.driver.find_element(By.XPATH, "//*[@id='patient-section']/div[1]/div[7]/div[2]/a[2]").click()
                    # Select button
                    # WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[7]/div[2]/ul/li/a"))).click()
                    time.sleep(15)
                    self.driver.find_element(By.XPATH, "/html/body/div[7]/div[2]/ul/li/a").click()
                    time.sleep(5)

                    drug_quantity = self.driver.find_element(By.NAME, "drug_quantity")
                    drug_quantity.send_keys(durg_quantity)
                    time.sleep(5)
                    select = Select(self.driver.find_element(By.NAME, "drug_quantity_qualifier"))
                    select.select_by_value("C28254")
                    drug_days_supply = self.driver.find_element(By.NAME, "drug_days_supply")
                    drug_days_supply.send_keys(drug_days_supply)
                    time.sleep(5)
                    self.driver.execute_script("window.scrollTo(0, window.scrollY + 100)")
                    icd10 = self.driver.find_element(By.NAME, "icd10")
                    icd10.send_keys(primary_diagnosis)
                    print("Now clicking on dropdown")
                    time.sleep(10)
                    get_doctor = self.driver.find_element(By.XPATH,
                                                          "//*[@id='provider-section']/header/div[2]/div/div/a/ul")
                    all_li = get_doctor.find_elements_by_tag_name("li")
                    sum_f = len(all_li) + 1
                    print(sum_f, "----------")
                    for k in range(1, len(all_li) + 1):
                        doc_name = self.driver.find_element(By.XPATH,
                                                            "//*[@id='provider-section']/header/div[2]/div/div/a/ul/li[" + str(
                                                                k) + "]/span[1]").text
                        print(doc_name)
                        if doctor_name == doc_name:
                            self.driver.find_element(By.XPATH,
                                                     "//*[@id='provider-section']/header/div[2]/div/div/a/ul/li[" + str(
                                                         k) + "]/span[1]").click()
                            time.sleep(20)
                            WebDriverWait(self.driver, 20).until(EC.element_to_be_clickable((By.XPATH,
                                                                                             "//*[@id='type-of-review-section']/div[1]/div/div[2]/div[1]/div[3]/div/div/label[2]"))).click()
                            time.sleep(20)
                            WebDriverWait(self.driver, 20).until(EC.element_to_be_clickable(
                                (By.XPATH, "//*[@id='app']/div/div[4]/section/div/a"))).click()
                            time.sleep(20)
                            WebDriverWait(self.driver, 20).until(
                                EC.element_to_be_clickable((By.XPATH, "/html/body/div[7]/div[3]/button[1]"))).click()
                            time.sleep(20)
                        else:
                            print("Doctor name not found!")



            except NoSuchElementException:
                print("Element not found!")
                bin = wait.until(EC.visibility_of_element_located((By.ID, "bin")))
                bin.send_keys(RxBIN)
                pcn = wait.until(EC.visibility_of_element_located((By.ID, "pcn")))
                pcn.send_keys(RxPCN)
                group_id = wait.until(EC.visibility_of_element_located((By.ID, "group_id")))
                group_id.send_keys(RxGroup)
                time.sleep(5)
                # Count the total number of forms.
                getAllForms = self.driver.find_element(By.ID, "formpick-form-results")
                items = getAllForms.find_elements_by_tag_name("li")
                for i in range(1, len(items)):
                    print("No Element Processing form: ", i)
                    time.sleep(5)
                    self.driver.get("https://formpick.covermymeds.com/")
                    # Now again filling all formsrequest_medication = wait.until(EC.visibility_of_element_located((By.ID,"s2id_autogen6_search")))
                    request_medication = wait.until(EC.visibility_of_element_located((By.ID, "s2id_autogen6_search")))
                    request_medication.send_keys(meds)
                    wait.until(EC.visibility_of_element_located((By.ID, "select2-result-label-7"))).click()
                    patient_fname = wait.until(EC.visibility_of_element_located((By.ID, "patient_fname")))
                    patient_fname.send_keys(first_name)
                    patient_lname = wait.until(EC.visibility_of_element_located((By.ID, "patient_lname")))
                    patient_lname.send_keys(last_name)

                    if sex == 0:
                        time.sleep(5)
                        self.driver.find_element(By.XPATH,
                                                 "//*[@id='patient-section']/div[1]/div[3]/div[2]/div[1]/div/div/div/label[1]/input").click()
                    elif sex == 1:
                        time.sleep(5)
                        self.driver.find_element(By.XPATH,
                                                 "//*[@id='patient-section']/div[1]/div[3]/div[2]/div[1]/div/div/div/label[2]/input]").click()
                    else:
                        time.sleep(5)
                        self.driver.find_element(By.XPATH, "//*[@id='unspecified']").click()
                    time.sleep(5)
                    patient_dob = wait.until(EC.visibility_of_element_located((By.ID, "patient_dob")))
                    patient_dob.send_keys(dob)
                    time.sleep(5)
                    patient_address_zip = wait.until(EC.visibility_of_element_located((By.ID, "patient_address_zip")))
                    patient_address_zip.send_keys(zip_code)
                    time.sleep(5)
                    self.driver.execute_script("window.scrollTo(100,document.body.scrollHeight);")
                    # Wait to load page
                    time.sleep(5)
                    self.driver.find_element(By.XPATH, "//*[@id='patient-details']/div[7]/button[2]").click()
                    bin = wait.until(EC.visibility_of_element_located((By.ID, "bin")))
                    bin.send_keys(RxBIN)
                    pcn = wait.until(EC.visibility_of_element_located((By.ID, "pcn")))
                    pcn.send_keys(RxPCN)
                    group_id = wait.until(EC.visibility_of_element_located((By.ID, "group_id")))
                    group_id.send_keys(RxGroup)
                    time.sleep(5)
                    self.driver.execute_script("window.scrollBy(0,500)")
                    # Wait to load page
                    time.sleep(5)
                    wait.until(EC.visibility_of_element_located(
                        (By.XPATH, "//*[@id='formpick-form-results']/li[" + str(i) + "]/div[2]/div/button[2]"))).click()
                    time.sleep(5)
                    patient_id_number = self.driver.find_element(By.NAME, "patient_id_number")
                    patient_id_number.send_keys(member_id)
                    patient_address1 = self.driver.find_element(By.NAME, "patient_address1")
                    patient_address1.send_keys(street)
                    patient_city = self.driver.find_element(By.NAME, "patient_city")
                    patient_city.send_keys(city)
                    time.sleep(5)
                    # CLICKING ON BUTTON TO CHECK ELIGIBILITY:
                    self.driver.find_element(By.XPATH,
                                             "/html/body/div[3]/div[2]/div/div[3]/section[2]/div[1]/div[7]/div[2]/a[2]").click()
                    # Select button
                    # WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[7]/div[2]/ul/li/a"))).click()
                    time.sleep(15)
                    self.driver.find_element(By.XPATH, "/html/body/div[7]/div[2]/ul/li/a").click()
                    time.sleep(10)
                    self.driver.execute_script("window.scrollTo(0, window.scrollY + 100)")
                    time.sleep(5)
                    drug_quantity = self.driver.find_element(By.NAME, "drug_quantity")
                    drug_quantity.send_keys(durg_quantity)
                    select = Select(self.driver.find_element(By.NAME, "drug_quantity_qualifier"))
                    select.select_by_value("C28254")
                    time.sleep(5)
                    print("Chekcing............")
                    drug_days_supply = self.driver.find_element(By.NAME, "drug_days_supply")
                    drug_days_supply.send_keys(28)
                    drug_days_supply.send_keys(Keys.BACKSPACE)
                    drug_days_supply.send_keys(Keys.BACKSPACE)
                    drug_days_supply.send_keys(Keys.BACKSPACE)
                    drug_days_supply.send_keys(28)
                    time.sleep(10)
                    # icd10 = driver.find_element(By.NAME, "icd10")
                    # icd10.send_keys(primary_diagnosis)
                    print("Now clicking on dropdown")
                    WebDriverWait(self.driver, 20).until(EC.element_to_be_clickable(
                        (By.XPATH, "//*[@id='provider-section']/header/div[2]/div/div"))).click()
                    time.sleep(5)
                    get_doctor = self.driver.find_element(By.XPATH,
                                                          "//*[@id='provider-section']/header/div[2]/div/div/a/ul")
                    all_li = get_doctor.find_elements_by_tag_name("li")
                    sum_f = len(all_li) + 1
                    print(sum_f, "----------")
                    for k in range(1, len(all_li) + 1):
                        doc_name = self.driver.find_element(By.XPATH,
                                                            "//*[@id='provider-section']/header/div[2]/div/div/a/ul/li[" + str(
                                                                k) + "]/span[1]").text
                        print(doc_name)
                        if doctor_name == doc_name:
                            self.driver.find_element(By.XPATH,
                                                     "//*[@id='provider-section']/header/div[2]/div/div/a/ul/li[" + str(
                                                         k) + "]/span[1]").click()
                            time.sleep(5)
                            # WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, "//*[@id='provider-section']/header/div[2]/div/div/a/ul/li[1]"))).click()
                            # time.sleep(5)
                            WebDriverWait(self.driver, 20).until(EC.element_to_be_clickable((By.XPATH,
                                                                                             "//*[@id='type-of-review-section']/div[1]/div/div[2]/div[1]/div[3]/div/div/label[2]"))).click()
                            time.sleep(5)
                            WebDriverWait(self.driver, 20).until(EC.element_to_be_clickable(
                                (By.XPATH, "//*[@id='app']/div/div[4]/section/div/a"))).click()
                            time.sleep(55)
                            WebDriverWait(self.driver, 20).until(
                                EC.element_to_be_clickable((By.XPATH, "/html/body/div[7]/div[3]/button[1]"))).click()
                            time.sleep(10)
                        else:
                            print("Doctor name not found!")


def cover_my_meds_fill_form(order_details: CoverMedsPatientFillForm):
    order = NewCoverMedsPatientFillForm()
    covermeds_order = order_details.dict()
    logger.info(f"fill form for covermeds Patient: {covermeds_order}")
    order.workflow(covermeds_order)


if __name__ == '__main__':
    data = {
        "patient_id": "103498773",
        "first_name": "Marc",
        "last_name": "Jonathan",
        "sex": "0",
        "dob": "08201990",
        "zip_code": "85711",
        "RxBIN": "004336",
        "RxPCN": "RX7391",
        "RxGroup": "ADV",
        "member_id": "985864208",
        "street": "Home Visit",
        "city": "Newyork",
        "medication": 'Wegovy 0.25MG/0.5ML',
        "icd_code": 'E66.9 - Obesity, unspecified'
        # "doctor_name": "MARCJONATHAN_SEROTA"
    }
    cover_meds = CoverMedsPatientFillForm(**data)
    cover_my_meds_fill_form(cover_meds)
