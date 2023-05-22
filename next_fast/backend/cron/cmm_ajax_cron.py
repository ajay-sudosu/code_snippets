import datetime
import json
import logging
import os
import platform
import time
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path
import chromedriver_autoinstaller
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from config import CMM_USERNAME, CMM_PASSWORD
# fresh imports
from database.crud import VisitsCrud, QuestionCrud
from database.db import get_db
from db_client import DBClient
from healthie import healthie
from mdintegrations import mdi_weightloss
from stripe_api import get_subscription, fetch_payment_intent

db_session = next(get_db())
db = DBClient()

CMM_USERNAME = CMM_USERNAME
CMM_PASSWORD = CMM_PASSWORD

preferred_drug_list = ["ozempic", "wegovy", "mounjaro", "saxenda", "rybelsus"]

medication_keys = {
    "ozempic": [{"partner_medication_id": "9541454d-46c0-44b2-970e-73b84b7b70ab"},
                {"partner_medication_id": "1c011b31-693e-4126-b82d-50b3acd05bf1"},
                {"partner_medication_id": "1551ddb3-54b5-4437-9e0d-8746fa867088"},
                {"partner_medication_id": "a4b4b327-606e-48b3-bbc7-d85b461a45b2"},
                {"partner_medication_id": "ea735bc9-6a9a-487d-8842-b465a24d45ee"}],
    "saxenda": [{"partner_medication_id": "c7678b2f-9cda-4560-ba85-8f85c102bae4"},
                {"partner_medication_id": "df80ae5c-51df-4248-87ef-b862cd8acac2"},
                {"partner_medication_id": "ea735bc9-6a9a-487d-8842-b465a24d45ee"},
                {"partner_compound_id": "408c2dee-e2e5-4840-9ad5-f72b5c3f9f16"}],
    "rybelsus": [{"partner_medication_id": "de51d06d-d94b-42c0-8f03-7b56b573eed2"},
                 {"partner_medication_id": "ef86df38-1f42-465f-aa09-6c32a124c2ea"},
                 {"partner_medication_id": "2170e453-ae7d-4add-8f60-2a04049753b1"}],
    "contrave": [{"partner_medication_id": "a48873c4-5dbe-4e70-8ec0-4bb8ee1e90c1"},
                 {"partner_medication_id": "c62e1adf-7dc0-4cc5-8ced-bbadd8048456"}],
    "mounjaro": [{"partner_medication_id": "634dcf1f-5e29-4de3-96ff-4732555c918e"},
                 {"partner_medication_id": "31e83d4c-e1dd-454d-901b-16648f9843b1"},
                 {"partner_medication_id": "e759fb5d-d270-405f-b57c-0583636ec0c3"},
                 {"partner_medication_id": "dbb49aed-afbd-4af0-816b-1c3b86d25a15"},
                 {"partner_medication_id": "ea735bc9-6a9a-487d-8842-b465a24d45ee"}],
    "metformin": [{"partner_medication_id": "a48873c4-5dbe-4e70-8ec0-4bb8ee1e90c1"},
                  {"partner_medication_id": "00ebd86f-7a3b-4cbf-aeec-63f2878e4b6c"}],
    "victoza": [{"partner_medication_id": "ce38fd9b-e1c8-4155-806d-ec730f0255a0"},
                {"partner_medication_id": "328f8dbf-b837-4224-802d-a27875618a11"},
                {"partner_medication_id": "ea735bc9-6a9a-487d-8842-b465a24d45ee"},
                {"partner_compound_id": "328f8dbf-b837-4224-802d-a27875618a11"}],
    "trulicity": [{"partner_medication_id": "e5b0717f-3e0a-4f6d-b59a-a41c4b4faa52"},
                  {"partner_medication_id": "98160dd5-f7e3-40f3-89f5-ba440d0d5b40"},
                  {"partner_medication_id": "fdb5122e-ff5d-4403-83e5-b6face91797b"},
                  {"partner_medication_id": "8479282e-2b4d-4531-9a2f-373dd6aea089"},
                  {"partner_medication_id": "9e34704d-9b62-4d23-a1f3-f43c0cfa8d43"}],
    "wegovy": [{"partner_medication_id": "98a56b60-8e9b-45c0-ad0c-b39f2198f403"},
               {"partner_medication_id": "1c011b31-693e-4126-b82d-50b3acd05bf1"},
               {"partner_medication_id": "1551ddb3-54b5-4437-9e0d-8746fa867088"},
               {"partner_medication_id": "a4b4b327-606e-48b3-bbc7-d85b461a45b2"},
               {"partner_medication_id": "ea735bc9-6a9a-487d-8842-b465a24d45ee"}],
    "semaglutide": [{"partner_compound_id": "4d094cba-c9f8-4ec2-b9f5-52746990657b"},
                    {"partner_compound_id": "97dc914a-7475-44c2-a283-4642294f333b"},
                    {"partner_compound_id": "a76883bb-1a8b-46ed-a07a-07c856ad82fc"},
                    {"partner_compound_id": "cc3531d9-264b-429d-ac27-977414f2a24b"},
                    {"partner_medication_id": "ea735bc9-6a9a-487d-8842-b465a24d45ee"}],
}

# logging
logger = logging.getLogger('cmm_ajax_cron')
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s : %(levelname)s : %(funcName)s : %(message)s')

log_dir = os.path.join(os.getcwd(), 'log')
logging_file = os.path.join(
    log_dir,
    os.path.splitext(os.path.basename(__file__))[0] + datetime.datetime.now().strftime('%y%m%d') + '.log'
)
fh = TimedRotatingFileHandler(logging_file, when='d', interval=1, backupCount=5)
fh.setLevel(logging.DEBUG)
fh.setFormatter(formatter)
logger.addHandler(fh)

chromedriver_path = './chromedriver.exe'
which_os = platform.system()
if which_os == 'Windows':
    chromedriver_path = '../../chromedriver.exe'


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


class CoverMedsAjax:

    def __init__(self):
        #logger.log("Initializing cmm_ajax_cron...")
        options = Options()
        options.add_argument("--headless")
        chromedriver_autoinstaller.install()
        self.driver = webdriver.Chrome(options=options)
        self.driver.implicitly_wait(20)
        self.wait = WebDriverWait(self.driver, 20)
        self.session = requests.Session()
        self.list_of_pa_ids = []
        self.list_of_pa_ids_filename = 'pa_ids_list.json'
        self.load_list_of_pa_ids()

    def load_list_of_pa_ids(self):
        logger.info(f"loading list_of_pa_ids...")
        file = Path(self.list_of_pa_ids_filename)
        if file.is_file():
            with open(file, 'r') as openfile:
                try:
                    self.list_of_pa_ids = json.load(openfile)
                except Exception as e:
                    self.list_of_pa_ids = []
        else:
            self.save_list_of_pa_ids()

    def save_list_of_pa_ids(self):
        logger.info(f"saving list_of_pa_ids: {self.list_of_pa_ids}")
        file = Path(self.list_of_pa_ids_filename)
        with open(file, "w") as outfile:
            json.dump(self.list_of_pa_ids, outfile)

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

    def handle_data(self, data):
        pa_list = data.get('requests', [])
        for PA in pa_list:
            try:
                name = PA.get("name")
                drug_name = self.get_drug_name(PA.get("drug"))
                request_outcome = PA.get("request_outcome")
                if request_outcome == 0:
                    continue
                request_outcome = 2 if PA.get("request_outcome") == "Approved" else 1
                # empty PA or can't find drug for some reason
                if drug_name != "NA":
                    for preferred_drug in preferred_drug_list:
                        if preferred_drug in drug_name.lower():
                            drug_name = preferred_drug
                             # insert drug into pa_results table, Jack's ep
                            res = db.update_pa_results_by_medication(name, drug_name, request_outcome)
                            logger.debug(res)
                   
                    # no row found for given name
                    if res is None:
                        # should eventually add some sort of freshdesk ticketing and sub logic here. 
                        logger.error('No medication found in preferred_drug_list... drug_name=' + str(drug_name))
                        continue
                    # otherwise continue
                    email = res.get('email')
                    rejected_all = res.get('rejected_all')

                    # get necessary visits table data for patient who had an insertion performed
                    data = VisitsCrud.get_visits_row_by_email(db_session, email)
                    if not data:
                        logger.error(f"No visit found for: {email}")
                        continue
                    patient_data = data[0]
                    backup_medicine = patient_data.get('backup_medicine')
                    payment_id = patient_data.get('payment_id')
                    server_date_time = patient_data.get('server_date_time')

                    # check that subscription is still active...
                    if self.is_active_status(payment_id, server_date_time):
                        # check for rejected all 
                        if rejected_all:
                            if backup_medicine == "contrave":
                                contrave_issues = patient_data.get('contrave_issues')
                                if contrave_issues is not None:
                                    # set weight medicine type metformin then pass
                                    res = db.update_weight_loss_medication(email, "metformin")
                                    logger.info("Set to metformin for email=" + str(email))
                                    continue
                                else:
                                    # contrave is good for rx
                                    self.create_rx_case(patient_data, backup_medicine)
                            else:
                                # semaglutide weight medicine type
                                # update weight medicine type
                                is_healthie = patient_data.get('is_healthie')
                                if is_healthie == 1:
                                    # switch patient to MDI
                                    logger.info("Switching patient to MDI for semaglutide...")
                                    self.switch_patient_to_mdi(patient_data)
                                self.create_rx_case(patient_data, backup_medicine)
                        else:
                            if drug_name in preferred_drug_list:
                                # create case with proper medicine, right now do nothing if trulicity or victoza
                                # set weight medicine type
                                self.create_rx_case(patient_data, drug_name)
            except Exception as e:
                logger.exception(e)

    def create_rx_case(self, patient_data, drug_name):
        email = patient_data.get('email')
        logger.info("Creating an rx case for email=" + str(email) + " drug=" + str(drug_name))
        res = db.update_weight_loss_medication(email, drug_name)
        is_healthie = patient_data.get('is_healthie')
        if is_healthie is None or is_healthie == 0:
            patient_id = patient_data.get('patient_id_md')
            # create MDI case
            if drug_name == "semaglutide":
                # switch pharmacy to westchester pharmacy
                gogomeds_pharmacy_id = "245312"
                logger.info("Switching pharmacy to Westchester Pharmacy for Semaglutide...")
                res = mdi_weightloss.add_pharmacy_to_patient(patient_id, gogomeds_pharmacy_id, True)
            # create mdi case
            db_questions = QuestionCrud.get_question_by_mrn(db_session, patient_data.get('mrn'))
            questions = []
            if db_questions:
                for que in db_questions:
                    q = {
                        'question': que.get('questions'),
                        'answer': que.get('answer'),
                        'type': "string",
                        'important': True
                    }
                    questions.append(q)
            data = {
                'patient_id': patient_id,
                'case_prescriptions': medication_keys.get(drug_name)
            }
            if questions:
                data['case_questions'] = questions
            logger.info(f"creating mdi case: {data}")
            res = mdi_weightloss.create_case(data)
            logger.debug(res)
        else:
            # create erx task for openloop
            healthie_create_task_data = {
                "user_id": "1627246",
                "content": "write_erx - " + drug_name,
                "client_id": patient_data.get('healthie_id'),
                "due_date": datetime.date.today().strftime('%Y-%m-%d'),
                "reminder": {
                    "is_enabled": True,
                    "interval_type": "daily",
                    "interval_value": "friday",
                    "remove_reminder": True
                }
            }
            logger.info(f"creating healthie write_erx task: {healthie_create_task_data}")
            healthie.create_task(healthie_create_task_data)

    @staticmethod
    def get_drug_name(drug_string: str):
        drug_list = ("mounjaro", "ozempic", "wegovy", "saxenda", "rybelsus", "victoza", "trulicity", "contrave")
        drug_string = drug_string.lower()
        for drug in drug_list:
            if drug in drug_string:
                return drug
        return "NA"

    def switch_patient_to_mdi(self, patient_data):
        patient_address = patient_data.get('patient_address')
        patient_address_list = patient_address.split(',')
        data = {
            "first_name": patient_data.get('first_name'),
            "last_name": patient_data.get('last_name'),
            "email": patient_data.get('email'),
            "metadata": "",
            "gender": 2 if patient_data.get('gender') == 'female' else 1,
            "phone_number": patient_data.get('phone_number'),
            "phone_type": 2,
            "date_of_birth": patient_data.get('dob'),
            "address": {
                "address": patient_address_list[0].strip(),
                "zip_code": patient_data.get('zip_code'),
                "city_name": patient_address_list[1].strip(),
                "state_name": patient_address_list[2].strip()
            }
        }
        logger.info(f"creating mdi: {data}")
        res = mdi_weightloss.create_patient(data)
        logger.debug(res)
        if 'patient_id' in res:
            patient_id = res.get('patient_id')
            try:
                VisitsCrud.update_visits_patient_id_md_by_email(db_session, patient_data.get('email'), patient_id)
            except Exception as e:
                logger.exception("switch_patient_to_mdi => " + str(e))

    def is_active_status(self, payment_id, server_date_time):
        payment_type = self.get_payment_type(payment_id)
        if payment_type == "affirm":
            return False
        elif payment_type == "prepaid":
            response = fetch_payment_intent(payment_id)
            charge = response["charges"]["data"][0]
            amount_refunded = charge["amount_refunded"]
            if amount_refunded > 50000:
                return False
            return True
        else:
            response = get_subscription(payment_id)
            if 'id' in response:
                if not (response["status"] == "active" or response["status"] == "trialing"):
                    if '-' in server_date_time:
                        booking_ts = datetime.datetime.strptime(server_date_time, "%d-%m-%Y%H:%M:%S")
                    else:
                        booking_ts = datetime.datetime.strptime(server_date_time, "%d/%m/%Y %H:%M:%S")

                    end_date = booking_ts + datetime.timedelta(days=5)
                    db.update_subscription_time_status(end_date, payment_id)
                    return True
            logger.debug("subscription is not in active state")
            return False

    @staticmethod
    def get_payment_type(payment_id):
        vals = payment_id.split("_")
        if len(vals) == 1:
            return "affirm"
        else:
            if vals[0] == "pi":
                return "prepaid"
            else:
                return "sub"

    def ajax_scraping(self):
        try:
            selenium_user_agent = self.driver.execute_script("return navigator.userAgent;")
            self.session.headers.update({"user-agent": selenium_user_agent})

            for cookie in self.driver.get_cookies():
                self.session.cookies.set(cookie['name'], cookie['value'], domain=cookie['domain'])

            response = self.session.get("https://www.covermymeds.com/ajax/list")
            data = response.json()
            logger.info("Received Data! data=" + str(data))
            self.handle_data(data)
        except Exception as e:
            if response:
                logger.exception("response=" + str(response) + " response.content=" + str(response.content) + " error=" + str(e))
            else:
                logger.exception("No response from https://www.covermymeds.com/ajax/list, error=" + str(e))

    def workflow(self):
        """Main business logic"""
        # Run for 1 hour every minute
        max_run_count = 60
        run_count = 0
        logger.info("================ Started ================")
        self.login()
        while run_count < max_run_count:
            self.ajax_scraping()
            run_count += 1
            time.sleep(60)
        self.save_list_of_pa_ids()
        self.driver.quit()
        logger.info("================ Finished ================")


if __name__ == '__main__':
    ajax = CoverMedsAjax()
    ajax.workflow()
