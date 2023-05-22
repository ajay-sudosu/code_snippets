import json
from http.client import CannotSendHeader
import logging
from fastapi import APIRouter, Request, status, Response, BackgroundTasks, UploadFile, File, HTTPException, Depends
from typing import Optional, List
from db_client import DBClient
from mdintegrations import mdintegrations_api, mdi_instance_dict, MDintegrationsPatient, MDICreateCase, \
    WEBHOOK_SECRET, WEBHOOK_TOKEN, MDintegrationsPatientPharmacy, MDICreateHerpesCase, MDICasePrescription, \
    MDIPatientId, MDICreatePrescriptionsCase, MDICasePrescriptionUpdate, MDISearchPharmacy, \
    WEBHOOK_TOKEN_ACCUTANE, WEBHOOK_TOKEN_WEIGHTLOSS, WEBHOOK_TOKEN_TESTOSTERONE, WEBHOOK_TOKEN_CANADA, \
    WEBHOOK_TOKEN_AGING, WEBHOOK_TOKEN_DIAGNOSTICS, MDICreateCaseMedicine, detect_mdi_case_account_type
from utils import download_file, delete_file
from bg_task.mdi_tasks import mdi_attach_pharmacy_to_patient, mdi_webhook_handle, mdi_webhook_handle_accutane, \
    mdi_webhook_handle_weightloss, mdi_webhook_handle_testosterone, mdi_webhook_handle_aging, \
    mdi_webhook_handle_canada, mdi_webhook_handle_diagnostics
from stripe_api import update_subscription
from config import *
import base64
from io import BytesIO
from database.db import get_db
from database.crud import MDIMappingCrud, VisitsCrud
from sqlalchemy.orm import Session
from pathlib import Path

logger = logging.getLogger("fastapi")
router = APIRouter()

medication_dict = {
    'Accutane': {
        'less_166': {
            'medicine': 'ISOtretinoin (oral - capsule)',
            'id': 'c9036927-48f1-4fc0-b635-179ee4accb2b',
            'type': 'Medication'
        },
        'greater_166': {
            'medicine': 'ISOtretinoin (oral - capsule)',
            'id': '249ca084-13e2-4a06-a220-131ee5ef2a3d',
            'type': 'Medication'
        },
        'Herpes 1': {
            'outbreaks': {
                'medicine': 'Valacyclovir 1000 mg (HSV-1 Acute Flare)',
                'id': '59ccae47-3203-42cd-832b-6749f02831d1',
                'type': 'Compound'
            },
            'suppression': {
                'medicine': 'Valacyclovir 500 mg (HSV-2 Acute Flare)',
                'id': 'a96329f9-102d-4409-98c9-42883edbcc40',
                'type': 'Medication'
            }
        },
        'Herpes 2': {
            'outbreaks': {
                'medicine': 'Valacyclovir 500 mg (HSV-2 Acute Flare)',
                'id': 'd6906815-0e93-4bd8-b64b-b83541b4407f',
                'type': 'Compound'
            },
            'suppression': {
                'medicine': 'Valacyclovir 500 mg (HSV-2 Acute Flare)',
                'id': 'a96329f9-102d-4409-98c9-42883edbcc40',
                'type': 'Medication'
            }
        },
        'Loratadine': '3f91bd5b-a70e-41ee-9261-daadf8f69c04',
        'Fluticasone Nasal': '6b2e3aa9-553a-45e1-b8b4-6927f596c2ba',
        'Emtricitabine/Tenofovir Alafenamide': '5df4245c-023d-45e4-a3cd-92a916b1959b',
        'Valacyclovir': 'a96329f9-102d-4409-98c9-42883edbcc40',
        'Acyclovir': 'd680224e-a841-4f47-87e6-bc91357bd3fd',
        'Levothyroxine': 'be9e4d40-ba51-4a93-85e4-c04b46b63b4f',
        'Simvastatin': '912b427d-55bc-42f7-9784-308498660117',
        'Rosuvastatin': 'a9bcd2c4-5fa8-4ffe-a418-f210ce3dcc3d',
        'Cyanocobalamin': 'd6ac6d9e-a2cf-4488-b3cd-5903368fa41a',
        'Ergocalciferol': '692d4185-264e-468e-9d30-6e663ab4a953',
    }

}


def _get_md_clinician_id_(patient_id_md):
    try:
        response = mdintegrations_api.get_patient_cases(patient_id_md)
        if 'data' not in response:
            logger.debug(response)
            return None

        for case in response['data']:
            clinician_id = case['case_assignment']['clinician']['clinician_id']
            return clinician_id
    except Exception as e:
        logger.exception(e)
    return None


def get_messages_by_patient_id(patient_id: str, test_type: str = 'normal'):
    messages, case_id = [], ""
    try:
        mdi_instance = mdi_instance_dict.get(test_type, 'normal')
        response = mdi_instance.get_patient_cases(patient_id)
        if "data" in response:
            for case in response["data"]:
                case_id = case["case_id"]
                response = mdi_instance.get_messages(case_id, "patient")
                messages.extend(response)
    except Exception as e:
        logger.exception(e)
    return messages, case_id


def _update_stripe_subscription_(subscription_id, patient_id_md, case_id, refills_ordered=1):
    """Update stripe subscription for refill count & new case id"""
    try:
        if not subscription_id:
            logger.warning(f"Not Updating stripe subscription: {subscription_id}")
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


@router.post('/mdintegrations-webhooks', tags=["mdintegrations"])
async def mdintegrations_webhooks_endpoint(request: Request, response: Response, background_tasks: BackgroundTasks):
    try:
        logger.info("API: mdintegrations-webhooks")
        # check header
        signature = request.headers.get('Signature')
        if signature is None:
            response.status_code = status.HTTP_403_FORBIDDEN
            return {"status": "failed", "error": "HTTP header 'Signature' is missing"}

        # check header
        content_type = request.headers.get('Content-Type')
        if content_type is None:
            response.status_code = status.HTTP_403_FORBIDDEN
            return {"status": "failed", "error": "HTTP header 'content_type' is missing"}
        elif content_type != 'application/json':
            response.status_code = status.HTTP_403_FORBIDDEN
            return {"status": "failed", "error": "unsupported content_type"}

        # # find algo & hash
        # algo, msg_hash = signature.split('=')
        # # logger.debug(algo, msg_hash)

        # # get raw request body
        # raw_data = await request.body()
        # # calculate hash
        # digest_maker = hmac.new(bytes(WEBHOOK_SECRET, 'utf-8'), raw_data, hashlib.sha256)

        # # check hash for authentication
        # cal_hash = digest_maker.hexdigest()
        # logger.debug(cal_hash)
        # if cal_hash != msg_hash:
        #     response.status_code = status.HTTP_403_FORBIDDEN
        #     return {"message": "Secret Key Mismatch"}

        data = await request.json()
        logger.debug(data)

        # check token
        token = request.headers.get('Authorization')
        if token == WEBHOOK_TOKEN:
            background_tasks.add_task(mdi_webhook_handle, data)
        elif token == WEBHOOK_TOKEN_ACCUTANE:
            background_tasks.add_task(mdi_webhook_handle_accutane, data)
        elif token == WEBHOOK_TOKEN_WEIGHTLOSS:
            background_tasks.add_task(mdi_webhook_handle_weightloss, data)
        elif token == WEBHOOK_TOKEN_TESTOSTERONE:
            background_tasks.add_task(mdi_webhook_handle_testosterone, data)
        elif token == WEBHOOK_TOKEN_AGING:
            background_tasks.add_task(mdi_webhook_handle_aging, data)
        elif token == WEBHOOK_TOKEN_CANADA:
            background_tasks.add_task(mdi_webhook_handle_canada, data)
        elif token == WEBHOOK_TOKEN_DIAGNOSTICS:
            background_tasks.add_task(mdi_webhook_handle_diagnostics, data)
        else:
            response.status_code = status.HTTP_403_FORBIDDEN
            return {"message": "Invalid Token"}

        return {"status": "success", "data": "Being handled in bg."}

    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@router.post('/mdi-create-prescriptions-case', tags=["mdintegrations"])
async def mdintegrations_create_prescriptions_case_endpoint(new_request: MDICreatePrescriptionsCase):
    """Create cases on MDI with prescription"""

    def herpes_abnormal_tests(tests_results):
        if tests_results is None:
            return None
        tests_list = tests_results.split(';')
        if 'Herpes 1' in tests_list and 'Herpes 2' in tests_list:
            return 'Herpes 2'
        if 'Herpes 2' in tests_list:
            return 'Herpes 2'
        if 'Herpes 1' in tests_list:
            return 'Herpes 1'
        return None

    try:
        logger.info("API: mdi-create-prescriptions-case")
        req = new_request.dict()
        logger.debug(req)

        db = DBClient()
        # fetch row from visits table
        visit = db.get_visits_by_mrn(mrn=new_request.mrn)
        if visit == {}:
            return {"status": "failed", "error": f"Not found mrn: {new_request.mrn}"}

        patient_id_md = visit.get("patient_id_md")
        if patient_id_md is None:
            return {"status": "failed", "error": "patient_id_md is None"}
        data = {
            'patient_id': patient_id_md
        }
        clinician_id = _get_md_clinician_id_(patient_id_md)
        if clinician_id is not None:
            data['clinician_id'] = clinician_id

        prescriptions_list = []
        abnormal_result_answer = "NO"
        medication = "No Medicine Requested"

        if new_request.medicineList is not None:
            for medicine in new_request.medicineList:
                partner_medication_id = medication_dict.get(medicine.strip())
                if partner_medication_id is None:
                    logger.warning(f"Medicine not found: {medicine}")
                else:
                    prescription = {
                        'partner_medication_id': partner_medication_id
                    }
                    prescriptions_list.append(prescription)
                    logger.info(f"Medicine added: {medicine}, id: {partner_medication_id}")

        if len(prescriptions_list) > 0:
            data['case_prescriptions'] = prescriptions_list
            abnormal_result_answer = "YES"
            medication = "Medicine Requested"

        # save stripe subscription id to case
        data['metadata'] = new_request.subscriptionId

        # download result file
        file_path = download_file(new_request.mrn, url=visit.get('drchrono_res'))
        if file_path is None:
            return {"status": "failed", "error": "Results NA"}
        # upload to MDI
        file_id = mdintegrations_api.mdi_create_file(file_path)
        data["case_files"] = [file_id]
        delete_file(file_path)

        patient_symptoms = visit.get("patient_symptoms")
        if patient_symptoms is None:
            patient_symptoms = 'NA'
        elif len(patient_symptoms) == 0:
            patient_symptoms = 'NA'

        questions = [
            {
                'question': "RESULT REVIEW",
                'answer': "REVIEW RESULTS",
                'type': "string",
                'important': True,
            },
            {
                'question': "ABNORMAL RESULT",
                'answer': abnormal_result_answer,
                'type': "string",
                'important': True,
            },
            {
                'question': "SYMPTOMS",
                'answer': patient_symptoms,
                'type': "string",
                'important': True,
            },
            {
                'question': "MEDICATION",
                'answer': medication.upper(),
                'type': "string",
                'important': True,
            }
        ]

        data['case_questions'] = questions

        # create case on mdi
        logger.info(data)
        res = mdintegrations_api.create_case(data)
        logger.debug(res)
        if 'error' in res:
            return {"status": "failed", "error": res['error']}
        md_case_id = res.get('case_id')
        # save case_id to db
        db.update_visits_md_case_id(mrn=new_request.mrn, md_case_id=md_case_id)
        return {"status": "success", "data": {"md_case_id": md_case_id}}
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@router.post('/mdi-create-herpes-case', tags=["mdintegrations"])
async def mdintegrations_create_herpes_case_endpoint(herpes_case: MDICreateHerpesCase):
    """Create Herpes case on MDI with prescription"""

    def herpes_abnormal_tests(tests_results):
        if tests_results is None:
            return None
        tests_list = tests_results.split(';')
        if 'Herpes 1' in tests_list and 'Herpes 2' in tests_list:
            return 'Herpes 2'
        if 'Herpes 2' in tests_list:
            return 'Herpes 2'
        if 'Herpes 1' in tests_list:
            return 'Herpes 1'
        return None

    try:
        logger.info("API: mdi-create-herpes-case")
        req = herpes_case.dict()
        logger.debug(req)
        db = DBClient()
        # fetch row from visits table
        visit = db.get_visits_by_mrn(mrn=herpes_case.mrn)
        if visit == {}:
            return {"status": "failed", "error": f"Not found mrn: {herpes_case.mrn}"}

        '''# check case is not already created
        md_case_id = visit.get('md_case_id')
        if md_case_id is not None and md_case_id != 'None':
            logger.info(f"case {md_case_id} already created.")
            return {"status": "success", "data": {"md_case_id": md_case_id}}
        '''

        # check they are herpes +ve
        herpes = herpes_abnormal_tests(visit.get('drchrono_abnormal_tests'))
        if herpes is None:
            return {"status": "failed", "error": f"Not Herpes +ve"}

        # download result file
        file_path = download_file(herpes_case.mrn, url=visit.get('drchrono_res'))
        if file_path is None:
            return {"status": "failed", "error": "Results NA"}
        # upload to MDI
        file_id = mdintegrations_api.mdi_create_file(file_path)
        delete_file(file_path)
        patient_id_md = visit.get("patient_id_md")
        if patient_id_md is None:
            return {"status": "failed", "error": "patient_id_md is None"}
        clinician_id = _get_md_clinician_id_(patient_id_md)
        data = {
            'patient_id': patient_id_md,
            'case_files': [file_id]
        }
        if clinician_id is not None:
            data['clinician_id'] = clinician_id

        if herpes_case.subscriptionType is None or herpes_case.subscriptionType == '':
            medication = "No Medicine Requested"
            abnormal_result_answer = "NO"
        elif herpes_case.subscriptionType.lower() == "suppression":
            medication = "suppression"
            prescription = {
                'partner_medication_id': '6329f9-102d-4409-98c9-42883edbcc40',
            }

            data['case_prescriptions'] = [prescription]
            abnormal_result_answer = "YES"

        elif herpes_case.subscriptionType.lower() == "outbreaks":
            medication = "outbreaks"
            partner_compound_id = medication_dict[herpes]["outbreaks"]['id']
            prescription = {
                'partner_compound_id': partner_compound_id,
            }
            data['case_prescriptions'] = [prescription]
            abnormal_result_answer = "YES"
        else:
            medication = "No Medicine Requested"
            abnormal_result_answer = "NO"

        patient_symptoms = visit.get("patient_symptoms")
        if patient_symptoms is None:
            patient_symptoms = 'NA'
        elif len(patient_symptoms) == 0:
            patient_symptoms = 'NA'

        questions = [
            {
                'question': "RESULT REVIEW",
                'answer': "REVIEW RESULTS",
                'type': "string",
                'important': True,
            },
            {
                'question': "ABNORMAL RESULT",
                'answer': abnormal_result_answer,
                'type': "string",
                'important': True,
            },
            {
                'question': "SYMPTOMS",
                'answer': patient_symptoms,
                'type': "string",
                'important': True,
            },
            {
                'question': "MEDICATION",
                'answer': medication.upper(),
                'type': "string",
                'important': True,
            }
        ]

        data['case_questions'] = questions

        # save stripe subscription id to case
        data['metadata'] = herpes_case.subscriptionId

        # create case on mdi
        logger.info(data)
        res = mdintegrations_api.create_case(data)
        logger.debug(res)
        if 'error' in res:
            return {"status": "failed", "error": res['error']}
        md_case_id = res.get('case_id')
        # save case_id to db
        db.update_visits_md_case_id(mrn=herpes_case.mrn, md_case_id=md_case_id)
        return {"status": "success", "data": {"md_case_id": md_case_id}}
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@router.post('/mdi-get-case-messages', tags=["mdintegrations"])
async def mdintegrations_get_case_messages_endpoint(request: Request, db_session: Session = Depends(get_db)):
    """Get all case's messages for the given patient"""
    try:
        logger.info("API: mdi-get-case-messages")
        data = await request.json()
        logger.debug(data)
        if not data.get('patient_id') and not data.get('email'):
            return {"status": "failed", "message": "Some required fields are missing."}
        test_type = data.get('test_type', 'normal')
        if data.get('patient_id'):
            patient_id = data["patient_id"]
            test_type, mdi_api = detect_mdi_account_type(db_session, patient_id)
            messages, case_id = get_messages_by_patient_id(patient_id, test_type)
            return {"status": "success", "data": messages, "case_id": case_id, "test_type": test_type}
        else:
            params = {"search": data.get('email')}
            for test_type, mdi_api in mdi_instance_dict.items():
                response = mdi_api.search_patient(params)
                for res in response:
                    patient_id = res.get("patient_id")
                    if patient_id:
                        logger.debug(f"found {data.get('email')} in {test_type} patient_id: {patient_id}")
                        messages, case_id = get_messages_by_patient_id(patient_id, test_type)
                        return {"status": "success", "data": messages, "case_id": case_id, "test_type": test_type}
        return {"status": "failed", "error": "not found", "data": [], "case_id": '', "test_type": test_type}
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@router.post('/mdintegrations-case-get-messages', tags=["mdintegrations"])
async def mdintegrations_case_get_messages_endpoint(request: Request, db_session: Session = Depends(get_db)):
    """Get all messages for a case"""
    try:
        logger.info("API: mdintegrations-case-get-messages")
        data = await request.json()
        logger.debug(data)
        test_type = data.get('test_type', 'normal')
        mdi_account_type, mdi_instance = detect_mdi_case_account_type(db_session, data['case_id'])
        if mdi_instance:
            res = mdi_instance.get_messages(
                case_id=data['case_id'], channel=data['channel'])
            logger.debug(res)
            return res
        return {"status": "failed", "error": "invalid case_id"}

    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@router.post('/mdintegrations-case-create-message', tags=["mdintegrations"])
async def mdintegrations_case_create_message_endpoint(request: Request, db_session: Session = Depends(get_db)):
    try:
        logger.info("API: mdintegrations-case-create-message")
        data = await request.json()
        logger.debug(data)
        case_id = data.get('case_id')
        del data['case_id']
        mdi_account_type, mdi_api = detect_mdi_case_account_type(db_session, case_id)
        if mdi_api:
            res = mdi_api.create_messages(case_id=case_id, data=data)
            logger.debug(res)
            if 'case_message_id' in res:
                return res
        return {"status": "failed", "error": f"{case_id} not found"}

    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


def detect_mdi_account_type(db_session: Session, patient_id: str):
    """detect_mdi_account_type for a patient_id"""
    if not patient_id or patient_id == 'None':
        return None, None
    try:
        db_mapping = MDIMappingCrud.fetch_by_patient_id(db_session, patient_id)
        if db_mapping:
            return db_mapping.mdi_account_type, mdi_instance_dict.get(db_mapping.mdi_account_type)
    except Exception as e:
        logger.exception(e)

    for mdi_account_type, mdi_api in mdi_instance_dict.items():
        try:
            res = mdi_api.get_patient(patient_id)
            if 'patient_id' in res:
                logger.info(f"Detected MDI account type: {mdi_account_type} for patient_id_md: {patient_id}")
                try:
                    MDIMappingCrud.create_with_values(db_session,
                                                      patient_id=patient_id,
                                                      email=res.get('email'),
                                                      mdi_account_type=mdi_account_type)
                except Exception as e:
                    logger.exception(e)
                return mdi_account_type, mdi_api
        except Exception as e:
            logger.exception(e)
    return None, None


def mdintegrations_create_case(db_session: Session, data: dict, mdi_api=None):
    mdi_account_type = data.pop('test_type')
    subscription_id = data.pop('subscription_id')
    if mdi_api is None:
        mdi_account_type, mdi_api = detect_mdi_account_type(db_session, data.get('patient_id'))
    if mdi_api:
        data = {k: v for k, v in data.items() if v}
        case_res = mdi_api.create_case(data)
        logger.debug(case_res)
        if 'case_id' in case_res and subscription_id:
            _update_stripe_subscription_(subscription_id, data['patient_id'], case_res['case_id'], refills_ordered=1)
        return case_res
    return {'status': 'failed', 'error': 'invalid patient_id'}


@router.post('/mdintegrations-create-case', tags=["mdintegrations"])
async def mdintegrations_create_case_endpoint(case: MDICreateCase, db_session: Session = Depends(get_db)):
    try:
        logger.info("API: mdintegrations-create-case")
        data = case.dict()
        logger.debug(data)

        if not case.patient_id:
            return {'status': 'failed', 'error': 'invalid patient_id'}
        response = mdintegrations_create_case(db_session, data)
        return response
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


def read_jsonfile(filepath: Path):
    try:
        filepath.touch(exist_ok=True)
        with open(filepath, 'r') as openfile:
            mdi_medication_dict_tmp = json.load(openfile)
            return mdi_medication_dict_tmp
    except Exception as e:
        logger.exception(e)
        return {}


def get_prescriptions_from_dict(medicines, curr_dose, weight_loss_month):
    case_prescriptions = []
    for med in medicines:
        if med.get("month") == weight_loss_month and med.get("curr_dose") == curr_dose:
            for __id in med.get("medication_id", []):
                case_prescription = {'partner_medication_id': __id}
                case_prescriptions.append(case_prescription)
            for __id in med.get("compound_id", []):
                case_prescription = {'partner_compound_id': __id}
                case_prescriptions.append(case_prescription)
            break
    return case_prescriptions


@router.post('/mdintegrations-create-case-medication', tags=["mdintegrations"])
async def mdintegrations_create_case_medication_endpoint(case: MDICreateCaseMedicine,
                                                         db_session: Session = Depends(get_db)):
    try:
        mdi_medication_dict = {}
        logger.info("API: mdintegrations-create-case-medication")
        data = case.dict()
        logger.debug(data)

        if not case.patient_id:
            return {'status': 'failed', 'error': 'invalid patient_id'}
        if not case.medicine:
            return {'status': 'failed', 'error': 'invalid medicine'}
        mdi_account_type, mdi_api = detect_mdi_account_type(db_session, case.patient_id)
        if mdi_account_type == 'normal':
            filename = Path('mdi_data/customer_nextmed.json')
            mdi_medication_dict = read_jsonfile(filename)
        elif mdi_account_type == 'weightloss':
            filename = Path('mdi_data/customer_weightloss.json')
            mdi_medication_dict = read_jsonfile(filename)
        else:
            return {'status': 'failed', 'error': 'invalid mdi_account_type'}

        # get medicine from dict
        req_medicine = data.pop('medicine')
        medicines = mdi_medication_dict.get(req_medicine.title())
        if not medicines:
            return {'status': 'failed', 'error': f'invalid medicine: {case.medicine}'}

        visits = VisitsCrud.get_visits_row_by_patient_id_md(case.patient_id)
        if not visits:
            return {'status': 'failed', 'error': f'visit not found'}
        visit = visits[0]
        if not visit.get('weight_medicine_type'):
            return {'status': 'failed', 'error': f'weight_medicine_type empty'}
        try:
            curr_dose = int(visit.get('curr_dose', 0))
        except:
            curr_dose = 0

        try:
            weight_loss_month = int(visit.get('weight_loss_month', 0))
        except:
            weight_loss_month = 0

        data['case_prescriptions'] = get_prescriptions_from_dict(medicines, curr_dose, weight_loss_month)
        response = mdintegrations_create_case(db_session, data)
        return response
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@router.post('/mdintegrations-create-case-accutane', tags=["mdintegrations"])
async def mdintegrations_create_case_accutane_endpoint(case: MDICreateCase, db_session: Session = Depends(get_db)):
    try:
        logger.info("API: mdintegrations-create-case-accutane")
        data = case.dict()
        logger.debug(data)

        if not case.patient_id:
            return {'status': 'failed', 'error': 'invalid patient_id'}
        response = mdintegrations_create_case(db_session, data)
        return response
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@router.post('/mdintegrations-create-case-weightloss', tags=["mdintegrations"])
async def mdintegrations_create_case_weightloss_endpoint(case: MDICreateCase, db_session: Session = Depends(get_db)):
    try:
        logger.info("API: mdintegrations-create-case-weightloss")
        data = case.dict()
        logger.debug(data)

        if not case.patient_id:
            return {'status': 'failed', 'error': 'invalid patient_id'}
        response = mdintegrations_create_case(db_session, data)
        return response
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


# @router.post('/mdintegrations-create-retool-case', tags=["mdintegrations"])
# async def mdintegrations_create_case_retool_endpoint(request: Request):
#     try:
#         data = await request.json()
#         db = DBClient()
#         logger.debug(data)
#         subscription_id = None
#         if 'subscription_id' in data:
#             subscription_id = data['subscription_id']
#             del data['subscription_id']
#         res = mdintegrations_api.create_case(data)
#         logger.debug(res)
#         if 'case_id' in res:
#             _update_stripe_subscription_(subscription_id, data['patient_id'], res['case_id'], refills_ordered=1)
#             db.update_visits_by_case_id(res['patient']['email'],res['case_id'])
#             return res
#         raise Exception(res)
#     except Exception as e:
#         logger.exception(e)
#         raise HTTPException(status_code=403, detail={"status": "failed", "error": str(e)})


@router.get('/mdi-get-case', tags=["mdintegrations"])
async def mdintegrations_get_case_endpoint(case_id: str, db_session: Session = Depends(get_db)):
    """Get case details for the given case id"""
    try:
        logger.info("API: mdi-get-case")
        mdi_account_type, mdi_instance = detect_mdi_case_account_type(db_session, case_id)
        if mdi_instance:
            response = mdi_instance.get_case(case_id)
            return response
        return {"status": "failed", "error": "invalid case_id"}

    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@router.post('/mdintegrations-get-pharmacies', tags=["mdintegrations"])
async def mdintegrations_get_pharmacies_endpoints(data: MDISearchPharmacy):
    # At least one query parameter is required:
    try:
        logger.info("API: mdintegrations-get-pharmacies")
        logger.debug(data.dict())
        res = mdintegrations_api.get_pharmacies(params=data)
        logger.debug(res)
        if res is not None:
            return res
        raise Exception(res)

    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@router.post('/mdintegrations-get-prescriptions', tags=["mdintegrations"])
async def mdintegrations_get_prescriptions_endpoints(
        prescription: MDICasePrescription,
        db_session: Session = Depends(get_db)
):
    """Fetch case prescriptions for given case id"""
    # At least one query parameter is required:
    try:
        logger.info("API: mdintegrations-get-prescriptions")
        data = prescription.dict()
        logger.debug(data)
        mdi_account_type, mdi_api = detect_mdi_case_account_type(db_session, prescription.case_id)
        if mdi_api:
            res = mdi_api.get_prescription(case_id=prescription.case_id)
            logger.debug(res)
            return res
        return {"status": "failed", "error": f"case_id {prescription.case_id} not found"}

    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@router.post('/mdintegrations-update-prescriptions', tags=["mdintegrations"])
async def mdintegrations_update_prescriptions_endpoints(
        data: MDICasePrescriptionUpdate,
        db_session: Session = Depends(get_db)
):
    """Update case prescriptions for given case id"""
    try:
        logger.info("API: mdintegrations-update-prescriptions")
        logger.debug(data.dict())
        mdi_account_type, mdi_api = detect_mdi_case_account_type(db_session, data.case_id)
        if mdi_api:
            res = mdi_api.update_case_prescriptions(
                case_id=data.case_id, data=data.prescriptions)
            logger.debug(res)
            return res
        return {"status": "failed", "error": f"case_id {data.case_id} not found"}

    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@router.get('/mdi-get-case-questions', tags=["mdintegrations"])
async def mdintegrations_get_case_questions_endpoint(case_id: str, db_session: Session = Depends(get_db)):
    """Get case questions for the given case id"""
    try:
        logger.info("API: mdi-get-case-questions")
        mdi_account_type, mdi_api = detect_mdi_case_account_type(db_session, case_id)
        if mdi_api:
            response = mdi_api.get_case_questions(case_id)
            return response
        return {"status": "failed", "error": f"case_id {case_id} not found"}
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@router.post('/mdintegrations-patient-cases', tags=["mdintegrations"])
async def mdintegrations_get_patient_cases_endpoint(patient: MDIPatientId, response: Response,
                                                    db_session: Session = Depends(get_db)):
    """ Get all cases of a patient id"""
    try:
        logger.info("API: mdintegrations-patient-cases")
        data = patient.dict()
        logger.debug(data)
        # NXTMD-509
        if patient.patient_id == 'None' or not patient.patient_id:
            response.status_code = status.HTTP_406_NOT_ACCEPTABLE
            return {"status": "failed", "error": "patient_id invalid"}

        mdi_account_type, mdi_api = detect_mdi_account_type(db_session, patient.patient_id)
        if mdi_api:
            res = mdi_api.get_patient_cases(patient_id=patient.patient_id)
            logger.debug(res)
            return res
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"status": "failed", "error": "patient_id invalid"}
    except Exception as e:
        logger.exception(e)
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"status": "failed", "error": str(e)}


@router.post('/mdintegrations-create-patient', tags=["mdintegrations"])
async def mdintegrations_create_patient_endpoint(request: Request):
    try:
        logger.info("API: mdintegrations-create-patient")
        data = await request.json()
        logger.debug(data)
        test_type = 'normal'
        if 'test_type' in data:
            test_type = data['test_type'].lower()
            del data['test_type']
        mdi_instance = mdi_instance_dict.get(test_type, 'normal')
        res = mdi_instance.create_patient(data)
        logger.debug(res)
        if 'patient_id' in res:
            return res
        raise Exception(res)

    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@router.post('/mdintegrations-get-patient', tags=["mdintegrations"])
async def mdintegrations_get_patient_endpoint(request: Request, response: Response,
                                              db_session: Session = Depends(get_db)):
    try:
        logger.info("API: mdintegrations-get-patient")
        data = await request.json()
        logger.debug(data)
        patient_id = data.get("patient_id")
        mdi_account_type, mdi_api = detect_mdi_account_type(db_session, patient_id)
        if mdi_api:
            res = mdi_api.get_patient(patient_id)
            return res
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"status": "failed", "error": "patient_id invalid"}

    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@router.get('/mdintegrations-get-patient-pharmacies', tags=["mdintegrations"])
async def mdintegrations_get_patient_pharmacies_endpoint(patient_id: str, test_type: str = 'normal',
                                                         db_session: Session = Depends(get_db)):
    """Retrieves a detailed list of preferred pharmacies in the patient’s record."""
    try:
        logger.info("API: mdintegrations-get-patient-pharmacies")
        mdi_account_type, mdi_api = detect_mdi_account_type(db_session, patient_id)
        if mdi_api:
            res = mdi_api.get_patient_pharmacies(patient_id)
            return res
        return {"status": "failed", "error": "patient_id invalid"}
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@router.post('/mdintegrations-search-patient', tags=["mdintegrations"])
async def mdintegrations_search_patient_endpoint(request: Request):
    try:
        logger.info("API: mdintegrations-search-patient")
        data = await request.json()
        email = data["email"]
        params = {
            "search": email
        }
        test_type = data["test_type"]
        mdi_instance = mdi_instance_dict.get(test_type, 'normal')
        res = mdi_instance.search_patient(params)
        return res

    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@router.post('/mdintegrations-add-pharmacy-to-patient', tags=["mdintegrations"])
async def mdintegrations_add_pharmacy_to_patient_endpoints(data: MDintegrationsPatientPharmacy,
                                                           background_tasks: BackgroundTasks):
    try:
        logger.info("API: mdintegrations-add-pharmacy-to-patient")
        body = data.dict()
        logger.debug(body)

        background_tasks.add_task(mdi_attach_pharmacy_to_patient, data)

        return {"status": "success", "message": "Pharmacy being attached in background."}

    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@router.post('/mdintegrations-create-file', tags=["mdintegrations"])
async def mdintegrations_create_file_endpoint(file: UploadFile = File(...)):
    try:
        logger.info("API: mdintegrations-create-file")
        logger.debug(file.filename)
        data = await file.read()
        res = mdintegrations_api.create_file(data)
        logger.debug(res)
        return res

    except Exception as e:
        logger.exception(e)
        raise HTTPException(status_code=403, detail={"status": "failed", "error": str(e)})


@router.post('/mdintegrations-create-file-retool', tags=["mdintegrations"])
async def mdintegrations_create_file_retool_endpoint(request: Request):
    try:
        logger.info("API: mdintegrations-create-file-retool")
        data = await request.json()
        imgString = BytesIO(base64.b64decode(data['image']))
        test_type = data.get("test_type")
        mdi_instance = mdi_instance_dict.get(test_type, 'normal')
        res = mdi_instance.create_file(imgString)
        logger.debug(res)
        return res

    except Exception as e:
        logger.exception(e)
        raise HTTPException(status_code=403, detail={"status": "failed", "error": str(e)})


@router.post('/add-case-to-support', tags=["mdintegrations"])
async def add_case_to_support_endpoint(request: Request, db_session: Session = Depends(get_db)):
    logger.info("API: add-case-to-support")
    try:
        data = await request.json()
        logger.debug(data)
        case_id = data.get("case_id")
        if not case_id:
            return {"status": "failed", "error": "Invalid case_id"}
        mdi_account_type, mdi_api = detect_mdi_case_account_type(db_session, case_id)
        if mdi_api:
            case = mdi_api.add_case_to_support(case_id)
            return case
        else:
            return {"status": "failed", "error": "Invalid case_id"}
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}
