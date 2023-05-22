"""
We need CRON to make additional form to weight loss patients.
TO achieve this we have following fields in visits table:-
1- booking month
2- booking date
3- booking year
4- booking time

We want to enable patient to fill new additional form 
1- After 28 days of booking
2- After 88 days of booking
3- After 178 days of booking
4- After 358 days of booking
"""
import os
from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler
scheduler = BackgroundScheduler()
from sre_constants import SUCCESS
import pandas as pd
from api.klaviyo_api import curexa_klaviyo_track_month_cron
from db_client import DBClient
import logging
import datetime
from api.affirm_api import affirm_api
from mdintegrations import MDintegrationsAPI
import json
from fastapi import APIRouter, Request, status, Response, BackgroundTasks
from typing import Optional
from bg_tasks import DrChronoNewLabOrder, drchrono_send_new_lab_order, \
    frontend_test_names_to_code_labcorp, frontend_test_names_to_code_quest, \
    frontend_test_names_to_health_gorilla
from drchrono import drchrono, DrChronoInsuranceQuery, DrChronoLabOrder
from stripe_api import get_subscription, fetch_payment_intent
from config import *
logger = logging.getLogger("fastapi")
router = APIRouter()


log_dir = os.path.join(os.getcwd(), 'log')
logging_file = os.path.join(log_dir,
                            os.path.splitext(os.path.basename(__file__))[0] +
                            datetime.datetime.now().strftime('%y%m%d') +
                            '.log')
logging.basicConfig(
    level=logging.DEBUG,  # DEBUG,
    format='%(asctime)s : %(levelname)s : %(threadName)-9s : %(message)s',
    filename=logging_file,
    filemode='a',
)

def create_accutane_case_mdi(patient):
    try:
        weight = patient["weight"]
        patient_id_md = patient["patient_id_md"]
        data = {
            'patient_id': patient_id_md 
        }

        accutane_dict =  {'Accutane' : {
            'less_166': {
                'medicine': 'ISOtretinoin (oral - capsule)',
                'id': 'c9036927-48f1-4fc0-b635-179ee4accb2b',
                'type': 'Medication'
            },
            'greater_166': {
                'medicine': 'ISOtretinoin (oral - capsule)',
                'id': '249ca084-13e2-4a06-a220-131ee5ef2a3d',
                'type': 'Medication'
            }
        }
        }
        if weight < 166:
            prescriptions = [accutane_dict["less_166"]]
        else:
            prescriptions = [accutane_dict["greater_166"]]
        data['case_prescriptions'] = prescriptions
        questions = [
            {
            'question': "ACCUTANE MONTHLY REFILL",
            'answer': "REFILL ACCUtANE",
            'type': "string",
            'important': False,
            }
        ]
        data['case_questions'] = questions
        res = MDintegrationsAPI.create_case(data)
        logger.debug(res)
        if 'error' in res:
            return {"status": "failed", "error": res['error']}
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


def drchrono_send_lab_order(laborder: DrChronoNewLabOrder, background_tasks: BackgroundTasks):
    """Create lab order for new patient in the background using selenium"""
    try:
        req = laborder.dict()
        logger.debug(req)
        order_type = req.get('order_type')
        if order_type.lower() not in ["labcorp", "quest", "bioreference"]:
            return {"status": "failed", "error": f"invalid order_type: {order_type}"}

        # check patient_id
        patient_id = req.get('patient_id')
        res = drchrono.patients_read(patient_id)
        logger.debug(res)
        if 'id' not in res:
            return {"status": "failed", "error": f"invalid patient: {patient_id}"}

        test_codes = []
        if order_type.lower() == "bioreference":
            target_code = frontend_test_names_to_health_gorilla.keys()
            for favorite in req.get('test_names', []):
                favorite = favorite.strip()
                if favorite not in target_code:
                    logger.error(f"invalid testname: {favorite}")
                    return {"status": "failed", "error": f"invalid test: {favorite}"}
                code = frontend_test_names_to_health_gorilla[favorite]
                test_codes.append(code)
            laborder.test_names = test_codes
        elif order_type.lower() == "labcorp":
            target_code = frontend_test_names_to_code_labcorp.keys()
            for favorite in req.get('test_names', []):
                favorite = favorite.strip()
                if favorite not in target_code:
                    logger.error(f"invalid testname: {favorite}")
                    return {"status": "failed", "error": f"invalid test: {favorite}"}
                code = frontend_test_names_to_code_labcorp[favorite]
                test_codes.append(code)
            laborder.test_names = test_codes
        else:
            target_code = frontend_test_names_to_code_quest.keys()
            for favorite in req.get('test_names', []):
                favorite = favorite.strip()
                if favorite.startswith("STD"):
                    favorite = f"{favorite} {req.get('patient_gender')}"
                if favorite not in target_code:
                    logger.error(f"invalid testname: {favorite}")
                    return {"status": "failed", "error": f"invalid test: {favorite}"}
                code = frontend_test_names_to_code_quest[favorite]
                test_codes.append(code)
            laborder.test_names = test_codes

        background_tasks.add_task(drchrono_send_new_lab_order, laborder)
        return {"status": "success", "message": "Lab Order being created in background."}
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}




def int_to_time(time_int: int) -> tuple:
    """Convert int to hour & minutes
    419 -> hr = 4 & min = 19
    0 -> hr = 0 & min = 0
    """
    time_str = '%4d' % time_int
    time_str = time_str.replace(' ', '0')

    df = pd.to_datetime(time_str, format='%H%M')
    return df.hour, df.minute



def update_patient_info(email, value):
    db = DBClient()
    update_patient = db.make_patient_checkin(email, value)
    if update_patient:
        return {"status":"success"}
    else:
        return {"status":"failed"}

def get_payment_type(payment_id):
    vals = payment_id.split("_")
    if len(vals) == 1:
        return "affirm"
    else:
        if vals[0] == "pi":
            return "prepaid"
        else:
            return "sub"

def order_accutane_testing(patient, is_first_test):
    server_date_time = patient["server_date_time"]
    email = patient["email"]
    sex = patient["sex"]
    address = patient["address"]
    insurance = patient["insurance"]
    patient_name = patient["patient_name"]
    testName = patient["consumer_notes"]
    patient_id = patient["patient_id"]
    payment_id = patient["payment_id"]
    intake_completed = patient["is_user_verified"]
    weight = patient["weight"]
    # check if it's first test and female so we can order female specific initial testing
    if is_first_test and sex == 1:
        test_names = "Acne Treatment Program Female"
    else:
        # else just normal testing for both men and women
        test_names = "Acne Treatment Program Male"
    payload = {}
    if sex == 0:
        payload["patient_gender"] = "Male"
    else:
        payload["patient_gender"] = "Female"
    if insurance == "No":
        payload["bill_to"] = "Doctor Bill"
    else:
        payload["bill_to"] = "Patient Bill"
    lab_location = address.split(" ")[0].lower()
    if lab_location == "home":
        payload["order_type"] = "bioreference"
    else:
        payload["order_type"] = lab_location   
    drchrono_send_lab_order(payload)     

def is_Active_Status(payment_id, server_time):
    db = DBClient()
    payment_type = get_payment_type(payment_id)
    if payment_type == "affirm":
        response = affirm_api.read_transaction(payment_id)
        amount_refunded = response["amount_refunded"]
        if amount_refunded > 50000:
            return False
        return True
    elif payment_type == "prepaid":
        response = fetch_payment_intent(payment_id)
        charge = response["charges"]["data"][0]
        amount_refunded = charge["amount_refunded"]
        if amount_refunded > 50000:
            return False
        return True
    else:
        response = get_subscription(payment_id)
    if id in response:
        if not (response["status"] == "active" or response["status"] == "trialing"):
            booking_ts = datetime.datetime.strptime(server_time, "%d/%m/%Y %H:%M:%S")    
            end_date = booking_ts + datetime.timedelta(days=5)
            db.update_subscription_time_status(end_date, payment_id)
            return True
        else:
            logger.debug("subscription is active state")
            return False    

def cron_body_logic(month, patient):
    sex = patient["sex"]
    payment_id = patient["payment_id"]
    server_date_time = patient["server_date_time"]
    email = patient["email"]
    if is_Active_Status(payment_id, server_date_time):
        if sex == 1: 
            update_patient_info(email, 1)
        curexa_klaviyo_track_month_cron(email,1)
        create_accutane_case_mdi(patient)
    if month == 2 or month == 11:
        order_accutane_testing(patient, False)


            
def main():
    logging.info("Started")
    current_ts = datetime.datetime.now()
    try:
        db = DBClient()
        weightloss_patients = db.get_accutane_patients()
        z=logging.debug(f"No. of Weightloss patients: {len(weightloss_patients)}...")
        for patient in weightloss_patients:
            logging.debug(patient)
            server_date_time = patient["server_date_time"]
            payment_id = patient["payment_id"]
            intake_completed = patient["is_user_verified"]
            patient_name = patient["patient_name"]
            if intake_completed is None or intake_completed == 0:
                booking_ts = datetime.datetime.strptime(server_date_time, "%d/%m/%Y %H:%M:%S")  
                end_date = booking_ts + datetime.timedelta(days=5)
                z=db.update_subscription_time_status(end_date, payment_id)
                pass
            if server_date_time is None:
                logging.debug(f"server_date_time is None. skipping {patient_name}...")
                continue
            booking_ts = datetime.datetime.strptime(patient["server_date_time"], "%d/%m/%Y %H:%M:%S")
            td = current_ts - booking_ts
            # Month 2
            if td.days == 30:
                cron_body_logic(1, patient)
            # Month 3
            elif td.days == 60:
                cron_body_logic(2, patient)
            # Month 4    
            elif td.days == 90:
                cron_body_logic(3, patient)
            # Month 5
            elif td.days == 120:
                cron_body_logic(4, patient)
            # Month 6
            elif td.days == 150:
                cron_body_logic(5, patient)
            # Month 7
            elif td.days == 180:
                cron_body_logic(6, patient)
            # Month 8
            elif td.days == 210:
                cron_body_logic(7, patient)
            # Month 9
            elif td.days == 240:
                cron_body_logic(8, patient)
            # Month 10
            elif td.days == 270:
                cron_body_logic(9, patient)
            # Month 11
            elif td.days == 300:
                cron_body_logic(10, patient)
            # Month 12
            elif td.days == 330:
                cron_body_logic(11, patient)

            else:
                logging.debug(f"condition not met. skipping {patient_name}...")
                continue
    except Exception as e:
        logging.exception(e)

    logging.info("Finished")
    
scheduler.add_job(main, 'interval', minutes= 600)
scheduler.start()
main()