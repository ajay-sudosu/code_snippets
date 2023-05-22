from http.client import CannotSendHeader
import logging
from fastapi import APIRouter, Request, status, Response, BackgroundTasks
from typing import Optional
from db_client import DBClient
from mdintegrations import mdintegrations_api, mdintegrations_chat, MDintegrationsPatient, \
    WEBHOOK_SECRET, WEBHOOK_TOKEN, MDintegrationsPatientPharmacy, MDICreateHerpesCase, MDICasePrescription, \
    MDIPatientId, MDICreatePrescriptionsCase, MDICasePrescriptionUpdate, MDISearchPharmacy
from utils import download_file, delete_file
from bg_task.mdi_tasks import mdi_attach_pharmacy_to_patient, mdi_webhook_handle
from stripe_api import update_subscription

logger = logging.getLogger("fastapi")
router = APIRouter()

medication_dict = {
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


def _update_stripe_subscription_(subscription_id, patient_id_md, case_id, refills_ordered=1):
    """Update stripe subscription for refill count & new case id"""
    try:
        if subscription_id is None:
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
        # check token
        token = request.headers.get('Authorization')
        if token != WEBHOOK_TOKEN:
            response.status_code = status.HTTP_403_FORBIDDEN
            return {"message": "Invalid Token"}

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
        background_tasks.add_task(mdi_webhook_handle, data)
        return {"status": "success", "data": ""}

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
async def mdintegrations_get_case_messages_endpoint(request: Request):
    """Get all case's messages for the given patient"""
    try:
        data = await request.json()
        patient_id_md = data["patient_id_md"]
        messages = []
        response = mdintegrations_chat.get_patient_cases(patient_id_md)
        case_id = ""
        for case in response.get("data", []):
            case_id = case.get("case_id")
            response = mdintegrations_chat.get_messages(case_id, "patient")
            messages += response

        return {"status": "success", "data": messages, "case_id": case_id}

    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@router.post('/mdintegrations-create-case', tags=["mdintegrations"])
async def mdintegrations_create_case_endpoint(request: Request):
    try:
        data = await request.json()
        logger.debug(data)
        subscription_id = None
        if 'subscription_id' in data:
            subscription_id = data['subscription_id']
            del data['subscription_id']
        res = mdintegrations_api.create_case(data)
        logger.debug(res)
        if 'case_id' in res:
            _update_stripe_subscription_(subscription_id, data['patient_id'], res['case_id'], refills_ordered=1)
            return res
        raise Exception(res)

    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@router.get('/mdi-get-case', tags=["mdintegrations"])
async def mdintegrations_get_case_endpoint(case_id: str):
    """Get case details for the given case id"""
    try:
        response = mdintegrations_api.get_case(case_id)
        return response

    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@router.post('/mdintegrations-get-pharmacies', tags=["mdintegrations"])
async def mdintegrations_get_pharmacies_endpoints(data: MDISearchPharmacy):
    # At least one query parameter is required:
    try:
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
async def mdintegrations_get_prescriptions_endpoints(prescription: MDICasePrescription):
    """Fetch case prescriptions for given case id"""
    # At least one query parameter is required:
    try:
        data = prescription.dict()
        logger.debug(data)
        res = mdintegrations_api.get_prescription(case_id=prescription.case_id)
        logger.debug(res)
        if res is not None:
            return res
        raise Exception(res)

    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@router.post('/mdintegrations-update-prescriptions', tags=["mdintegrations"])
async def mdintegrations_update_prescriptions_endpoints(data: MDICasePrescriptionUpdate):
    """Update case prescriptions for given case id"""
    try:
        logger.debug(data.dict())
        res = mdintegrations_api.update_case_prescriptions(
            case_id=data.case_id, data=data.prescriptions)
        logger.debug(res)
        if res is not None:
            return res
        raise Exception(res)

    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@router.get('/mdi-get-case-questions', tags=["mdintegrations"])
async def mdintegrations_get_case_questions_endpoint(case_id: str):
    """Get case questions for the given case id"""
    try:
        response = mdintegrations_api.get_case_questions(case_id)
        return response

    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@router.post('/mdintegrations-patient-cases', tags=["mdintegrations"])
async def mdintegrations_get_patient_cases_endpoint(patient: MDIPatientId):
    """ Get all cases of a patient id"""
    try:
        data = patient.dict()
        logger.debug(data)
        res = mdintegrations_api.get_patient_cases(
            patient_id=patient.patient_id)
        logger.debug(res)
        return res

    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@router.post('/mdintegrations-create-patient', tags=["mdintegrations"])
async def mdintegrations_create_patient_endpoint(request: Request):
    try:
        data = await request.json()
        logger.debug(data)
        res = mdintegrations_api.create_patient(data)
        logger.debug(res)
        if 'patient_id' in res:
            return res
        raise Exception(res)

    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@router.get('/mdintegrations-get-patient', tags=["mdintegrations"])
async def mdintegrations_get_patient_endpoint(patient_id: str):
    try:
        res = mdintegrations_api.get_patient(patient_id)
        return res

    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@router.get('/mdintegrations-get-patient-pharmacies', tags=["mdintegrations"])
async def mdintegrations_get_patient_pharmacies_endpoint(patient_id: str):
    """Retrieves a detailed list of preferred pharmacies in the patient’s record."""
    try:
        res = mdintegrations_api.get_patient_pharmacies(patient_id)
        return res

    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@router.get('/mdintegrations-search-patient', tags=["mdintegrations"])
async def mdintegrations_search_patient_endpoint(email: Optional[str] = None):
    try:
        params = {
            "search": email
        }
        res = mdintegrations_api.search_patient(params)
        return res

    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@router.post('/mdintegrations-add-pharmacy-to-patient', tags=["mdintegrations"])
async def mdintegrations_add_pharmacy_to_patient_endpoints(data: MDintegrationsPatientPharmacy,
                                                           background_tasks: BackgroundTasks):
    try:
        body = data.dict()
        logger.debug(body)

        background_tasks.add_task(mdi_attach_pharmacy_to_patient, data)

        return {"status": "success", "message": "Pharmacy being attached in background."}

    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}
