import base64
import copy
import logging
import requests
from pydantic import ValidationError

from config import *
from database.crud import CMMPAResultsCrud
from database.db import get_db
from db_client import DBClient
from drchrono import drchrono
from healthie import healthie
from datetime import date, datetime
from sqlalchemy.orm import Session

from helpers.herlper_methods import upload_file_to_s3
from mdintegrations import mdi_instance_dict
from celery_service.celery_service import CELERY_APP


logger = logging.getLogger("fastapi")

@CELERY_APP.task(bind=True)
def update_patient_data(self, data):
    """
    Updates patient data
    :param data
    :return: dict
    """
    from backend.routers.router_user import _update_stripe_subscription_
    from backend.routers.router_healthie import UpdatePatientHealtieData
    from backend.airtable_api import create_new_record
    email_id = data.get("email")
    case_data = data["case_data"]
    dr_chrono_data = data["dr_chrono_data"]
    lab_document_data = data.get("dr_chrono_lab_document_data")
    dr_chrono_task_data = data["dr_chrono_task_data"]
    dr_chrono_appointment_data = data["dr_chrono_appointment_data"]
    md_data = data["md_data"]
    healthie_data = data["healthie_data"]
    profile_data = data["profile_data"]
    address = profile_data["address"]
    ins_data = data["ins_data"]
    client = DBClient()
    case_id = ""
    count = 0
    patient_md = ""
    healthie_id = ""
    visit_healthie_id = ""
    patient_dr = ""
    mdintegration_patient_created = False
    questions_created = False
    mdintegration_case_created = False
    drchrono_patient_created = False
    drchrono_appointment_created = False
    drchrono_task_created = False
    is_healthie = 0
    is_contrave = None
    is_metformin = None
    drchrono_request_log_status = client.add_drchrono_request_log(copy.deepcopy(data), ENV)
    logger.info("Updating patient email=" + str(email_id) + " address=" + str(address))
    try:
        db: Session = next(get_db())
        airtable_payload = {
            "Patient Name": profile_data.get("patient_name"),
            "Email": email_id,
            "Stripe Payment ID": "",
            "Phone Number": profile_data.get("mobile"),
            "Date Purchased": str(date.today()),
            "Patient Address": profile_data.get("patient_address"),
            "Status": "Open"
        }
        insurance_data_list = profile_data.get("insurance", "").strip().replace(" ", "").split(',')
        if len(insurance_data_list) == 3:
            airtable_payload["Patient Insurance Name"] = insurance_data_list[0]
            airtable_payload["Insurance ID #"] = insurance_data_list[1]
            airtable_payload["Insurance Group #"] = insurance_data_list[2]

        pharmacy_data_list = profile_data.get("pharmacy_ins_patient", "").strip().replace(" ", "").split(',')
        if len(pharmacy_data_list) == 3:
            airtable_payload["Rx Bin"] = pharmacy_data_list[0]
            airtable_payload["Rx PCN"] = pharmacy_data_list[1]
            airtable_payload["Rx Group"] = pharmacy_data_list[2]

        visits_patients_data = client.get_patient_visits(email_id)
        client.update_isVerified(email_id)
        visits_data = visits_patients_data["data"]
        if "test_type" in profile_data:
            mdintegrations_api = mdi_instance_dict.get(profile_data.get("test_type", "normal"))
        for visit in visits_data:
            if visit["is_healthie"] == "1":
                is_healthie = 1
                healthie_id = visit.get('healthie_id')
                is_contrave = True if "contrave" in visit.get('consumer_notes').lower() else False
                is_metformin = True if "metformin" in visit.get('consumer_notes').lower() else False
                break
        if not is_healthie:
            if profile_data.get("address") == "Lab uploaded":
                if not CMMPAResultsCrud.find_by_mrn(db_session=db, mrn=profile_data["mrn"]):
                    ts = datetime.now()
                    CMMPAResultsCrud.create_with_values(
                        db,
                        mrn=profile_data["mrn"],
                        email=email_id,
                        name=profile_data["patient_name"],
                        date_added=ts.strftime("%Y/%m/%d %H:%M:%S"),
                        mounjaro=None,
                        ozempic=None,
                        rybelsus=None,
                        saxenda=None,
                        wegovy=None,
                        preferred_drug_approved=False,
                        rejected_all=False,
                        date_started=None
                    )
            if "test_type" in profile_data:
                md_data["test_type"] = profile_data.get("test_type", "normal")
                case_data["test_type"] = profile_data.get("test_type", "normal")

            if profile_data["test_name"] in [
                "GLP-1 Weight Loss Complete Program",
                "GLP-1 Weight Loss Program"
            ]:
                if profile_data.get("test_name") == "GLP-1 Weight Loss Complete Program":
                    airtable_payload["Subscription Type"] = "GLP Weight Loss Complete"
                if profile_data.get("test_name") == "GLP-1 Weight Loss Program":
                    airtable_payload["Subscription Type"] = "GLP Weight Loss"
                create_new_record(airtable_payload)
            find_patient = client.get_patient_visits(email_id)
            patient_all_data = find_patient["data"]
            for patient in patient_all_data:
                if patient["patient_id_md"] not in [None, "None", ""]:
                    patient_md = patient["patient_id_md"]
                    break
            logger.debug(patient_md)
            if patient_md == "":
                if md_data.get("driver_license"):
                    imgString = base64.b64decode(md_data.get("driver_license"))
                    md_file_res = mdintegrations_api.create_file(imgString)
                    if md_file_res.get('file_id'):
                        md_data["driver_license_id"] = md_file_res.get('file_id')
                try:
                    md_data.pop("driver_license", None)
                    md_patient = mdintegrations_api.create_patient(md_data)
                    mdintegration_patient_created = True
                except Exception as e:
                    mdintegration_patient_created = False
                    md_patient = {}
                    logger.exception("md integration => patient not created: " + str(e))
                if "patient_id" in md_patient:
                    logger.debug(md_patient["patient_id"])
                    subscription_id = None
                    patient_md = md_patient["patient_id"]
                    if "subscription_id" in case_data:
                        subscription_id = case_data["subscription_id"]
                        del case_data["subscription_id"]
                    case_data["patient_id"] = md_patient["patient_id"]
                    if profile_data["test_name"] in [
                        "GLP-1 Weight Loss Complete Program",
                        "GLP-1 Weight Loss Program",
                        "Accutane Acne Program",
                        "Accutane Acne Complete Program",
                        "Contrave Weight Loss Program",
                    ]:
                        for question in case_data["case_questions"]:
                            try:
                                client.create_question(
                                    question["question"],
                                    question["answer"],
                                    profile_data["mrn"],
                                    case_id,
                                    patient_md,
                                    profile_data["pharmacy_id"],
                                )
                                questions_created = True
                            except Exception as e:
                                questions_created = False
                                logger.exception(
                                    "create question => question not created: " + str(e)
                                )
                    else:
                        try:
                            create_md_case = mdintegrations_api.create_case(case_data)
                            mdintegration_case_created = True
                        except Exception as e:
                            create_md_case = {}
                            mdintegration_case_created = False
                            logger.exception(
                                "create case => case not created: " + str(e)
                            )
                        logger.debug(create_md_case)
                        if "case_id" in create_md_case:
                            logger.debug(create_md_case["case_id"])
                            case_id = create_md_case["case_id"]
                            try:
                                _update_stripe_subscription_(
                                    subscription_id,
                                    md_patient["patient_id"],
                                    create_md_case["case_id"],
                                    refills_ordered=1,
                                )
                            except Exception as e:
                                logger.exception(
                                    "update stripe subscription => stripe subscription not updated: "
                                    + str(e)
                                )
            else:
                logger.debug("else value")
                logger.debug(patient_md)
                subscription_id = None
                if "subscription_id" in case_data:
                    subscription_id = case_data["subscription_id"]
                    del case_data["subscription_id"]
                case_data["patient_id"] = patient_md
                if profile_data["test_name"] in [
                    "GLP-1 Weight Loss Complete Program",
                    "GLP-1 Weight Loss Program",
                    "Accutane Acne Program",
                    "Accutane Acne Complete Program",
                    "Contrave Weight Loss Program",
                ]:
                    logger.debug("non one time test")
                    for question in case_data["case_questions"]:
                        try:
                            client.create_question(
                                question["question"],
                                question["answer"],
                                profile_data["mrn"],
                                case_id,
                                patient_md,
                                profile_data["pharmacy_id"],
                            )
                            questions_created = True
                        except Exception as e:
                            questions_created = False
                            logger.exception(
                                "create question => question not created: " + str(e)
                            )
                else:
                    try:
                        create_md_case = mdintegrations_api.create_case(case_data)
                        mdintegration_case_created = True
                    except Exception as e:
                        create_md_case = {}
                        mdintegration_case_created = False
                        logger.exception(
                            "md integration => patient not created: " + str(e)
                        )
                    logger.debug(create_md_case)
                    if "case_id" in create_md_case:
                        logger.debug(create_md_case["case_id"])
                        case_id = create_md_case["case_id"]
                        try:
                            _update_stripe_subscription_(
                                subscription_id,
                                patient_md,
                                create_md_case["case_id"],
                                refills_ordered=1,
                            )
                        except Exception as e:
                            logger.exception(
                                "update stripe subscription => stripe subscription not updated: "
                                + str(e)
                            )
        else:
            for question in case_data["case_questions"]:
                            try:
                                client.create_question(
                                    question["question"],
                                    question["answer"],
                                    profile_data["mrn"],
                                    case_id,
                                    patient_md,
                                    profile_data["pharmacy_id"],
                                )
                                questions_created = True
                            except Exception as e:
                                questions_created = False
                                logger.exception(
                                    "create question => question not created: " + str(e)
                                )                     
        try:
            drchrono_patient = drchrono.patient_create(dr_chrono_data)
            drchrono_patient_created = True
            client.update_drchrono_request_log_processed(
                drchrono_request_log_status["record_id"], processed=1
            )
        except Exception as e:
            drchrono_patient = {}
            drchrono_patient_created = False
            logger.exception(
                "drchrono create patient => patient not created: " + str(e)
            )
        if "id" in drchrono_patient:
            patient_dr = drchrono_patient["id"]
            dr_chrono_appointment_data["patient"] = drchrono_patient["id"]
            try:
                drchrono.appointment_create(dr_chrono_appointment_data)
                drchrono_appointment_created = True
            except Exception as e:
                drchrono_appointment_created = False
                logger.exception(
                    "drchrono create appointment => appointment not created: "
                    + str(e)
                )
            ins_data["patient_id"] = drchrono_patient["id"]
            dr_chrono_task_data["associated_items"] = [
                {"type": "Patient", "value": drchrono_patient["id"]}
            ]
            try:
                drchrono.tasks_create(dr_chrono_task_data)
                drchrono_task_created = True
            except Exception as e:
                drchrono_task_created = False
                logger.exception(
                    "drchrono create task => task not created: " + str(e)
                )
            try:
                drchrono.patient_partial_update(ins_data)
            except Exception as e:
                logger.exception(
                    "drchrono update partial patient => patient not updated: "
                    + str(e)
                )
            if address == "Lab uploaded" and lab_document_data:
                try:
                    file = base64.b64decode(f"data:application/pdf;base64,{lab_document_data.get('file_content')}")
                    files = [
                        ('document', ('lab_document.pdf', file))
                    ]
                    url = "https://drchrono.com/api/documents"
                    payload = {
                        'date': date.today().strftime('%Y-%m-%d'),
                        'description': lab_document_data.get('description'),
                        'doctor': dr_chrono_data.get('doctor'),
                        'patient': patient_dr
                    }
                    headers = {
                        'Authorization': f'Bearer {drchrono.get_access_token()}'
                    }
                    requests.request("POST", url, headers=headers, data=payload, files=files)
                except Exception as e:
                    logger.exception(f"drchrono lab document upload failed => {str(e)}")
        client.update_isVerified(email_id)
        if is_healthie:
            try:
                healthie_data = UpdatePatientHealtieData(**healthie_data).dict()
                healthie_patient = healthie.create_patient_all_in_one(healthie_data)
            except ValidationError as e:
                raise e
            except Exception as e:
                healthie_patient = {}
                logger.exception(
                    "healthie create patient => patient not created: " + str(e)
                )
            if healthie_patient:
                user = healthie_patient["data"]["createClient"]["user"]
            else:
                user = {}
            if user and "id" in user:
                healthie_id = user["id"]
                healthie_data["user_id"] = user["id"]
                healthie_data["rel_user_id"] = user["id"]
                healthie.upload_document_all_in_one(healthie_data)
                healthie_data["id"] = user["id"]
                for policiy in healthie_data.get("policies", []):
                    policiy["user_id"] = user["id"]
                healthie.update_patient_all_in_one(healthie_data)
                if profile_data.get("address") == "Lab uploaded":
                    if not CMMPAResultsCrud.find_by_mrn(db_session=db, mrn=profile_data["mrn"]):
                        ts = datetime.now()
                        CMMPAResultsCrud.create_with_values(
                            db,
                            mrn=profile_data["mrn"],
                            email=email_id,
                            name=profile_data["patient_name"],
                            date_added=ts.strftime("%Y/%m/%d %H:%M:%S"),
                            mounjaro=None,
                            ozempic=None,
                            rybelsus=None,
                            saxenda=None,
                            wegovy=None,
                            preferred_drug_approved=False,
                            rejected_all=False,
                            date_started=None
                        )
                if address == "Lab uploaded" and lab_document_data:
                    try:
                        file = f"data:application/pdf;base64,{lab_document_data.get('file_content')}"
                        lab_document = {
                            'rel_user_id': user["id"],
                            'file_string': file,
                            'include_in_charting': True,
                            'display_name': 'Lab Document',
                            'share_with_rel': True
                        }
                        healthie.upload_document_all_in_one(lab_document)
                        url = upload_file_to_s3({"file_content": lab_document_data.get('file_content')})
                        client.update_drchrono_res_req_column(url=url, mrn=profile_data["mrn"], column="drchrono_res")
                    except Exception as e:
                        logger.exception(f"Healthie lab document upload failed => {str(e)}")
                try:
                    client.update_healthie(email_id)
                except Exception as e:
                    logger.exception(
                        "healthie update => healthie not updated: " + str(e)
                    )
                if profile_data["test_name"] in [
                    "GLP-1 Weight Loss Complete Program",
                    "GLP-1 Weight Loss Program"
                ]:
                    if profile_data.get("test_name") == "GLP-1 Weight Loss Complete Program":
                        airtable_payload["Subscription Type"] = "GLP Weight Loss Complete"
                    if profile_data.get("test_name") == "GLP-1 Weight Loss Program":
                        airtable_payload["Subscription Type"] = "GLP Weight Loss"
                    create_new_record(airtable_payload)
                if address == "Lab uploaded" or is_contrave or is_metformin:
                    try:
                        data_dict = {
                            "user_id": "1627246",
                            "content": "EB_CHECK",
                            "client_id": healthie_id,
                            "due_date": date.today().strftime('%Y-%m-%d'),
                            "reminder": {
                                "is_enabled": True,
                                "interval_type": "daily",
                                "interval_value": "friday",
                                "remove_reminder": True
                            }
                        }
                        healthie.create_task(data_dict)
                        logger.info("Created healthie EB_CHECK task for email=" + str(email_id))
                    except Exception as e:
                        logger.exception(
                            "healthie create task => task not created: " + str(e)
                        )
                try:
                    if healthie_data.get("weight"):
                        weight_entry = {
                            "metric_stat": healthie_data.get("weight"),
                            "category": "Weight",
                            "type": "MetricEntry",
                            "user_id": healthie_id,
                            "created_at": date.today().strftime('%Y-%m-%d')
                        }
                        healthie.storing_Metric_data(weight_entry)
                except Exception as e:
                    logger.exception("storing_Metric_data => data not updated: " + str(e))
                try:
                    if len(healthie_data.get("allergies", [])) > 0:
                        for data in healthie_data.get("allergies"):
                            allergies_entry = {
                                "is_current": True,
                                "user_id": user["id"],
                                "category": "allergy",
                                "name": data.get("name"),
                            }
                            healthie.create_allergy_sensitivity(allergies_entry)
                except Exception as e:
                    logger.exception("storing_Metric_data => data not updated: " + str(e))
                try:
                    if len(healthie_data.get("medications", [])) > 0:
                        for data in healthie_data.get("medications"):
                            medication_entry = {
                                "user_id": user["id"],
                                "active": True,
                                "name": data.get("name"),
                            }
                            healthie.create_medication(medication_entry)
                except Exception as e:
                    logger.exception("medication not added: " + str(e))
                try:
                    if healthie_data.get("charting_notes", {}):
                        charting_notes = healthie_data.get("charting_notes", {})
                        charting_entry = {
                            "user_id": user["id"],
                            "finished": True,
                            "custom_module_form_id": charting_notes.get("custom_module_form_id"),
                            "form_answers": []
                        }
                        answers_list = []
                        if len(charting_notes.get("form_answers", [])) > 0:
                            for answer in charting_notes.get("form_answers", []):
                                answers_list.append(
                                    {
                                        "custom_module_id": answer.get("custom_module_id"),
                                        "answer": answer.get("answer"),
                                        "user_id": user["id"]
                                    }
                                )
                        if len(answers_list) > 0:
                            charting_entry.get("form_answers").extend(answers_list)
                        healthie.creating_filled_out_forms(charting_entry)
                except Exception as e:
                    logger.exception("charting_notes not added: " + str(e))
        result = (
                client.edit_patient_profile_new_fake(
                    profile_data["mrn"],
                    profile_data["patient_name"],
                    profile_data["insurance"],
                    profile_data["pharmacy"],
                    profile_data["patient_address"],
                    profile_data["dob_date"],
                    profile_data["dob_month"],
                    profile_data["dob_year"],
                    profile_data["sex"],
                    profile_data["height"],
                    profile_data["weight"],
                    profile_data["current_medications"],
                    profile_data["allergies"],
                    profile_data["region_no"],
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
                    profile_data["test_type"]
                )
                or {}
        )
        logger.debug("DATA_SUBMITTED")  
        count = count + 1
        result["mdintegration_patient_created"] = mdintegration_patient_created
        result["questions_created"] = questions_created
        result["mdintegration_case_created"] = mdintegration_case_created
        result["drchrono_patient_created"] = drchrono_patient_created
        result["drchrono_appointment_created"] = drchrono_appointment_created
        result["drchrono_task_created"] = drchrono_task_created
        return result
    except ValidationError as e:
        return {"status": "failed", "error": e.errors()}
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}
