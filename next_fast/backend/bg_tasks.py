
import os
import time
import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
from pydantic import BaseModel
from db_client import DBClient
import platform
from drchrono import drchrono


logger = logging.getLogger("fastapi")

DRCHRONO_USERNAME = "TariqueAnwer"
DRCHRONO_PASSWORD = "drchrono@123#"
chromedriver_path = './chromedriver.exe'
which_os = platform.system()
if which_os == 'Windows':
    chromedriver_path = '..\\chromedriver.exe'

url_login = "https://app.drchrono.com/accounts/login/"

new_order_dropdown = '//*[@id="content1"]/div[3]/div/div/div/div[1]/div[2]/a'
new_order_dropdown_menu = {
    'Manual Entry': '//*[@id="content1"]/div[3]/div/div/div/div[1]/div[2]/ul/li[1]/a',
    'Quest Diagnostics': '//*[@id="content1"]/div[3]/div/div/div/div[1]/div[2]/ul/li[3]/a',
    'LabCorp': '//*[@id="content1"]/div[3]/div/div/div/div[1]/div[2]/ul/li[4]/a'
}
xpath_dropdown_quest_wdl = '//*[@id="lab-order-form"]/div/form/div[1]/div/select'
xpath_dropdown_labcorp_bill_type = '//*[@id="lab-order-form"]/div/form/div[1]/div/select'

bill_to_radio_button = {
    'Patient': '//*[@id="lab-order-form"]/div/form/fieldset[1]/div[1]/div/div[1]/button[1]',
    'Doctor': '//*[@id="lab-order-form"]/div/form/fieldset[1]/div[1]/div/div[1]/button[2]',
    'Insurance': '//*[@id="lab-order-form"]/div/form/fieldset[1]/div[1]/div/div[1]/button[3]'
}

id_icd_10_codes = 's2id_autogen4'

# indoor outdoor allergy
icd_10_codes_test_mapper = dict.fromkeys(['15277', '15286', '15288', '15289', '15290', '15291',
                                          '15292', '15293', '15294', '15278', '15279', '15280',
                                          '15281', '15282', '15283', '15284', '15287'
                                          '15259', '15268', '15269', '15270', '15271', '15272',
                                          '15273', '15274', '15275', '15260', '15261', '15262',
                                          '15263', '15264', '15265', '15266', '15267'],
                                         'T78.40XA')
# Hormone Test
icd_10_codes_test_mapper.update(dict.fromkeys(['15311', '15313', '15296', '15298', '15297',
                                               '15305', '15299', '15312', '15320', '15314', '16868'], 'Z13.29'))
# Celiac Disease
icd_10_codes_test_mapper.update(dict.fromkeys(['15295', '15276'], 'R10.9'))
# Food Allergy
icd_10_codes_test_mapper.update(dict.fromkeys(['15258', '15257'], 'Z91.018'))
# Thyroid tests
icd_10_codes_test_mapper.update(dict.fromkeys(['15302', '15300', '15301', '15317', '15315', '15316'], 'Z13.29'))
# heavy metal
icd_10_codes_test_mapper.update(dict.fromkeys(['15303', '15318'], 'T56.891A'))
# lyme
icd_10_codes_test_mapper.update(dict.fromkeys(['15304', '15319'], 'A69.20'))
# STD
icd_10_codes_test_mapper.update(dict.fromkeys(['15245', '15249', '15248', '16876', '16877', '16878', '16879'], 'Z11.3'))
# HIV
icd_10_codes_test_mapper.update(dict.fromkeys(['15522', '15543', '15521', '15514', '15545'], 'B20'))
# Herpes
icd_10_codes_test_mapper.update(dict.fromkeys(['15544', '15521', '16101', '15523', '15542', '15516', '15515'], 'B00.9'))
# vitamin
icd_10_codes_test_mapper.update(dict.fromkeys(['16863'], 'E53.9'))
# weightloss
icd_10_codes_test_mapper.update(dict.fromkeys(['19494', '19495', '19496', '19497'], 'E66.9'))

xpath_dropdown_load_a_favorite = '//*[@id="lab-order-form"]/div/form/div[1]/div/button[2]'

text_dropdown_load_a_favorite_menu_labcorp = {
    '15257': '15257 : 36 Food Allergy Panel',
    '15295': '15295 : Celiac Disease',
    '15310': '15310 : Cholesterol & Lipids Panel',
    '15306': '15306 : Cortisol Test',
    '15296': '15296 : Female Hormone Complete',
    '15303': '15303 : Heavy Metals Test',
    '36 Food Allergy Panel': '15257 : 36 Food Allergy Panel',
    'Celiac Disease': '15295 : Celiac Disease',
    'Cholesterol & Lipids Panel': '15310 : Cholesterol & Lipids Panel',
    'Cortisol Test': '15306 : Cortisol Test',
    'Female Hormone Complete': '15296 : Female Hormone Complete',
    'Heavy Metals Test': '15303 : Heavy Metals Test',
    '15309': '15309 : Hemoglobin A1C Test',
    '15544': '15544 : Herpes Early Detection',
    '15522': '17054 : HIV Complete',
    '15543': '15543 : HIV RNA',
    '15521': '17053 : HIV Standard',
    '16101': '16101 : HSV Complete',
    '15523': '15523 : HSV Standard',
    '15277': '15277 : Indoor Outdoor Allergy Region 1',
    '15286': '15286 : Indoor Outdoor Allergy Region 10',
    '15288': '15288 : Indoor Outdoor Allergy Region 11',
    '15289': '15289 : Indoor Outdoor Allergy Region 12',
    '15290': '15290 : Indoor Outdoor Allergy Region 13',
    '15291': '15291 : Indoor Outdoor Allergy Region 14',
    '15292': '15292 : Indoor Outdoor Allergy Region 15',
    '15293': '15293 : Indoor Outdoor Allergy Region 16',
    '15294': '15294 : Indoor Outdoor Allergy Region 17',
    '15278': '15278 : Indoor Outdoor Allergy Region 2',
    '15279': '15279 : Indoor Outdoor Allergy Region 3',
    '15280': '15280 : Indoor Outdoor Allergy Region 4',
    '15581': '15281 : Indoor Outdoor Allergy Region 5',
    '15582': '15282 : Indoor Outdoor Allergy Region 6',
    '15283': '15283 : Indoor Outdoor Allergy Region 7',
    '15284': '15284 : Indoor Outdoor Allergy Region 8',
    '15287': '15287 : Indoor Outdoor Allergy Region 9',
    '15304': '15304 : Lyme Disease Test',
    '15298': '15298 : Male Hormone Test',
    '15297': '15297 : Female Hormone Standard',
    '15305': '15305 : Sleep & Stress Hormone Test',
    'Lyme Disease Test': '15304 : Lyme Disease Test',
    'Male Hormone Test': '15298 : Male Hormone Test',
    'Female Hormone Standard': '15297 : Female Hormone Standard',
    'Sleep & Stress Hormone Test': '15305 : Sleep & Stress Hormone Test',
    '15245': '17052 : STD Basic',
    '15247': '16631 : STD Complete',
    '15525': '15525 : STD Complete (HIV)',
    '15526': '15526 : STD Complete (HSV)',
    '15451': '16628 : STD Standard',
    'STD Standard': '16628 : STD Standard',
    'STD Basic': '15245 : STD Basic',
    'STD Complete': '15247 : STD Complete',
    'STD Complete (HIV)': '15525 : STD Complete (HIV)',
    'STD Complete (HSV)': '15526 : STD Complete (HSV)',
    'STD Standard New': '15451 : STD Standard New',
    '15299': '15299 : Male Hormone Standard',
    '15302': '15302 : Thyroid Complete Panel',
    '15300': '15300 : Thyroid Function Test',
    '15301': '15301 : Thyroid Standard Panel',
    '15307': '15307 : Vitamin B Panel',
    '15308': '15308 : Vitamin D & Inflammation Test',
    'Male Hormone Standard': '15299 : Male Hormone Standard',
    'Thyroid Complete Panel': '15302 : Thyroid Complete Panel',
    'Thyroid Function Test': '15300 : Thyroid Function Test',
    'Thyroid Standard Panel': '15301 : Thyroid Standard Panel',
    'Vitamin B Panel': '15307 : Vitamin B Panel',
    'Vitamin D & Inflammation Test': '15308 : Vitamin D & Inflammation Test',
    '16868': '16868 : Comp. Metabolic Panel',
    '16863': '16863 : Complete Vitamin Panel',
    '16877': '16877 : Chlamydia',
    '16878': '16878 : Gonorrhea',
    '16879': '16879 : Trichomoniasis',
    '16876': '16876 : Mycoplasma & Ureaplasma',
    '16823': '16823 : Wegovy/Metformin (Weight Loss)',
    '19494': '19494 : GLP-1 Weight Loss Program',
    '19495': '19495 : GLP-1 Weight Loss Complete Program',
    '17853': '17853 : Weight Loss Quarterly Female',
    '17854': '17854 : Weight Loss Quarterly Male',
    '17868': '17868 : Acne Treatment Program Female',    
    '17867': '17867 : Acne Treatment Program Male',    
    '18488': '18488 : Celiac Complete',    
    '18489': '18489 : Female Hormone Complete',    
    '18492': '18492 : Male Hormone Complete',    
    '19278': '19278 : Weight Loss Program',
    '19279': '19279 : Weight Loss Complete Program',
    '18499': '18499 : Contrave Weight Loss Program',    
    '18500': '18500 : Metformin Weight Loss Program',    
    '18496': '18496 : Comprehensive Metabolic Panel',    
    '18493': '18493 : 16-Component Urinalysis',
    '18689': '18689 : Clomid'    
}

text_dropdown_load_a_favorite_menu_quest = {
    '15258': '15258 : 36 Food Allergy Panel',
    '15276': '15276 : Celiac Disease',
    '15325': '15325 : Cholesterol & Lipids Panel',
    '15321': '15321 : Cortisol Test',
    '36 Food Allergy Panel': '15258 : 36 Food Allergy Panel',
    'Celiac Disease': '15276 : Celiac Disease',
    'Cholesterol & Lipids Panel': '15325 : Cholesterol & Lipids Panel',
    'Cortisol Test': '15321 : Cortisol Test',
    'Female Hormone Complete': '15311 : Female Hormone Complete',
    '15318': '15318 : Heavy Metals Test',
    '15324': '15324 : Hemoglobin A1C Test',
    '15542': '15542 : Herpes Early Detection',
    '15514': '17051 : HIV Complete',
    '15545': '15545 : HIV RNA',
    'Heavy Metals Test': '15318 : Heavy Metals Test',
    'Hemoglobin A1C Test': '15324 : Hemoglobin A1C Test',
    'Herpes Early Detection': '15542 : Herpes Early Detection',
    'HIV Complete': '15514 : HIV Complete',
    'HIV RNA': '15545 : HIV RNA',
    '15513': '17050 : HIV Standard',
    '15516': '15516 : HSV Complete',
    '15515': '15515 : HSV Standard',
    'HIV Standard': '15513 : HIV Standard',
    'HSV Complete': '15516 : HSV Complete',
    'HSV Standard': '15515 : HSV Standard',
    '15259': '15259 : Indoor Outdoor Allergy Region 1',
    '15268': '15268 : Indoor Outdoor Allergy Region 10',
    '15269': '15269 : Indoor Outdoor Allergy Region 11',
    '15270': '15270 : Indoor Outdoor Allergy Region 12',
    '15271': '15271 : Indoor Outdoor Allergy Region 13',
    '15272': '15272 : Indoor Outdoor Allergy Region 14',
    '15273': '15273 : Indoor Outdoor Allergy Region 15',
    '15274': '15274 : Indoor Outdoor Allergy Region 16',
    '15275': '15275 : Indoor Outdoor Allergy Region 17',
    'Indoor Outdoor Allergy Region 1': '15259 : Indoor Outdoor Allergy Region 1',
    'Indoor Outdoor Allergy Region 10': '15268 : Indoor Outdoor Allergy Region 10',
    'Indoor Outdoor Allergy Region 11': '15269 : Indoor Outdoor Allergy Region 11',
    'Indoor Outdoor Allergy Region 12': '15270 : Indoor Outdoor Allergy Region 12',
    'Indoor Outdoor Allergy Region 13': '15271 : Indoor Outdoor Allergy Region 13',
    'Indoor Outdoor Allergy Region 14': '15272 : Indoor Outdoor Allergy Region 14',
    'Indoor Outdoor Allergy Region 15': '15273 : Indoor Outdoor Allergy Region 15',
    'Indoor Outdoor Allergy Region 16': '15274 : Indoor Outdoor Allergy Region 16',
    'Indoor Outdoor Allergy Region 17': '15275 : Indoor Outdoor Allergy Region 17',
    '15260': '15260 : Indoor Outdoor Allergy Region 2',
    '15261': '15261 : Indoor Outdoor Allergy Region 3',
    '15262': '15262 : Indoor Outdoor Allergy Region 4',
    '15263': '15263 : Indoor Outdoor Allergy Region 5',
    '15264': '15264 : Indoor Outdoor Allergy Region 6',
    '15265': '15265 : Indoor Outdoor Allergy Region 7',
    '15266': '15266 : Indoor Outdoor Allergy Region 8',
    '15267': '15267 : Indoor Outdoor Allergy Region 9',
    'Indoor Outdoor Allergy Region 2': '15260 : Indoor Outdoor Allergy Region 2',
    'Indoor Outdoor Allergy Region 3': '15261 : Indoor Outdoor Allergy Region 3',
    'Indoor Outdoor Allergy Region 4': '15262 : Indoor Outdoor Allergy Region 4',
    'Indoor Outdoor Allergy Region 5': '15263 : Indoor Outdoor Allergy Region 5',
    'Indoor Outdoor Allergy Region 6': '15264 : Indoor Outdoor Allergy Region 6',
    'Indoor Outdoor Allergy Region 7': '15265 : Indoor Outdoor Allergy Region 7',
    'Indoor Outdoor Allergy Region 8': '15267 : Indoor Outdoor Allergy Region 8',
    'Indoor Outdoor Allergy Region 9': '15267 : Indoor Outdoor Allergy Region 9',
    '15319': '15319 : Lyme Disease Test',
    '15313': '15313 : Male Hormone Test',
    '15311': '15311 : Female Hormone Test',
    '15312': '15312 : Ovarian Reserve Test',
    'Ovarian Reserve': '15312 : Ovarian Reserve Test',
    '15320': '15320 : Sleep & Stress Hormone Test',
    'Lyme Disease Test': '15319 : Lyme Disease Test',
    'Male Hormone Test': '15313 : Male Hormone Test',
    'Female Hormone Standard': '15312 : Female Hormone Standard',
    'Sleep & Stress Hormone Test': '15320 : Sleep & Stress Hormone Test',
    '15249': '17049 : STD Basic - F',
    '15248': '17048 : STD Basic - M',
    '15518': '15518 : STD Complete (HIV) Female',
    '15517': '15517 : STD Complete (HIV) Male',
    '15519': '15519 : STD Complete (HSV) Female',
    '15520': '15520 : STD Complete (HSV) Male',
    '15253': '16625 : STD Complete - Female',
    '15252': '16626 : STD Complete - Male',
    '15449': '16623 : STD Standard - Female',
    '15450': '16622 : STD Standard - Male',
    'STD Basic - Female': '15249 : STD Basic - Female',
    'STD Basic - Male': '15248 : STD Basic - Male',
    'STD Complete (HIV) Female': '15518 : STD Complete (HIV) Female',
    'STD Complete (HIV) Male': '15517 : STD Complete (HIV) Male',
    'STD Complete (HSV) Female': '15519 : STD Complete (HSV) Female',
    'STD Complete (HSV) Male': '15520 : STD Complete (HSV) Male',
    'STD Complete - Female': '15253 : STD Complete - Female',
    'STD Complete - Male': '15252 : STD Complete - Male',
    'STD Standard Female New': '15449 : STD Standard Female New',
    'STD Standard Male New': '15450 : STD Standard Male New',
    '15314': '15314 : Male Hormone Standard',
    '15317': '15317 : Thyroid Complete Panel',
    '15315': '15315 : Thyroid Function Test',
    '15316': '15316 : Thyroid Standard Panel',
    '15322': '15322 : Vitamin B Panel',
    '15323': '15323 : Vitamin D & Inflammation Test',
    'Male Hormone Standard': '15314 : Male Hormone Standard',
    'Thyroid Complete Panel': '15317 : Thyroid Complete Panel',
    'Thyroid Function Test': '15315 : Thyroid Function Test',
    'Thyroid Standard Panel': '15316 : Thyroid Standard Panel',
    'Vitamin B Panel': '15322 : Vitamin B Panel',
    'Vitamin D & Inflammation Test': '15323 : Vitamin D & Inflammation Test',
    '16833': '16833 : Comp. Metabolic Panel',
    '16862': '16862 : Complete Vitamin Panel',
    '16874': '16874 : Chlamydia',
    '16873': '16873 : Gonorrhea',
    '16871': '16871 : Trichomoniasis - Male',
    '16872': '16872 : Trichomoniasis - Female',
    '16875': '16875 : Mycoplasma & Ureaplasma',
    '16822': '16822 : Wegovy/Metformin (Weight Loss)',
    '19276': '19276 : Weight Loss Program',
    '19277': '19277 : Weight Loss Complete Program',
    '17767': '17767 : Weight Loss Quarterly Female',
    '17768': '17768 : Weight Loss Quarterly Male',    
    '17864': '17864 : Acne Treatment Program Female',    
    '17865': '17865 : Acne Treatment Program Male',
    '18487': '18487 : Celiac Complete',
    '18490': '18490 : Female Hormone Complete',
    '18491': '18491 : Male Hormone Complete',
    '19496': '19496 : GLP-1 Weight Loss Program',
    '19497': '19497 : GLP-1 Weight Loss Complete Program',
    '18503': '18503 : Contrave Weight Loss Program',    
    '18504': '18504 : Metformin Weight Loss Program',
    '18495': '18495 : Comprehensive Metabolic Panel',
    '18494': '18494 : 16-Component Urinalysis',
    '18687': '18687 : Clomid'
}

frontend_test_names_to_code_labcorp = {
    '36 Food Allergy Panel': '15257',
    'Indoor & Outdoor Allergy': '15277',
    'Indoor and Outdoor Allergy': '15277',
    'Female Hormone Standard': '15297',
    'Male Hormone Test': '15298',
    'Male Hormone Standard': '15299',
    'STD Basic': '15245',
    'STD Standard': '15451',
    'STD Complete': '15247',
    'Herpes Standard': '15523',
    'Herpes Complete': '16101',
    'Herpes 1&2 Early Detection': '15544',
    'HIV Standard': '15521',
    'HIV Complete': '15522',
    'HIV P24 Antigen Early Detection': '15543',
    'Thyroid Standard Panel': '15301',
    'Thyroid Complete Panel': '15302',
    'Heavy Metals Test': '15303',
    'Lyme Disease Test': '15304',
    'Sleep & Stress Hormone Test': '15305',
    'Cortisol Test': '15306',
    'Vitamin B Panel': '15307',
    'Vitamin D & Inflammation Test': '15308',
    'Hemoglobin A1C Test': '15309',
    'Cholesterol & Lipids Panel': '15310',
    'Wegovy - Monthly Weight Loss Program': '16823',
    'Weight Loss Program': '19278',
    'Weight Loss Complete Program': '19279',
    'Weight Loss Quarterly Female': '17853',
    'Weight Loss Quarterly Male': '17854',   
    'Acne Treatment Program Female': '17868',    
    'Acne Treatment Program Male': '17867',
    'Celiac Complete': '18488',
    'Female Hormone Complete': '18489',
    'Male Hormone Complete': '18492',
    'GLP-1 Weight Loss Program': '19494',
    'GLP-1 Weight Loss Complete Program': '19495',
    'Contrave Weight Loss Program': '18499',
    'Metformin Weight Loss Program': '18500',   
    'Comprehensive Metabolic Panel': '18496',      
    '16-Component Urinalysis': '18493',
    'Clomid': '18689'    
}

frontend_test_names_to_code_quest = {
    'Indoor & Outdoor Allergy': '15259',
    'Indoor and Outdoor Allergy': '15259',
    'Female Hormone Standard': '15311',
    'Ovarian Reserve': '15312',
    'Male Hormone Test': '15313',
    'STD Basic Male': '15248',
    'STD Basic Female': '15249',
    'STD Standard Male': '15450',
    'STD Standard Female': '15449',
    'STD Complete Male': '15252',
    'STD Complete Female': '15253',
    'Herpes Standard': '15515',
    'Herpes Complete': '15516',
    'Herpes 1&2 Early Detection': '15542',
    'HIV Standard': '15513',
    'HIV Complete': '15514',
    'HIV P24 Antigen Early Detection': '15545',
    'Thyroid Standard Panel': '15316',
    'Thyroid Complete Panel': '15317',
    'Heavy Metals Test': '15318',
    'Lyme Disease Test': '15319',
    'Sleep & Stress Hormone Test': '15320',
    'Cortisol Test': '15321',
    'Vitamin B Panel': '15322',
    'Vitamin D & Inflammation Test': '15323',
    'Hemoglobin A1C Test': '15324',
    'Cholesterol & Lipids Panel': '15325',
    'Wegovy - Monthly Weight Loss Program': '16822',
    'Weight Loss Program': '19276',
    'Weight Loss Complete Program': '19277',
    'Weight Loss Quarterly Female': '17855',
    'Weight Loss Quarterly Male': '17856',
    'Acne Treatment Program Female': '17864',    
    'Acne Treatment Program Male': '17865',
    'Celiac Complete': '18487',
    'Female Hormone Complete': '18490',
    'Male Hormone Complete': '18491',
    'GLP-1 Weight Loss Program': '19496',
    'GLP-1 Weight Loss Complete Program': '19497',
    'Contrave Weight Loss Program': '18503',
    'Metformin Weight Loss Program': '18504',
    'Comprehensive Metabolic Panel': '18495',
    '16-Component Urinalysis': '18494',
    'Clomid': '18687'    
}

frontend_test_names_to_health_gorilla = {
    '36 Food Allergy Panel': 'Food Allergy Panel',
    'Indoor & Outdoor Allergy': 'Indoor Outdoor Allergy',
    'Indoor and Outdoor Allergy': 'Indoor Outdoor Allergy',
    'Celiac Complete': 'Celiac',
    'Female Hormone Complete': 'Female Hormone',
    'Female Hormone Standard': 'Ovarian Reserve',
    'Male Hormone Test': 'Male Hormone',
    'Male Hormone Standard': 'Testosterone',
    'STD Basic': 'STD Basic',
    'STD Standard': 'STD Standard',
    'STD Complete': 'STD Complete',
    'Herpes Standard': 'Herpes Standard',
    'Herpes Complete': '15516',
    'Herpes 1&2 Early Detection': '15542',
    'HIV Standard': 'HIV Standard',
    'HIV Complete': 'HIV Complete',
    'HIV P24 Antigen Early Detection': 'HIV RNA',
    'Thyroid Standard Panel': 'Thyroid Standard',
    'Thyroid Complete Panel': 'Thyroid Complete',
    'Heavy Metals Test': 'Heavy Metals (Scarlet)',
    'Lyme Disease Test': 'Lyme Disease',
    'Sleep & Stress Hormone Test': '15320',
    'Cortisol Test': 'Cortisol',
    'Vitamin B Panel': 'Vitamin B Panel',
    'Vitamin D & Inflammation Test': 'Vitamin D & Inflammation',
    'Hemoglobin A1C Test': 'Hemoglobin A1c',
    'Cholesterol & Lipids Panel': 'Cholesterol & Lipids Panel',
    'Metformin Weight Loss Program': 'Wegovy/Metformin (Weight Loss)',
    'Contarve Weight Loss Program': 'Wegovy/Contrave (Weight Loss)',
    'Wegovy - Monthly Weight Loss Program': 'Wegovy/Metformin (Weight Loss)',
    'GLP-1 Weight Loss Program': 'Weight Loss Program',
    'GLP-1 Weight Loss Complete Program': 'Weight Loss Complete Program',
    'Weight Loss Quarterly Female': 'Weight Loss Quarterly Female',
    'Weight Loss Quarterly Male': 'Weight Loss Quarterly Male',
    'Acne Treatment Program Female': 'Acne Treatment Program Female',    
    'Acne Treatment Program Male': 'Acne Treatment Program Male',
    'Weight Loss Program': 'Weight Loss Program',
    'Weight Loss Compete Program': 'Weight Loss Complete Program'
}

button_send_order = '//*[@id="lab-order-form"]/div/form/div[3]/button[1]'

health_gorilla_test_names_mapper = {
    'Food Allergy Panel': 'Z91.018',
    'HIV RNA': 'B20',
    'STD Basic': 'Z11.3',
    'STD Standard': 'z11.3',
    'STD Complete': 'z11.3',
    'Celiac': 'R10.9',
    'Female Hormone': 'Z13.29',
    'Ovarian Reserve': 'Z13.29',
    'Food Allergy (Scarlet)': 'Z91.018',
    'Trich': '',
    'Male Hormone': 'Z13.29',
    'Thyroid Standard': 'Z13.29',
    'Thyroid Complete': 'Z13.29',
    'Herpes Standard': 'B00.9',
    'HIV Standard': 'B20',
    'Scarlet': '',
    'Acne Treatment Program': 'r94.5',
    'Weight Loss Quarterly Female': 'Z13.29',
    'Weight Loss Program': 'Z13.29',
    'Weight Loss Complete Program': 'Z13.29'
    # 'Weight Loss Quarterly Female': 'Z13.29',
    
}


class DrChronoNewLabOrder(BaseModel):
    patient_id: int
    patient_gender: str
    order_type: str
    bill_to: str
    test_names: list


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

    return wrapper


def wait_clickable(driver, xpath, timeout=5):
    wait = WebDriverWait(driver, timeout)
    element = wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
    return element


class NewLabOrder:

    def __init__(self):
        logger.debug("Initializing object...")
        self.icd_10_codes = []
        chrome_options = Options()
        if which_os != 'Windows':
            chrome_options.add_argument("no-sandbox")
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--headless")
        chrome_options.add_argument('--start-maximized')
        chrome_options.add_argument('--window-size=2560,1440')
        #chrome_options.add_experimental_option('w3c', False)
        self.driver = webdriver.Chrome(options=chrome_options, executable_path=chromedriver_path)
        self.driver.implicitly_wait(10)

    @retry
    def login(self, username, password):
        logger.debug("Login...")
        self.driver.get(url_login)
        time.sleep(5)

        element = self.driver.find_element_by_id("username")
        element.send_keys(username)

        element = self.driver.find_element_by_id("password")
        element.send_keys(password)

        self.driver.find_element_by_id("login").click()

    @retry
    def switch_account(self, switch_to='Marc Serota'):
        element = self.driver.find_element(By.ID, "switch-button")
        ActionChains(self.driver).click(element).perform()
        option = self.driver.find_element(By.LINK_TEXT, switch_to)
        ActionChains(self.driver).click(option).perform()

    @retry
    def new_lab_order(self, patient_id, order_type):
        logger.info(f"order_type={order_type} for patient_id={patient_id}")
        url_lab_order = f"https://nextmedical.drchrono.com/misc/labs/{patient_id}/"
        self.driver.get(url_lab_order)

        time.sleep(5)

        # click dropdown
        element = self.driver.find_element_by_xpath(new_order_dropdown)
        ActionChains(self.driver).click(element).perform()

        # click dropdown menu
        orderOption = self.driver.find_element_by_link_text(order_type)
        ActionChains(self.driver).click(orderOption).perform()

    @retry
    def quest_wdl(self):
        # select WDL from dropdown
        select = Select(self.driver.find_element_by_xpath(xpath_dropdown_quest_wdl))
        select.select_by_value('9')

    @retry
    def labcorp_bill_type(self, insurance):
        # select dropdown
        select = Select(self.driver.find_element_by_xpath(xpath_dropdown_labcorp_bill_type))
        if insurance is False:
            select.select_by_value('0')
        else:
            select.select_by_value('1')

    @retry
    def fill_icd_10_codes(self, codes):
        time.sleep(1)
        # select icd-10 codes
        element = self.driver.find_element_by_id(id_icd_10_codes)
        element.send_keys(codes)
        time.sleep(2)
        element.send_keys(Keys.RETURN)

    def add_icd_10_codes(self, favorite):
        code = icd_10_codes_test_mapper.get(favorite)
        if code and code not in self.icd_10_codes:
            logger.debug(f"adding {code} to icd_10_codes.")
            self.icd_10_codes.append(code)
            return
        if favorite in ['15518', '15517', '15519', '15520', '15253', '15252', '15449', '15450',
                        '15247', '15525', '15526', '15451']:
            for cod in ['B20', 'B00.9', 'z11.3']:
                if cod not in self.icd_10_codes:
                    logger.debug(f"adding {cod} to icd_10_codes.")
                    self.icd_10_codes.append(cod)
        elif favorite == '16823':
            for cod in ['z13.1', 'z13.29', 'E51.9']:
                if cod not in self.icd_10_codes:
                    logger.debug(f"adding {cod} to icd_10_codes.")
                    self.icd_10_codes.append(cod)

    @retry
    def select_bill_to(self, bill_to):
        time.sleep(2)
        xpath = bill_to_radio_button[bill_to]
        element = self.driver.find_element_by_xpath(xpath)
        if element.get_property('disabled'):
            logger.warning(f"{bill_to} is disabled. Selecting 'Patient' instead...")
            xpath = bill_to_radio_button['Patient']
            element = self.driver.find_element_by_xpath(xpath)
        element.click()

    @retry
    def add_favorite(self, favorite, labcorp=True):
        time.sleep(2)
        # click dropdown
        dropdown = self.driver.find_element_by_xpath(xpath_dropdown_load_a_favorite)
        ActionChains(self.driver).click(dropdown).perform()

        # click dropdown menu
        if labcorp:
            text = text_dropdown_load_a_favorite_menu_labcorp[favorite]
        else:
            text = text_dropdown_load_a_favorite_menu_quest[favorite]
        # myOption = self.driver.find_element_by_xpath(xpath)
        myOption = self.driver.find_element_by_link_text(text)
        # myOption = self.driver.find_element_by_partial_link_text(text)
        ActionChains(self.driver).click(myOption).perform()

    @retry
    def send_order(self):
        logger.info("Sending lab order now...")
        self.driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
        time.sleep(2)
        element = self.driver.find_element_by_xpath(button_send_order)
        time.sleep(2)
        element.click()

    def send_drchrono_task(self, patient_id, order_type, bill_to, tests):
        try:
            if order_type.lower() == "labcorp":
                testsnames = [text_dropdown_load_a_favorite_menu_labcorp[i] for i in tests]
                testsnames = '-'.join([str(elem) for elem in testsnames])
            elif order_type.lower() == "quest":
                testsnames = [text_dropdown_load_a_favorite_menu_quest[i] for i in tests]
                testsnames = '-'.join([str(elem) for elem in testsnames])
            else:
                testsnames = '-'.join([str(elem) for elem in tests])
            dr_chrono_task_data = {
                "title": f"{testsnames}-{bill_to}-{order_type}",
                "status": 2,
                "assignee_user": 438633,
                "associated_items": [{
                    "type": "Patient",
                    "value": patient_id
                }]
            }
            logger.debug(f"creating task: {dr_chrono_task_data}")
            response = drchrono.tasks_create(dr_chrono_task_data)
        except Exception as e:
            logger.exception(e)

    def workflow(self, order_details):
        logger.info("Starting")
        self.icd_10_codes.clear()
        self.login(DRCHRONO_USERNAME, DRCHRONO_PASSWORD)
        # select radio button
        time.sleep(5)
        self.switch_account()
        client = DBClient()
        patient_id = order_details.get('patient_id')
        order_type = order_details.get('order_type')
        favorites = order_details.get('test_names')
        bill_to = order_details.get('bill_to')

        if order_type.lower() == "labcorp":
            insurance_info = False
            insurance = False
            try:
                res = client.get_visits_by_patient_id(patient_id)
                visit = res.get("data")
                if visit.get("insurance_payer_id") == 'None' or visit.get("insurance_payer_id") is None:
                    insurance_info = False
                else:
                    insurance_info = True
                if visit.get("insurance").lower() == 'yes':
                    insurance = True
                else:
                    insurance = False
            except Exception as e:
                logger.exception(e)
            self.new_lab_order(patient_id, "LabCorp")
            self.labcorp_bill_type(insurance_info)
            for favorite in favorites:
                self.add_favorite(favorite)
                self.add_icd_10_codes(favorite)
            for codes in self.icd_10_codes:
                self.fill_icd_10_codes(codes)
            if insurance_info is True:
                self.select_bill_to('Insurance')
            # elif insurance is False:
            #    self.select_bill_to('Patient')
            else:
                self.select_bill_to('Doctor')
        elif order_type.lower().startswith("quest"):
            self.new_lab_order(patient_id, "Quest Diagnostics")
            self.quest_wdl()
            for favorite in favorites:
                self.add_favorite(favorite, labcorp=False)
                self.add_icd_10_codes(favorite)
            for codes in self.icd_10_codes:
                self.fill_icd_10_codes(codes)

            if bill_to.lower().startswith("patient"):
                self.select_bill_to('Patient')
            elif bill_to.lower().startswith("insurance"):
                self.select_bill_to('Insurance')
            else:
                self.select_bill_to('Doctor')
        else:
            logger.error(f"Unknown order_type: {order_type}. Exiting.")
            self.driver.close()
            logger.info("Finished")
            return

        time.sleep(1)
        self.send_order()

        try:
            wait = WebDriverWait(self.driver, 30)
            wait.until(EC.text_to_be_present_in_element(
                (By.XPATH, '//*[@id="content1"]/div[3]/div/div/div/div[2]/div/div/div[2]/div/h2'),
                'Print and Send With Sample / Patient'))
            logger.info(f"Successfully sent Lab Order for {patient_id}.")
        except Exception as e:
            logger.exception(e)
            client.send_patient_failed_order_email(patient_id)
            logger.error(f"Something went wrong for {patient_id}")
            logger.info(
                f'Sending drchrono task for patient_id={patient_id}, order_type={order_type}, bill_to={bill_to}, test_names={order_details.get("test_names")}')
            self.send_drchrono_task(patient_id, order_type, bill_to, order_details.get('test_names'))
        finally:
            self.driver.close()
        logger.info("Finished")

    def new_lab_order_health_gorilla(self, patient_id):
        logger.info(f"order_type=Health Gorilla for patient_id={patient_id}")
        url_lab_order = f"https://nextmedical.drchrono.com/patient/{patient_id}/integration/283/"
        self.driver.get(url_lab_order)

        time.sleep(10)

        # click dropdown
        self.driver.execute_script("window.scrollTo(0,document.body.scrollHeight/4);")

        # change to iframe
        self.driver.switch_to.frame(1)
        time.sleep(2)

    @retry
    def health_gorilla_place_new_order(self):
        element = self.driver.find_element_by_link_text("Place New Order")
        time.sleep(2)
        element.click()
        #ActionChains(self.driver).click(element).perform()

    @retry
    def health_gorilla_place_new_order_menu(self):
        time.sleep(2)
        # click dropdown menu
        orderOption = self.driver.find_element_by_xpath('/html/body/div[3]/div/div/div/div[1]/span')
        orderOption.click()

    @retry
    def health_gorilla_select_vendor(self):
        xpath1 = '//*[@id="container"]/div[2]/div/div/div[3]/div/div/div/div/div[1]/div[1]/div/div/div/div[2]'
        xpath2 = '//*[@id="container"]/div[2]/div/div/div[3]/div/div/div/div/div[1]/div[1]/div/div/div[2]/div[2]'
        for xpath in [xpath1, xpath2]:
            element = self.driver.find_element_by_xpath(xpath)
            if element.text == 'BioReference Lab':
                element.click()
                break

        '''button_continue_xpath = '//*[@id="container"]/div[2]/div/div/div[2]/div/div/div[1]/div[2]/a[3]'
        element = self.driver.find_element_by_xpath(button_continue_xpath)
        element.click()'''
        self.driver.find_element_by_link_text('Continue').click()

    @retry
    def health_gorilla_select_test(self, test_name):
        element = self.driver.find_element_by_link_text(test_name)
        #coordinates = element.location_once_scrolled_into_view  # returns dict of X, Y coordinates
        #self.driver.execute_script("coordinates=arguments[0].getBoundingClientRect();window.frames[1].contentWindow.scrollTo(coordinates.x, coordinates.y);", element)
        #self.driver.execute_script("arguments[0].scrollIntoView();", element)
        time.sleep(2)
        element.click()

    def health_gorilla_select_all_tests(self, test_names):
        for test in test_names:
            self.health_gorilla_select_test(test)
            time.sleep(2)

        # click continue
        self.driver.find_element_by_link_text('Continue').click()

    def health_gorilla_add_icd_10_codes(self, test_names):
        for favorite in test_names:
            code = health_gorilla_test_names_mapper.get(favorite)
            if code and code not in self.icd_10_codes:
                logger.debug(f"adding {code} to icd_10_codes.")
                self.icd_10_codes.append(code)
            if favorite in ['STD Standard', 'STD Complete']:
                for cod in ['B20', 'B00.9', 'z11.3']:
                    if cod not in self.icd_10_codes:
                        logger.debug(f"adding {cod} to icd_10_codes.")
                        self.icd_10_codes.append(cod)
            elif favorite == 'Wegovy/Metformin (Weight Loss)':
                for cod in ['z13.1', 'z13.29', 'E51.9']:
                    if cod not in self.icd_10_codes:
                        logger.debug(f"adding {cod} to icd_10_codes.")
                        self.icd_10_codes.append(cod)

    def health_gorilla_select_patient_diagnoses(self, codes: str):
        textbox_xpath = '//*[@id="container"]/div[2]/div/div/div[3]/div/div[1]/div/div/div[1]/div[2]/div/div/div/span[2]'
        textbox_x_xpath = '//*[@id="container"]/div[2]/div/div/div[3]/div/div[1]/div/div/div[1]/div[2]/div/div/div/span[3]'
        time.sleep(1)
        element = self.driver.find_element_by_xpath(textbox_xpath)
        self.driver.execute_script("arguments[0].scrollIntoView();", element)
        element.send_keys(codes)
        self.driver.find_element_by_xpath("/html/body/div[3]/div/div/div/div").click()
        d = self.driver.find_element_by_xpath(textbox_x_xpath)
        d.click()

    def health_gorilla_select_patient_all_diagnoses(self):
        for codes in self.icd_10_codes:
            self.health_gorilla_select_patient_diagnoses(codes)
        # click continue
        self.driver.find_element_by_link_text('Continue').click()

    def health_gorilla_unselect_print(self):
        self.driver.find_element_by_xpath(
            '//*[@id="container"]/div[2]/div/div/div[2]/div/div/div[2]/div[2]/div[1]/span/span[2]').click()

    def health_gorilla_submit_order(self):
        self.driver.find_element_by_link_text('Submit').click()
        time.sleep(5)
        self.driver.switch_to.default_content()

    def workflow_health_gorilla(self, order_details):
        logger.info("Starting")

        self.icd_10_codes.clear()

        self.login(DRCHRONO_USERNAME, DRCHRONO_PASSWORD)
        # select radio button
        time.sleep(5)

        patient_id = order_details.get('patient_id')
        order_type = order_details.get('order_type')
        test_names = order_details.get('test_names')

        self.new_lab_order_health_gorilla(patient_id)
        self.health_gorilla_place_new_order()
        self.health_gorilla_place_new_order_menu()
        self.health_gorilla_select_vendor()
        self.health_gorilla_select_all_tests(test_names)
        self.health_gorilla_add_icd_10_codes(test_names)
        self.health_gorilla_select_patient_all_diagnoses()
        self.health_gorilla_unselect_print()
        self.health_gorilla_submit_order()

        logger.info("Finished")


def drchrono_send_new_lab_order(order_details: DrChronoNewLabOrder):
    order = NewLabOrder()
    lab_order = order_details.dict()
    logger.info(f"Adding lab order: {lab_order}")
    if lab_order.get('order_type').lower() == 'bioreference':
        order.workflow_health_gorilla(lab_order)
    else:
        order.workflow(lab_order)


if __name__ == '__main__':
    data = {
        'patient_id': 107224583,
        'patient_gender': 'female',
        'order_type': 'quest',
        'bill_to': 'insurance',
        'test_names': ['Ovarian Reserve']
    }
    lab = DrChronoNewLabOrder(**data)
    drchrono_send_new_lab_order(lab)
