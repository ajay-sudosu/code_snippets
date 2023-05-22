import logging
from fastapi import APIRouter, HTTPException , Request, UploadFile, File, Form
from healthie import healthie
from pydantic import BaseModel
from typing import Optional, List
from db_client import DBClient
import requests
import base64
from functions import *

logger = logging.getLogger("fastapi")
router = APIRouter()


class HealthiePatient(BaseModel):
    first_name: str
    last_name: str
    email: str
    phone_number: Optional[str]


class HealthiePatientUpdate(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str
    phone_number: Optional[str]
    dob: Optional[str]
    gender: Optional[str]
    height: Optional[str]


class HealthieGetPotentialAppointment(BaseModel):
   clients_can_book: bool
   provider_id: int


class HealthieGetAvailableDays(BaseModel):
   provider_id: str
   date_from_month: str
   appt_type_id: str


class HealthieGetAvailableSlots(BaseModel):
    provider_id: str
    start_date: str
    end_date: str
    timezone: str
    appt_type_id: str


class HealthieBookTheAppointment(BaseModel):
    appointment_type_id: str
    contact_type: str
    date: str
    first_name: str
    last_name: str
    email: str
    phone_number: str
    provider_id: str
    timezone: str


class HealthieCreatingAppointment(BaseModel):
    user_id: str
    appointment_type_id: str
    contact_type: str
    other_party_id: str
    datetime: str


class UpdateTheApointmentt(BaseModel):
    client_updating: bool
    datetime: str
    id: str


class StoringMatricData(BaseModel):
    user_id : str
    created_at : str
    weight : Optional[str]
    height : Optional[str]
    allergies : Optional[str]
    medications : Optional[str]
    age : Optional[str]
    gender : Optional[str]
    address : Optional[str]


class QueryingFilledOutForms(BaseModel):
    date: str
    custom_module_form_id: str


class CreatingFilledOutForms(BaseModel):
    finished: bool
    custom_module_form_id: str
    user_id: str
    form_answers: List[dict]


class HealthieRequestedFormCompletion(BaseModel):
    recipient_id : int
    custom_module_form_id : int


@router.get('/healthie-list-patient', tags=["healthie"])
async def healthie_list_patient_endpoint():
    try:
        res = healthie.list_patient()
        #print("res2", res)
        logger.debug(res)
        return res
        
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@router.post('/healthie-create-patient', tags=["healthie"])
async def healthie_create_patient_endpoint(patient: HealthiePatient):
    try:
        db = DBClient()
        data = patient.dict()
        logger.debug(data)
        res = healthie.create_patient(data)
        logger.debug(res)
        user = res["data"]["createClient"]["user"]
        if "id" in user:
            db.insert_healthie_patient(user_id=user["id"], email=user["email"])
            #print("Inserted into data")
        return {"status": True, "response": res}
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@router.get('/healthie-get-patient', tags=["healthie"])
async def healthie_get_patient_endpoint(id: int):
    try:
        res = healthie.get_patient(id=id)
        return res

    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@router.post('/healthie-update-patient', tags=["healthie"])
async def healthie_update_patient_endpoint(patient: HealthiePatientUpdate):
    try:
        data = patient.dict()
        logger.debug(data)
        response = healthie.update_patient(data)
        logger.debug(response)
        return response

    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@router.post('/healthie-get-potential-appointment', tags=["healthie"])
async def healthie_get_potential_appointment_and_contactTypes_endpoint(request:Request):
    try:
        data = await request.json()
        response = healthie.get_potential_appointment_and_contactTypes_self_scheduling()
        logger.debug(response)
        return response

    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@router.post('/healthie-get-available-days', tags=["healthie"])
async def healthie_get_available_days_endpoint(patient: HealthieGetAvailableDays):
    try:
        data = patient.dict()
        logger.debug(data)
        response = healthie.get_available_days_self_scheduling(data)
        logger.debug(response)
        return response

    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@router.post('/healthie-get-available-slots', tags=["healthie"])
async def healthie_get_available_slots_endpoint(patient: HealthieGetAvailableSlots):
    try:
        data = patient.dict()
        logger.debug(data)
        response = healthie.get_available_slots_self_scheduling(data)
        logger.debug(response)
        return response

    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@router.post('/healthie-book-the-appointment', tags=["healthie"])
async def healthie_book_the_appointment_endpoint(patient: HealthieBookTheAppointment):
    try:
        data = patient.dict()
        logger.debug(data)
        response = healthie.book_the_appointment_self_scheduling(data)
        logger.debug(response)
        return response

    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@router.post('/healthie-creating-appointment', tags=["healthie"])
async def healthie_creating_appointment_endpoint(patient: HealthieCreatingAppointment):
    try:
        data = patient.dict()
        logger.debug(data)
        response = healthie.creating_appointment(data)
        logger.debug(response)
        return response

    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@router.post('/healthie-Update-the-appointment', tags=["healthie"])
async def healthie_update_the_appointment_endpoint(patient: UpdateTheApointmentt):
    try:
        data = patient.dict()
        logger.debug(data)
        response = healthie.update_the_appointment(data)
        logger.debug(response)
        return response

    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@router.post('/healthie-storing-metric-data', tags=["healthie"])
async def storing_metric_data_endpoint(patient: StoringMatricData):
    try:
        data = patient.dict()
        if "weight" in data:
            weight_entry = {
                "metric_stat": data["weight"],
                "category": "Weight",
                "type": "MetricEntry",
                "user_id": data["user_id"],
                "created_at": data["created_at"]
            }
            healthie.storing_Metric_data(weight_entry)

        if "height" in data:
            height_entry = {
                "metric_stat": data["height"],
                "category": "Height",
                "type": "MetricEntry",
                "user_id": data["user_id"],
                "created_at": data["created_at"]
            }
            healthie.storing_Metric_data(height_entry)

        if "allergies" in data:
            allergies_entry = {
                "metric_stat": data["allergies"],
                "category": "Allergies",
                "type": "MetricEntry",
                "user_id": data["user_id"],
                "created_at": data["created_at"]
            }
            healthie.storing_Metric_data(allergies_entry)

        if "medications" in data:
            medications_entry = {
                "metric_stat": data["medications"],
                "category": "Medications",
                "type": "MetricEntry",
                "user_id": data["user_id"],
                "created_at": data["created_at"]
            }
            healthie.storing_Metric_data(medications_entry)

        if "age" in data:
            age_entry = {
                "metric_stat": data["age"],
                "category": "Age",
                "type": "MetricEntry",
                "user_id": data["user_id"],
                "created_at": data["created_at"]
            }
            healthie.storing_Metric_data(age_entry)

        if "gender" in data:
            gender_entry = {
                "metric_stat": data["gender"],
                "category": "Gender",
                "type": "MetricEntry",
                "user_id": data["user_id"],
                "created_at": data["created_at"]
            }
            healthie.storing_Metric_data(gender_entry)

        if "address" in data:
            address_entry = {
                "metric_stat": data["address"],
                "category": "Address",
                "type": "MetricEntry",
                "user_id": data["user_id"],
                "created_at": data["created_at"]
            }
            healthie.storing_Metric_data(address_entry)

        return {"status": "success"}

    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@router.post('/healthie-querying-filled-out-forms', tags=["healthie"])
async def querying_filled_out_forms_endpoint(patient: QueryingFilledOutForms):
    try:
        data = patient.dict()
        logger.debug(data)
        response = healthie.querying_filled_out_forms(data)
        logger.debug(response)
        return response

    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@router.post('/healthie-creating-filled-out-forms', tags=["healthie"])
async def creating_filled_out_forms_endpoint(patient: CreatingFilledOutForms):
    try:
        data = patient.dict()
        logger.debug(data)
        response = healthie.creating_filled_out_forms(data)
        logger.debug(response)
        return response

    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}

def get_as_base64(url):
    return base64.b64encode(requests.get(url).content)


@router.post('/healthie-get-custom-module-form', tags=["healthie"])
async def healthie_custom_module_form_completion_endpoint():
    try:
        response = healthie.get_custom_module_form_completion()
        logger.debug(response)
        return response

    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@router.post('/healthie-create-requested-form-completion', tags=["healthie"])
async def healthie_requested_form_completion_endpoint(patient: HealthieRequestedFormCompletion):
    try:
        data = patient.dict()
        logger.debug(data)
        response = healthie.create_requested_form_completion(data)
        logger.debug(response)
        return response

    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@router.post('/healthie-upload-document', tags=["healthie"])
async def healthie_create_document_endpoint(rel_user_id: str = Form(...),file_string: UploadFile = File(...),description: str = Form(...), from_date: str = Form(...), to_date: str = Form(...), include_in_charting: bool = Form(...), display_name: str = Form(...)):
    try:
        files = file_string.filename
        if not files:
            return {"status": "failed", "error": "No file"}

        elif files.lower().endswith(('.jpg')):
            url = get_s3_file_url(files)
            print("url", url)
            convert_base64 = get_as_base64(url)
            print("convert_base64", convert_base64)
            convert_base64_utf = convert_base64.decode("utf-8")
            file_string = "data:image/jpeg;base64," + convert_base64_utf

        elif files.lower().endswith(('.png')):
            url = get_s3_file_url(files)
            convert_base64 = get_as_base64(url)
            convert_base64_utf = convert_base64.decode("utf-8")
            file_string = "data:image/png;base64," + convert_base64_utf

        elif files.lower().endswith(('.pdf')):
            url = get_s3_file_url(files)
            convert_base64 = get_as_base64(url)
            convert_base64_utf = convert_base64.decode("utf-8")
            file_string = "data:application/pdf;base64," + convert_base64_utf

        else:
            return {"status": "failed", "error": "File type not supported please provide jpg or png"}

        data = {"rel_user_id": rel_user_id, "file_string": file_string, "description": description, "from_date": from_date, "to_date": to_date, "include_in_charting": include_in_charting, "display_name": display_name}
        response = healthie.upload_document(data)
        print("response", response)
        return response

    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}
