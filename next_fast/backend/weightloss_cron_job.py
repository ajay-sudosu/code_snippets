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
import pandas as pd
from api.klaviyo_api import curexa_klaviyo_track_month_cron
from db_client import DBClient
import logging
import datetime

from fastapi import APIRouter, BackgroundTasks
from bg_tasks import (DrChronoNewLabOrder, drchrono_send_new_lab_order, frontend_test_names_to_code_labcorp,
                      frontend_test_names_to_code_quest, frontend_test_names_to_health_gorilla)
from drchrono import drchrono
from stripe_api import get_subscription, fetch_payment_intent

logger = logging.getLogger("fastapi")
router = APIRouter()

log_dir = os.path.join(os.getcwd(), 'log')
logging_file = os.path.join(
    log_dir, os.path.splitext(os.path.basename(__file__))[0] + datetime.datetime.now().strftime('%y%m%d') + '.log'
)
logging.basicConfig(
    level=logging.DEBUG,  # DEBUG,
    format='%(asctime)s : %(levelname)s : %(threadName)-9s : %(message)s',
    filename=logging_file,
    filemode='a',
)


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
        return {"status": "success"}
    else:
        return {"status": "failed"}


def get_payment_type(payment_id):
    vals = payment_id.split("_")
    if len(vals) == 1:
        return "affirm"
    else:
        if vals[0] == "pi":
            return "prepaid"
        else:
            return "sub"


def is_Active_Status(payment_id, server_date_time):
    db = DBClient()
    payment_type = get_payment_type(payment_id)
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
            
            
def main():
    logging.info("Started")
    current_ts = datetime.datetime.now()
    try:
        db = DBClient()
        weightloss_patients = db.get_weightloss_patients()
        logging.debug(f"No. of Weightloss patients: {len(weightloss_patients)}...")

        for patient in weightloss_patients:
            try:
                logging.debug(patient)
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

                # check if user belongs in healthie or MDI

                is_healthie = True if patient["is_healthie"] else False

                if intake_completed is None or intake_completed == 0:
                    try:
                        if '-' in server_date_time:
                            booking_ts = datetime.datetime.strptime(server_date_time, "%d-%m-%Y%H:%M:%S")
                        else:
                            booking_ts = datetime.datetime.strptime(server_date_time, "%d/%m/%Y %H:%M:%S")
                    except ValueError as e:
                        try:
                            server_date_time = server_date_time.replace(':', ' ', 1)
                            if '-' in server_date_time:
                                booking_ts = datetime.datetime.strptime(server_date_time, "%d-%m-%Y%H:%M:%S")
                            else:
                                booking_ts = datetime.datetime.strptime(server_date_time, "%d/%m/%Y %H:%M:%S")
                        except ValueError as e:
                            pass
                    end_date = booking_ts + datetime.timedelta(days=5)
                    db.update_subscription_time_status(end_date.strftime('%d/%m/%Y %H:%M:%S'), payment_id)
                    pass
                if server_date_time is None:
                    logging.debug(f"server_date_time is None. skipping {patient_name}...")
                    continue
                if '-' in server_date_time:
                    booking_ts = datetime.datetime.strptime(server_date_time, "%d-%m-%Y%H:%M:%S")
                else:
                    booking_ts = datetime.datetime.strptime(server_date_time, "%d/%m/%Y %H:%M:%S")

                td = current_ts - booking_ts
                if td.days == 28:
                    if str(testName).lower() == "clomid":
                        payload = {}
                        if sex == 0:
                            payload["patient_gender"] = "Male"
                        else:
                            payload["patient_gender"] = "Female"
                        addSpt = address.split(" ")
                        if insurance == "No":
                            payload["bill_to"] = "Doctor Bill"
                        else:
                            payload["bill_to"] = "Patient Bill"
                        if addSpt[0].lower() == "home":
                            payload["order_type"] = "bioreference"
                            payload["bill_to"] = "Patient Bill"
                        else:
                            payload["order_type"] = addSpt.lower()
                        payload["test_names"] = ["Clomid Month 1"]
                        payload["patient_id"] = patient_id
                        drchrono_send_lab_order(payload)

                    if is_Active_Status(payment_id, server_date_time):
                        update_patient_info(email, 1)
                        curexa_klaviyo_track_month_cron(email, 1)

                # month 2 check-in occurs for healthie patients only

                elif td.days == 58:
                    if is_Active_Status(payment_id, server_date_time) and is_healthie:
                        update_patient_info(email, 2)
                        curexa_klaviyo_track_month_cron(email, 2)

                elif td.days == 88:
                    if is_Active_Status(payment_id, server_date_time):
                        update_patient_info(email, 3)
                        curexa_klaviyo_track_month_cron(email, 3)
                        if testName == "GLP-1 Weight Loss Complete Program":
                            payload = {}
                            if sex == 0:
                                payload["patient_gender"] = "Male"
                            else:
                                payload["patient_gender"] = "Female"
                            addSpt = address.split(" ")
                            if insurance == "No":
                                payload["bill_to"] = "Doctor Bill"
                            else:
                                payload["bill_to"] = "Patient Bill"
                            if addSpt[0].lower() == "home":
                                payload["order_type"] = "bioreference"
                                payload["bill_to"] = "Patient Bill"
                            else:
                                payload["order_type"] = addSpt.lower()
                            payload["test_names"] = ["GLP-1 Weight Loss Complete Program"]
                            payload["patient_id"] = patient_id
                            drchrono_send_lab_order(payload)

                # months 4 and 5 of healthie check-ins

                elif td.days == 108:
                    if is_Active_Status(payment_id, server_date_time) and is_healthie:
                        update_patient_info(email, 4)
                        curexa_klaviyo_track_month_cron(email, 4)

                elif td.days == 138:
                    if is_Active_Status(payment_id, server_date_time) and is_healthie:
                        update_patient_info(email, 5)
                        curexa_klaviyo_track_month_cron(email, 5)

                # month 6 (logic doesn't change for healthie)

                elif td.days == 178:
                    if is_Active_Status(payment_id, server_date_time):
                        update_patient_info(email, 6)
                        curexa_klaviyo_track_month_cron(email, 6)
                        if testName == "GLP-1 Weight Loss Complete Program":
                            payload = {}
                            if sex == 0:
                                payload["patient_gender"] = "Male"
                            else:
                                payload["patient_gender"] = "Female"
                            addSpt = address.split(" ")
                            if insurance == "No":
                                payload["bill_to"] = "Doctor Bill"
                            else:
                                payload["bill_to"] = "Patient Bill"
                            if addSpt[0].lower() == "home":
                                payload["order_type"] = "bioreference"
                                payload["bill_to"] = "Patient Bill"
                            else:
                                payload["order_type"] = addSpt.lower()
                            payload["test_names"] = ["GLP-1 Weight Loss Complete Program"]
                            payload["patient_id"] = patient_id
                            drchrono_send_lab_order(payload)

                # months 7 and 8 of healthie check-ins

                elif td.days == 208:
                    if is_Active_Status(payment_id, server_date_time) and is_healthie:
                        update_patient_info(email, 7)
                        curexa_klaviyo_track_month_cron(email, 7)

                elif td.days == 238:
                    if is_Active_Status(payment_id, server_date_time) and is_healthie:
                        update_patient_info(email, 8)
                        curexa_klaviyo_track_month_cron(email, 8)

                # month 9 check-in logic already exists

                elif td.days == 268:
                    if is_Active_Status(payment_id, server_date_time):
                        update_patient_info(email, 9)
                        curexa_klaviyo_track_month_cron(email, 9)
                        if testName == "GLP-1 Weight Loss Complete Program":
                            payload = {}
                            if sex == 0:
                                payload["patient_gender"] = "Male"
                            else:
                                payload["patient_gender"] = "Female"
                            addSpt = address.split(" ")
                            if insurance == "No":
                                payload["bill_to"] = "Doctor Bill"
                            else:
                                payload["bill_to"] = "Patient Bill"
                            if addSpt[0].lower() == "home":
                                payload["order_type"] = "bioreference"
                                payload["bill_to"] = "Patient Bill"
                            else:
                                payload["order_type"] = addSpt.lower()
                            payload["test_names"] = ["GLP-1 Weight Loss Complete Program"]
                            payload["patient_id"] = patient_id
                            drchrono_send_lab_order(payload)

                # months 10 and 11 of healthie check-ins

                elif td.days == 298:
                    if is_Active_Status(payment_id, server_date_time) and is_healthie:
                        update_patient_info(email, 10)
                        curexa_klaviyo_track_month_cron(email, 10)

                elif td.days == 328:
                    if is_Active_Status(payment_id, server_date_time) and is_healthie:
                        update_patient_info(email, 11)
                        curexa_klaviyo_track_month_cron(email, 11)

                # month 12 already exists

                elif td.days == 358:
                    if is_Active_Status(payment_id, server_date_time):
                        update_patient_info(email, 12)
                        curexa_klaviyo_track_month_cron(email, 12)
                else:
                    logging.debug(f"condition not met. skipping {patient_name}...")
                    continue
            except Exception as e:
                logging.exception(e)
    except Exception as e:
        logging.exception(e)

    logging.info("Finished")


if __name__ == '__main__':
    main()
