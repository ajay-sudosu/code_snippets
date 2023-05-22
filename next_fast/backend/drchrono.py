import datetime
import json
import logging
import os
import pickle
from enum import Enum
from typing import Optional, List

import pathlib

import boto3
from botocore.client import Config
import requests
from pydantic import BaseModel
from requests_oauthlib import OAuth2Session

from config import DR_CHRONO_CLIENT_ID, DR_CHRONO_CLIENT_SECRET

CLIENT_ID = DR_CHRONO_CLIENT_ID
CLIENT_SECRET = DR_CHRONO_CLIENT_SECRET
AUTHORIZATION_BASE_URL = 'https://drchrono.com/o/authorize/'
TOKEN_URL = 'https://drchrono.com/o/token/'
SCOPE = "patients:read patients:write patients:summary:read patients:summary:write " \
        "calendar:read calendar:write clinical:read clinical:write " \
        "labs:read labs:write user:read user:write tasks:read tasks:write"
REDIRECT_URI = 'https://labintegration.joinnextmed.com'
REFRESH_TOKEN_URL = TOKEN_URL
TOKEN_REFRESH_INTERVAL = 40
#######
logger = logging.getLogger("fastapi")

s3_patient_bucket = "patient-upload"
s3_region = 'us-east-2'
s3_client = boto3.client(
    's3',
    region_name=s3_region,
    aws_access_key_id="AKIAJSZRUVGIPVVOPUGA",
    aws_secret_access_key="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",
    config=Config(
        signature_version='s3v4',
        retries={
            'max_attempts': 3,
            'mode': 'standard'
        }
    )
)

class DrChronoAppointment(BaseModel):
    doctor: int
    patient: int
    office: int
    exam_room: int
    scheduled_time: str
    duration: int
    date_range: Optional[str]
    since: Optional[str]


class DrChronoGender(str, Enum):
    male = "Male"
    female = "Female"
    other = "Other"


class DrChronoPatientInsurance(BaseModel):
    insurance_claim_office_number: str
    insurance_company: str
    insurance_group_name: str
    insurance_group_number: str
    insurance_id_number: str
    insurance_payer_id: str
    insurance_plan_name: str
    insurance_plan_type: str
    is_subscriber_the_patient: bool
    patient_relationship_to_subscriber: Optional[str]
    photo_back: Optional[str]
    photo_front: Optional[str]
    subscriber_address: Optional[str]
    subscriber_city: Optional[str]
    subscriber_country: Optional[str]
    subscriber_date_of_birth: Optional[str]
    subscriber_first_name: Optional[str]
    subscriber_gender: Optional[str]
    subscriber_last_name: Optional[str]
    subscriber_middle_name: Optional[str]
    subscriber_social_security: Optional[str]
    subscriber_state: Optional[str]
    subscriber_suffix: Optional[str]
    subscriber_zip_code: Optional[str]


class DrChronoPatient(BaseModel):
    doctor: int
    gender: DrChronoGender
    first_name: Optional[str]
    middle_name: Optional[str]
    last_name: Optional[str]
    date_of_birth: Optional[str]
    email: Optional[str]
    address: Optional[str]
    city: Optional[str]
    state: Optional[str]
    zip_code: Optional[str]
    cell_phone: Optional[str]
    chart_id: Optional[str]
    copay: Optional[str]
    social_security_number: Optional[str]
    primary_insurance: Optional[DrChronoPatientInsurance]
    secondary_insurance: Optional[DrChronoPatientInsurance]
    tertiary_insurance: Optional[DrChronoPatientInsurance]


class DrChronoLabOrder(BaseModel):
    doctor: int
    patient: int
    sublab: int
    priority: Optional[str]
    requisition_id: Optional[str]
    accession_number: Optional[str]
    documents: Optional[List]
    icd10_codes: Optional[List]
    notes: Optional[str]


class DrChronoTaskPriority(int, Enum):
    low = 10
    medium = 20
    high = 30
    urgent = 40


class DrChronoTaskNotes(BaseModel):
    task: int
    text: str
    created_by: Optional[int]
    archived: Optional[bool]


class DrChronoTask(BaseModel):
    title: str
    status: int
    archived: Optional[bool]
    assigned_by: Optional[int]
    assignee_user: Optional[int]
    assignee_group: Optional[int]
    associated_items: Optional[List]
    category: Optional[int]
    due_date: Optional[dict]
    notes: Optional[DrChronoTaskNotes]
    priority: Optional[DrChronoTaskPriority]


class DrChronoInsuranceQuery(BaseModel):
    payer_type: str
    cursor: Optional[str]
    page_size: Optional[int]
    term: Optional[str]


task_create_examples = {
    "minimal": {
        "summary": "A minimal example",
        "description": "A **minimal** create task payload that works correctly.",
        "value": {
            "title": "Test task",
            "status": 2,
            "assignee_user": 446492,
        },
    },
    "invalid": {
        "summary": "Invalid data is rejected with an error",
        "value": {
            "title": "Test task",
            "status": 2,
            "priority": 20
        },
    },
}


class Drchrono:
    """Client class to interact with DrChrono's API."""

    def __init__(self, client_id, client_secret):
        logger.info("Drchrono object initializing...")
        self.client_id = client_id
        self.client_secret = client_secret
        self.pickle_file = 'drchrono_api_token.pickle'
        self.oauth_client = None
        self.base_url = "https://app.drchrono.com"
        self.authorization_url = None
        self.state = None
        self.token = None
        self.token_ts = datetime.datetime.now()
        self.token_loader()
        # self.refresh_token()

    def token_saver(self, token):
        self.token = token
        with open(self.pickle_file, 'wb') as f:
            # Pickle the self.token using the highest protocol available.
            pickle.dump(token, f, pickle.HIGHEST_PROTOCOL)

    def token_loader(self):
        if not os.path.isfile(self.pickle_file):
            self.authorize()
            return
        with open(self.pickle_file, 'rb') as f:
            self.token = pickle.load(f)
        if self.oauth_client is None:
            extra = {
                'client_id': CLIENT_ID,
                'client_secret': CLIENT_SECRET
            }
            self.oauth_client = OAuth2Session(
                self.client_id,
                token=self.token,
                auto_refresh_url=REFRESH_TOKEN_URL,
                auto_refresh_kwargs=extra,
                token_updater=self.token_saver
            )

    def authorize(self):
        extra = {
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET
        }
        self.oauth_client = OAuth2Session(
            self.client_id,
            scope=SCOPE,
            redirect_uri=REDIRECT_URI,
            auto_refresh_url=REFRESH_TOKEN_URL,
            auto_refresh_kwargs=extra,
            token_updater=self.token_saver
        )
        self.authorization_url, self.state = self.oauth_client.authorization_url(AUTHORIZATION_BASE_URL)
        print("Please go here and authorize: {}".format(self.authorization_url))

        redirect_response = input("Copy & Paste the full redirect URL here then press 'Enter':")

        # Fetch the access token
        self.token = self.oauth_client.fetch_token(
            TOKEN_URL,
            client_secret=CLIENT_SECRET,
            authorization_response=redirect_response
        )
        print(self.token)
        self.token_saver(self.token)

    def refresh_token(self):
        if self.token is None:
            self.token_loader()
        self.oauth_client = OAuth2Session(self.client_id, token=self.token)
        extra = {
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET
        }
        logger.debug("Refreshing token...")
        self.token = self.oauth_client.refresh_token(REFRESH_TOKEN_URL, **extra)
        # return self.token
        self.token_ts = datetime.datetime.now()
        logger.debug(self.token)
        self.token_saver(self.token)

    def get_access_token(self):
        return self.token['access_token']

    def should_refresh_now(self):
        """Refresh token if TOKEN_REFRESH_INTERVAL is up"""
        dt = datetime.datetime.now()
        if dt - self.token_ts > datetime.timedelta(hours=TOKEN_REFRESH_INTERVAL):
            self.refresh_token()

    def _post_request_(self, uri, params=None, body=None):
        """
        Send a requests.post request
        :param uri: Endpoint URI
        :param params: URL Parameters
        :param body: body to be sent with request
        :return: json of response
        """
        url = self.base_url + uri
        logger.debug(params)
        logger.debug(body)
        self.should_refresh_now()

        if body is None:
            res = self.oauth_client.post(url, params=params)
        else:
            res = self.oauth_client.post(url, params=params, json=body)

        request_info = json.dumps({"url": url, "params": params, "body": body, "response": res.text})
        logger.info("drchrono post request ==> " + request_info)
        return res.json()

    def _put_request_(self, uri, params=None, body=None):
        """
        Send a requests.post request
        :param uri: Endpoint URI
        :param params: URL Parameters
        :param body: body to be sent with request
        :return: json of response
        """
        url = self.base_url + uri
        logger.debug(params)
        logger.debug(body)

        self.should_refresh_now()

        if body is None:
            res = self.oauth_client.put(url, params=params)
        else:
            res = self.oauth_client.put(url, params=params, json=body)
        if res.status_code == 201:
            pass
        else:
            logger.debug(res.status_code)

        request_info = json.dumps({"url": url, "params": params, "body": body, "response": res.text})
        logger.info("drchrono put request ==> " + request_info)
        return res.json()

    def _patch_request_(self, uri, params=None, body=None):
        """
        Send a requests.patch request
        :param uri: Endpoint URI
        :param params: URL Parameters
        :param body: body to be sent with request
        :return: json of response
        """
        url = self.base_url + uri
        # logger.debug(params)
        # logger.debug(body)

        self.should_refresh_now()

        if body is None:
            res = self.oauth_client.patch(url, params=params)
        else:
            res = self.oauth_client.patch(url, params=params, json=body)
        if res.status_code == 204:
            return {"status": "success"}
        else:
            logger.debug(res.status_code)
        return res.json()

    def _get_request_(self, uri, params=None):
        """
        Send a requests.post request
        :param uri: Endpoint URI
        :param params: URL Parameters
        :return: json of response
        """
        url = self.base_url + uri
        logger.debug(params)

        self.should_refresh_now()

        res = self.oauth_client.get(url, params=params)
        if res.status_code == 200:
            pass
        else:
            pass
        
        request_info = json.dumps({"url": url, "params": params, "response": res.text})
        logger.info("drchrono get request ==> " + request_info)
        return res.json()

    def _delete_request_(self, uri, params=None):
        """
        Send a requests.delete request
        :param uri: Endpoint URI
        :param params: URL Parameters
        :return: json of response
        """
        url = self.base_url + uri
        logger.debug(params)

        self.should_refresh_now()

        res = self.oauth_client.delete(url, params=params)
        logger.debug(res.status_code)

        request_info = json.dumps({"url": url, "params": params, "response": res.text})
        logger.info("drchrono delete request ==> " + request_info)
        return res.json()

    def doctor_list(self, params=None):
        """Retrieve or search doctors within practice group"""
        url = "/api/doctors"
        return self._get_request_(url, params=params)

    def patients_list(self, params=None):
        """Retrieve or search patients"""
        url = "/api/patients"
        return self._get_request_(url, params=params)

    def patients_read(self, patient_id, params=None):
        """Retrieve an existing patient"""
        url = f"/api/patients/{patient_id}"
        return self._get_request_(url, params=params)

    def patient_create(self, params):
        """create patient."""
        url = "/api/patients"
        logger.debug(params)
        email = params.get('email')
        # check if patient already exists based on dob & email
        params1 = {
            'email': email,
            'date_of_birth': params.get('date_of_birth')
        }
        try:
            patient_list_res = self.patients_list(params1)
            patient_list = patient_list_res.get('results', [])
            if len(patient_list) > 0:
                logger.info(f"Patient already exists with email={email} returning same.")
                return patient_list[0]
        except Exception as e:
            logger.exception("drchrono create patient patient list exception: " + str(e))
        return self._post_request_(url, body=params)

    def patient_partial_update(self, data):
        """Partial update"""
        patient_id = data["patient_id"]
        url = f"/api/patients/{patient_id}"
        del data["patient_id"]
        return self._patch_request_(url, body=data)

    def offices_list(self, params=None):
        """Retrieve or search offices"""
        url = "/api/offices"
        return self._get_request_(url, params=params)

    def appointment_create(self, params):
        """Create a new appointment or break on doctor's calendar."""
        url = "/api/appointments"
        return self._post_request_(url, body=params)

    def sublabs_list(self, params=None):
        """Retrieve or search sub vendors"""
        url = "/api/sublabs"
        return self._get_request_(url, params=params)

    def lab_documents_list(self, params=None):
        """Retrieve or search lab order documents"""
        url = "/api/lab_documents"
        return self._get_request_(url, params=params)

    def lab_orders_summary(self, params=None):
        """Retrieve or search documents"""
        url = "/api/lab_orders_summary"
        result = self._get_request_(url, params=params)
        return result

    def lab_orders_list(self, params=None):
        """Retrieve or search lab orders"""
        url = "/api/lab_orders"
        return self._get_request_(url, params=params)

    def lab_orders_create(self, body):
        """Create lab orders.."""
        url = "/api/lab_orders"
        return self._post_request_(url, body=body)

    def lab_orders_delete(self, lab_order_id: int):
        """Delete an existing lab order."""
        url = f"/api/lab_orders/{lab_order_id}"
        return self._delete_request_(url)

    def lab_orders_read(self, lab_order_id: int):
        """Retrieve an existing lab order."""
        url = f"/api/lab_orders/{lab_order_id}"
        return self._get_request_(url)

    def lab_documents_read(self, lab_document_id: int):
        """Retrieve an existing lab order."""
        url = f"/api/lab_documents/{lab_document_id}"
        return self._get_request_(url)

    def lab_orders_update(self, lab_order_id: int):
        """Update an existing lab order."""
        url = f"/api/lab_orders/{lab_order_id}"
        return self._put_request_(url)

    def lab_results_list(self, params=None):
        """Retrieve or search lab results"""
        url = "/api/lab_results"
        return self._get_request_(url, params=params)

    def lab_tests_read(self, lab_test_id):
        """Retrieve an existing lab test"""
        url = f"/api/lab_tests/{lab_test_id}"
        return self._get_request_(url)

    def tasks_list(self, params=None):
        """Retrieve or search tasks"""
        url = "/api/tasks"
        return self._get_request_(url, params=params)

    def tasks_create(self, body):
        """Create a task"""
        url = "/api/tasks"
        return self._post_request_(url, body=body)

    def tasks_read(self, task_id):
        """Retrieve an existing task"""
        url = f"/api/tasks/{task_id}"
        return self._get_request_(url)

    def tasks_partial_update(self, task_id, body):
        """Update an existing task"""
        url = f"/api/tasks/{task_id}"
        return self._patch_request_(url, body=body)

    def tasks_update(self, task_id, body):
        """Update an existing task"""
        url = f"/api/tasks/{task_id}"
        return self._put_request_(url, body=body)

    def task_notes_list(self, params=None):
        """Retrieve or search task notes"""
        url = "/api/task_notes"
        return self._get_request_(url, params=params)

    def task_notes_create(self, body):
        """Create a task note"""
        url = "/api/task_notes"
        return self._post_request_(url, body=body)

    def create_docs_chrono(self, body, files):
        print("check")
        """Create a doct_task note"""
        url = "/api/documents"
        return self._post_request_(url, body=body, files=files)

    def task_notes_read(self, note_id):
        """Retrieve an existing task note"""
        url = f"/api/task_notes/{note_id}"
        return self._get_request_(url)

    def task_notes_partial_update(self, note_id, body):
        """Update an existing task note"""
        url = f"/api/task_notes/{note_id}"
        return self._patch_request_(url, body=body)

    def users_list(self, params=None):
        """List all users"""
        url = "/api/users"
        return self._get_request_(url, params=params)

    def insurances_list(self, params=None):
        """List all insurances"""
        url = "/api/insurances"
        return self._get_request_(url, params=params)

    def download_document(self, url, document_id):
        dr_chrono_documents_directory_path = 'pdfs/drchrono_documents/'
        pathlib.Path(dr_chrono_documents_directory_path).mkdir(parents=True, exist_ok=True)
        pdf_path = dr_chrono_documents_directory_path + str(document_id) + '.pdf'
        try:
            logger.debug(f"downloading pdf {document_id}")
            response = requests.get(url)
            with open(pdf_path, 'wb') as f:
                f.write(response.content)
            f.close()
            return pdf_path
        except Exception as e:
            logger.exception(e)

    def upload_file(self, document_path, document_name):
        s3_bucket = 'drchronodoc'
        try:
            s3_client.upload_file(document_path, s3_bucket, document_name)
            return f"https://s3.{s3_region}.amazonaws.com/{s3_bucket}/{document_name}"
        except Exception as e:
            logger.error(f"upload_file (handle_type_req, handle_type_res) ==> {str(e)}")
            return False


drchrono = Drchrono(CLIENT_ID, CLIENT_SECRET)


def main():
    print(drchrono.token)
    patient = {
        'chart_id': 'BRCH000004',
        'date_of_birth': '1988-10-12',
        'first_name': 'Adam2',
        'doctor': 297491,
        'gender': 'Male',
        'last_name': 'Trial2',
        'email': 'abc@xyz.com'
    }
    # res = drchrono.sublabs_list()
    # print(res)
    # res = drchrono.lab_orders_read(5242338)
    # print(res)
    # res = drchrono.lab_orders_list()
    # print(res)
    lab_order = {
        'doctor': 297491,
        'patient': 97224960,
        'sublab': 20
    }
    # res = drchrono.lab_orders_delete(5242338)
    # print(res)
    # res = drchrono._get_request_("/api/patients")
    # print(res)
    appointment = {
        # 'date': '2021-09-09',
        'doctor': 297491,
        'patient': 95641386,
        'scheduled_time': '2021-09-10T10:00Z',
        'exam_room': 1,
        'office': 316915,
        'duration': 30
    }
    # res = drchrono.appointment_create(appointment)
    # res = drchrono._get_request_("/api/appointments", {'date': '2021-07-10'})
    # print(res)
    # drchrono.refresh_token()
    # print(drchrono.token)
    note = {
        "task": 13191996,
        "text": "Test note",
        "created_by": 446492,
    }
    res = drchrono.patient_partial_update({"email": 'xenum4u@gmail.com', "patient_id": 97102976})
    print(res)


if __name__ == '__main__':
    main()
