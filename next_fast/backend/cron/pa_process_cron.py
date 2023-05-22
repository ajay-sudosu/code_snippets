import datetime
import json
import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import logging
from selenium.webdriver.support.ui import WebDriverWait
import platform
import requests
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path
from config import CMM_USERNAME, CMM_PASSWORD
from database.crud import CMMPAResultsCrud, VisitsCrud, QuestionCrud
from database.db import get_db
from pydantic import BaseModel
from mdintegrations import mdi_weightloss
from healthie import healthie
from utils import send_text_email
from webdriver_manager.chrome import ChromeDriverManager

# logging
logger = logging.getLogger('pa_process_cron')
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s : %(levelname)s : %(funcName)s : %(message)s')

log_dir = os.path.join(os.getcwd(), 'log')
logging_file = os.path.join(
    log_dir,
    os.path.splitext(os.path.basename(__file__))[0] + datetime.datetime.now().strftime('%y%m%d') + '.log'
)
fh = TimedRotatingFileHandler(logging_file, when='d', interval=1, backupCount=10)
fh.setLevel(logging.DEBUG)
fh.setFormatter(formatter)
logger.addHandler(fh)

chromedriver_path = './chromedriver.exe'
which_os = platform.system()
if which_os == 'Windows':
    chromedriver_path = '../chromedriver.exe'
service = Service(chromedriver_path)
db_session = next(get_db())

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
    "rybelsus": [{"partner_medication_id": "9720d65f-52be-4167-85ea-e0298b227dfa"},
                 {"partner_medication_id": "d0fc7951-cf0b-40bc-b813-ebfb0aefb54a"},
                 {"partner_medication_id": "2170e453-ae7d-4add-8f60-2a04049753b1"}],
    "contrave": [{"partner_medication_id": "a48873c4-5dbe-4e70-8ec0-4bb8ee1e90c1"},
                 {"partner_medication_id": "80c613a8-b8c8-411a-bd51-3e22d3d51d38"},
                 {"partner_medication_id": "5ea2e31a-fb67-410b-93b8-1d2765f0a7f1"},
                 {"partner_medication_id": "7923232d-a76d-4460-aaad-798779020d3c"},
                 {"partner_medication_id": "e69ee577-943d-4938-8cc3-67705e0570ed"}],
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


class PAResponse(BaseModel):
    id: str
    sent_at_ts: datetime.datetime
    pa_status: str
    name: str
    drug_info: str


class PAProcessCron:

    def __init__(self):
        self.today = datetime.datetime.now()
        logger.debug("Initializing object...")
        chrome_options = Options()
        if which_os != 'Windows':
            chrome_options.add_argument("no-sandbox")
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--headless")
        chrome_options.add_argument('--start-maximized')
        chrome_options.add_argument('--window-size=2560,1440')
        # chrome_options.add_experimental_option('w3c', False)
        #self.driver = webdriver.Chrome(options=chrome_options, service=service)
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options,)
        self.driver.implicitly_wait(20)
        self.wait = WebDriverWait(self.driver, 20)
        self.session = requests.Session()
        self.pa_results = None
        self.pa_result = None
        self.list_of_pa_ids = []
        self.list_of_pa_ids_filename = 'pa_done_ids_list.json'
        self.load_list_of_pa_ids()

    def __del__(self):
        self.save_list_of_pa_ids()

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

    def cmm_scraping(self):
        try:
            selenium_user_agent = self.driver.execute_script("return navigator.userAgent;")
            self.session.headers.update({"user-agent": selenium_user_agent})

            for cookie in self.driver.get_cookies():
                self.session.cookies.set(cookie['name'], cookie['value'], domain=cookie['domain'])

            page = 1
            while page < 2894:
                try:
                    url = f"https://portal.covermymeds.com/requests/sent/{page}?_data=routes/requests/$tab.$page"
                    response = self.session.get(url)
                    data = response.json()
                    self.handle_data(data)
                    self.save_list_of_pa_ids()
                except Exception as e:
                    logger.exception(e)
                page += 1
        except Exception as e:
            logger.exception(e)

    def handle_data(self, data):
        responses = data.get('requests')
        for res in responses:
            try:
                sent_at = res.get('sentAt').replace('rd', '').replace('nd', '').replace(' 1st', ' 01')\
                    .replace('21st', '21').replace('31st', '31').replace('th', '').replace(' 1,', ' 01,')\
                    .replace(' 2,', ' 02,').replace(' 3,', ' 03,').replace(' 4,', ' 04,').replace(' 5,', ' 05,').\
                    replace(' 6,', ' 06,').replace(' 7,', ' 07,').replace(' 8,', ' 08,').replace(' 9,', ' 09,')
                sent_at_ts = datetime.datetime.strptime(sent_at, "%B %d, %Y")
                pa_status = res.get('status').get('value')
                _id = res.get('id')
                title = res.get('title')
                name = title.split('(')[0].strip()
                drug_info = res.get('drugInfo')

                if _id in self.list_of_pa_ids:
                    logger.info(f"{name} {_id} {drug_info} {pa_status} already handled. skipping...")
                    continue

                pa_response = PAResponse(
                    id=_id,
                    sent_at_ts=sent_at_ts,
                    pa_status=pa_status,
                    name=name,
                    drug_info=drug_info
                )

                self.pa_results = CMMPAResultsCrud.find_by_name(db_session, name=name)
                if len(self.pa_results) == 0:
                    logger.error(f"No Row found for {name}")
                    continue
                elif len(self.pa_results) == 1:
                    self.pa_result = self.pa_results[0]
                else:
                    # choose correct row
                    # check if same email
                    pa_result = self.pa_results[0]
                    for result in self.pa_results:
                        if result.email != pa_result.email:
                            logger.info("mismatch found -> send email to support to handle")
                            # mismatch found -> send email to support to handle
                            subject = "PA results: Multiple rows found."
                            content = f"{pa_response.json()}"
                            send_text_email(
                                sender='team@joinnextmed.com',
                                recipient='team@joinnextmed.com',
                                subject=subject,
                                content=content
                            )
                            break
                    else:
                        self.pa_result = self.pa_results[0]
                    if not self.pa_result:
                        continue
                self.response_handle(pa_response)
            except Exception as e:
                logger.exception(e)

    def response_handle(self, pa_response: PAResponse):
        # find visits by mrn
        visit = VisitsCrud.get_visits_by_mrn(db_session, mrn=self.pa_result.mrn)
        if not visit:
            logger.warning(f"invalid mrn: {self.pa_result.mrn}")
            return
        if pa_response.pa_status == 'PA Response - Approved':
            logger.info(f"Handling PA Response - Approved for {pa_response.name}")
            try:
                if visit.get('email') in self.list_of_pa_ids:
                    logger.info(f"already created case for {visit.get('email')}. skipping...")
                    return
                drug = self.get_drug_name(pa_response.drug_info)
                VisitsCrud.update_visits_weight_medicine_type_by_mrn(
                    db_session,
                    mrn=visit.get('mrn'),
                    value=drug
                )
                if visit.get('is_healthie') != '1':
                    # create mdi case
                    self.create_mdi_case(visit, drug=drug, patient_id_md=None)
                else:
                    # write healthie task write_erx - metformin
                    if visit.get('healthie_id'):
                        if visit.get('first_visit') == 1:
                            data = {    
                                "user_id": visit.get('healthie_id'),
                                "finished": True,
                                "form_answers": [{
                                    "custom_module_id": "15009383",
                                    "answer": pa_response.drug_info,
                                    "user_id": visit.get('healthie_id')
                                    }, 
                                    {
                                    "custom_module_id": "15009384",
                                    "answer": f"{pa_response.pa_status} pa_status_1",
                                    "user_id": visit.get('healthie_id')
                                    }]
                            }
                            logger.info(f"SENDING PA FORN TO HEALTHIE WITH DATA={data}")
                            healthie.creating_filled_out_pa_forms(data)
                            # self.create_healthie_task(visit, drug=drug)
                        else:
                            logger.info("Customer with name=" + str(pa_response.name) + " has not had their first visit yet...")
                    else:
                        logger.error("Customer with name=" + str(pa_response.name) + "does not have an associated healthie_id in the database")
                self.list_of_pa_ids.append(visit.get('email'))
                CMMPAResultsCrud.update_pa_processed_by_mrn(
                    db_session,
                    mrn=visit.get('mrn'),
                    pa_processed=True
                )
            except Exception as e:
                logger.error("Handling pa response error=" + str(e) + "for customer=" + str(pa_response.name) + "and status=" + str(pa_response.pa_status))
        elif pa_response.pa_status == 'PA Response - Denied':
            logger.info(f"Handling PA Response - Denied for {pa_response.name}")
            if pa_response.id in self.list_of_pa_ids:
                logger.info(f"already send email to support")
                return
            # just send a mail to support for now
            subject = "PA Response - Denied"
            content = f"{pa_response.json()}"
            send_text_email(
                sender='team@joinnextmed.com',
                recipient='team@joinnextmed.com',
                subject=subject,
                content=content
            )
            self.list_of_pa_ids.append(pa_response.id)
            return

            try:
                # set rejected all to True
                CMMPAResultsCrud.update_rejected_all_by_mrn(
                    db_session,
                    mrn=self.pa_result.mrn,
                    rejected_all=True
                )

                if 'semaglutide' in visit.get('backup_medicine').lower():
                    VisitsCrud.update_visits_weight_medicine_type_by_mrn(
                        db_session,
                        mrn=visit.get('mrn'),
                        value='semaglutide'
                    )
                    if visit.is_healthie != '1':
                        mdi_weightloss.add_pharmacy_to_patient(visit.get('patient_id_md'), 245312, True)
                        # create mdi case
                        self.create_mdi_case(visit, drug='semaglutide', patient_id_md=None)
                    else:
                        # healthie patient
                        # create mdi patient
                        patient_id_md = self.create_patient_to_mdi(visit)
                        if patient_id_md:
                            # set visit.is_healthie to 0
                            mdi_weightloss.add_pharmacy_to_patient(patient_id_md, 245312, True)
                            # create mdi case
                            self.create_mdi_case(visit, drug='semaglutide', patient_id_md=patient_id_md)
                elif 'contrave' in visit.get('backup_medicine').lower():
                    if visit.contrave_issues:
                        # cann't take contrave, go to metformin
                        VisitsCrud.update_visits_weight_medicine_type_by_mrn(
                            db_session,
                            mrn=visit.get('mrn'),
                            value='metformin'
                        )
                        if visit.get('is_healthie') != '1':
                            # create mdi case
                            self.create_mdi_case(visit, drug='metformin', patient_id_md=None)
                        else:
                            # write healthie task write_erx - metformin
                            self.create_healthie_task(visit, drug='metformin')
                    else:
                        VisitsCrud.update_visits_weight_medicine_type_by_mrn(
                            db_session,
                            mrn=visit.get('mrn'),
                            value='contrave'
                        )
                        if visit.get('is_healthie') != '1':
                            # create mdi case
                            self.create_mdi_case(visit, drug='contrave', patient_id_md=None)
                        else:
                            # write healthie task write_erx - contrave
                            self.create_healthie_task(visit, drug='contrave')
                self.list_of_pa_ids.append(pa_response.id)
            except Exception as e:
                logger.exception(e)
        else:
            #todo
            pass

    @staticmethod
    def create_patient_to_mdi(patient_data):
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
        logger.info(f"creating mdi patient: {data}")
        res = mdi_weightloss.create_patient(data)
        logger.debug(res)
        if 'patient_id' in res:
            patient_id = res.get('patient_id')
            try:
                VisitsCrud.update_visits_patient_id_md_by_email(db_session, patient_data.get('email'), patient_id)
            except Exception as e:
                logger.exception("switch_patient_to_mdi => " + str(e))
            return patient_id
        return None

    @staticmethod
    def create_mdi_case(visit, drug: str, patient_id_md: str=None):
        try:
            db_questions = QuestionCrud.get_question_by_mrn(db_session, visit.get('mrn'))
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
            if not patient_id_md:
                patient_id_md = visit.get('patient_id_md')
            data = {
                'patient_id': patient_id_md,
                'case_prescriptions': medication_keys.get(drug)
            }
            if questions:
                data['case_questions'] = questions
            logger.info(f"creating case: {data}")
            res = mdi_weightloss.create_case(data)
            logger.debug(res)
        except Exception as e:
            logger.exception(e)

    @staticmethod
    def create_healthie_task(visit, drug: str):
        try:
            healthie_create_task_data = {
                "user_id": "1627246",
                "content": "write_erx - " + drug,
                "client_id": visit.get('healthie_id'),
                "due_date": datetime.date.today().strftime('%Y-%m-%d'),
                "reminder": {
                    "is_enabled": True,
                    "interval_type": "daily",
                    "interval_value": "friday",
                    "remove_reminder": True
                }
            }
            logger.info(f"creating healthie task: {healthie_create_task_data}")
            healthie.create_task(healthie_create_task_data)
        except Exception as e:
            logger.exception(e)

    @staticmethod
    def get_drug_name(drug_string: str):
        drug_list = ("mounjaro", "ozempic", "wegovy", "saxenda", "rybelsus", "victoza", "trulicity", "contrave")
        drug_string = drug_string.lower()
        for drug in drug_list:
            if drug in drug_string:
                return drug
        return "NA"

    def notify_logic(self, sent_at_ts, pa_status):
        # todo
        pass

    @staticmethod
    def notify(email: str, message: str):
        SENDER = 'team@joinnextmed.com'
        logger.debug(f"Sending email to {email}")
        subject = "NextMed PA Process Updates"
        send_text_email(sender=SENDER, recipient=email, subject=subject, content=message)

    def notify_day_1(self, name, email):
        message = f"""Hi {name}, thanks for completing your intake form and all requirements. 
        We are now starting your prior authorization process to get your medication covered by insurance. 
        This takes about 2 weeks on average so please sit tight and we will update you as things progress. 
        Please reach out to team@joinnextmed.com if you have any questions in the meantime."""
        self.notify(email, message)

    def notify_day_3(self, name, email):
        message = f"""Hi {name}, just a quick update. We've filed all the necessary paperwork with your insurance 
        company and are just waiting to hear back. We will keep you posted. On average, your PA may take about 
        another 2 weeks to get back."""
        self.notify(email, message)

    def notify_day_7(self, name, email):
        message = f"""Hi {name}, can you believe it's been a week? We're still waiting for your insurance 
        plan to get back to us. We'll share updates once we have them."""
        self.notify(email, message)

    def notify_day_14(self, name, email):
        message = f"""Hi {name}, unfortunately we're still waiting for your insurance plan. 
        We'll let you know once we have an update."""
        self.notify(email, message)

    def notify_day_21(self, name, email):
        message = f"""Hi {name}, we're still waiting for your plan to approve your PA. 
        We are working through a list of possible medications to get you covered which is causing some delays. 
        We will keep you posted."""
        self.notify(email, message)

    def notify_day_28(self, name, email):
        message = f"""Hi {name}, your insurance plan unfortunately has been very slow to get back to us. 
        We are still processing your PA with them (unfortunately we're waiting too). 
        We will be in touch soon."""
        self.notify(email, message)

    def notify_day_42(self, name, email):
        message = f"""Hi {name}, your plan is still processing your order. At this point, 
        it may make sense to take a generic medication. Please contact us at team@joinnextmed.com so we 
        can help you further. We apologize for the delays in this process, unfortunately much of it 
        is out of our control."""
        self.notify(email, message)

    def workflow(self):
        self.login()
        self.cmm_scraping()
        self.driver.quit()


if __name__ == '__main__':
    cron = PAProcessCron()
    cron.workflow()
