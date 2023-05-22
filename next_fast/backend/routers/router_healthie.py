import logging
from math import remainder
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Request
from healthie import healthie
from pydantic import BaseModel
from typing import Optional, List
from db_client import DBClient
import json
from fastapi.encoders import jsonable_encoder
from json import JSONEncoder
import requests
import base64
from functions import *
import os
import PyPDF2
# import json as js
import requests
from utils import send_text_message, send_text_email

ALLOWED_EXTENSIONS = ['.pdf']


logger = logging.getLogger("fastapi")
router = APIRouter()


class HealthiePatientAllInOne(BaseModel):
    first_name: str
    last_name: str
    email: str
    phone_number: str
    weight: str
    height: str
    allergies: str
    age: str
    gender: str
    dietitian_id: Optional[str]
    user_group_id: Optional[str]
    address: str
    dob: str
    created_at: str
    include_in_charting: bool
    display_name: str
    file_string: str
    dont_send_welcome: bool


class StoringMatricDataAllInOne(BaseModel):
    created_at: str
    weight: str
    height: str
    user_id: str
    allergies: Optional[str]
    age: Optional[str]
    gender: Optional[str]
    address: Optional[str]


class HealthiePatient(BaseModel):
    first_name: str
    last_name: str
    email: str
    phone_number: Optional[str]
    dietitian_id: Optional[str]
    legal_name: Optional[str]


class HealthiePatientRetrieveChat(BaseModel):
    id: int
    provider_id: Optional[int]


class HealthiePatientUpdate(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str
    phone_number: Optional[str]
    legal_name: Optional[str]
    dob : Optional[str]
    user_group_id: str
    gender : Optional[str]
    height : Optional[str]
    pronouns : Optional[str]
    dietitian_id: Optional[str]
    location : dict
    policies : list


class HealthieGetAvailableDays(BaseModel):
    provider_id: str
    date_from_month: str
    appt_type_id: str
    org_level: Optional[bool]
    licensed_in_state: Optional[str]
    timezone: Optional[str]
    # timezone : str


class HealthieGetAvailableSlots(BaseModel):
    provider_id: str
    start_date: str
    end_date: str
    org_level: Optional[bool]
    timezone : str
    licensed_in_state: Optional[str]
    appt_type_id: str


class HealthieBookTheAppointment(BaseModel):
    first_name: Optional[str]
    last_name: Optional[str]
    email: Optional[str]
    phone_number: Optional[str]
    appointment_type_id: str
    contact_type: str
    date: str
    provider_id: str
    timezone: str


class HealthieCreatingAppointment(BaseModel):
    user_id: str
    appointment_type_id: str
    contact_type: str
    datetime: str
    providers: Optional[str]
    recurring_appointment: Optional[dict]
    timezone: Optional[str]


class HealthieDeletingAppointment(BaseModel):
    appointment_id: str
    delete_recurring: Optional[bool]


class GetTheReschedulingAppointmentID(BaseModel):
    filter: str
    should_paginate: bool
    is_active: bool


class GetTheReschedulingAvailableDays(BaseModel):
    provider_id: str 
    date_from_month: str 
    timezone: str
    appt_type_id: str 
    appointment_to_reschedule_id: int
    licensed_in_state: Optional[str]


class GetTheReschedulingAvailableSlots(BaseModel):
    provider_id: str
    start_date: str
    end_date: str
    timezone: str
    appt_type_id: str
    appointment_to_reschedule_id: int
    licensed_in_state: Optional[str]


class UpdateTheReschedulingAppointment(BaseModel):
    datetime: str
    id: str
    pm_status: Optional[str]
    timezone: Optional[str]


class StoringMatricData(BaseModel):
    user_id : str
    created_at : str
    weight : str
    height : str
    allergies : Optional[str]
    medications : Optional[str]
    age : Optional[str]
    gender : Optional[str]
    address : Optional[str]

class CreatingFilledOutForms(BaseModel):
    finished : bool
    custom_module_form_id : str
    user_id : str
    form_answers : list
    # label: str

class AfterVisitSummary(BaseModel):
    user_id : str

class CreatingFilledOutPAForm(BaseModel):
    finished : bool
    user_id : str
    form_answers : list

class HealthieCreateAllergySensitivity(BaseModel):
    user_id : str
    category : Optional[str]
    category_type: Optional[str]
    is_current: bool
    name: str
    custom_name: Optional[str]
    reaction: str
    custom_reaction: Optional[str]
    severity: Optional[str]

class HealthieCreateMedication(BaseModel):
    user_id: str
    active: bool
    comment: Optional[str]
    directions: Optional[str]
    dosage: str
    custom_name: Optional[str]
    end_date: Optional[str]
    name: str
    start_date: Optional[str]

class HealthieRequestedFormCompletion(BaseModel):
    recipient_id : int
    custom_module_form_id : int


class HealthieGetPatientRecentConversation(BaseModel):
    user_id : int


class HealthieUpdatePolicy(BaseModel):
    id : int
    type_string: str
    holder_first: str
    holder_mi: str
    holder_last: str
    holder_dob: str
    holder_gender: str
    holder_phone: str
    notes: str
    insurance_card_front_id: str
    insurance_card_back_id: str

class HealthiePrescription(BaseModel):
    patient_id: int
    status: str

class HealthieAddedUsers(BaseModel):
    label: str
    value: int


class HealthieCreateConversation(BaseModel):
    simple_added_users: Optional[str] # UserGroup if applicable
    owner_id: int  # staff id who owns chat
    name: str  # title of the chat


class HealthieUpdateConversation(BaseModel):
    id: int # conversation id
    simple_added_users: Optional[str] 
    name: Optional[str] # conversation title
    closed_by_id: Optional[int] # user id, closes convo

class HealthieListConversations(BaseModel):
    active_status: str # active, archived, closed
    read_status: str # all, read, unread
    conversation_type: str # all, individulal, community
    client_id : str # healthie patient id


class HealthieListAppointments(BaseModel):
    is_active: bool
    with_all_statuses: bool
    user_id: int
    sort_by: str


class HealthieCreateNote(BaseModel):
    user_id: str
    conversation_id: str
    content : str

class HealthiCreateWebhoks(BaseModel):
    resource_id: int
    # path: str
    resource_id_type: Optional[str]
    event_type: Optional[str]

class HealthieCreateTask(BaseModel):
    user_id: Optional[str]
    content: str
    seen: Optional[bool]
    client_id: Optional[str]
    created_by_id: Optional[str]
    due_date: Optional[str]
    remainder: Optional[dict]

class HealthieUploadDocument(BaseModel):
    rel_user_id: str
    include_in_charting: str
    display_name: str
    description: str
    from_date: str
    to_date: str
    file_string: str

class HealthieCreateDocs(BaseModel):
    rel_user_id: str
    include_in_charting: bool
    display_name: str
    file_string: str

class HealthieSendMessage(BaseModel):
    user_id: str
    conversation_id: str
    content: Optional[str]
    attached_image_string: Optional[str]


class HealthiePolicies(BaseModel):
    insurance_plan_id: str
    holder_relationship: str
    name: str
    holder_dob: str
    num: str


class HealthieLocations(BaseModel):
    name: str
    state: str
    country: str
    city: str
    line1: Optional[str]
    line2: Optional[str]
    zip: str


class HealthieMedications(BaseModel):
    name: str


class HealthieAllergies(BaseModel):
    name: str


class HealthieFormAnswers(BaseModel):
    custom_module_id: str
    answer: str


class HealthieChartingNotes(BaseModel):
    custom_module_form_id: str
    form_answers: Optional[List[HealthieFormAnswers]]


class UpdatePatientHealtieData(BaseModel):
    first_name: str
    last_name: str
    email: str
    share_with_rel: bool = True
    phone_number: str
    dont_send_welcome: bool = True
    photo_id: bool = False
    dietitian_id: str
    weight: str
    height: str
    charting_notes: Optional[HealthieChartingNotes]
    allergies: List[HealthieAllergies]
    medications: List[HealthieMedications]
    age: str
    gender: str
    address: str
    dob: str
    created_at: str
    include_in_charting: bool = False
    display_name: str
    location: HealthieLocations
    policies: List[HealthiePolicies]
    file_string: str


@router.get('/healthie-list-patient', tags=["healthie"])
async def healthie_list_patient_endpoint():
    try:
        logger.info("API: healthie-list-patient")
        res = healthie.list_patient()
        print("res2", res)
        logger.debug(res)
        return res
        
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@router.get('/healthie-list-all-patients', tags=["healthie"])
async def healthie_list_all_patient_endpoint():
    try:
        logger.info("API: healthie-list-all-patients")
        res = healthie.list_all_patients()
        logger.debug(res)
        return res
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@router.post('/healthie-create-patient', tags=["healthie"])
async def healthie_create_patient_endpoint(patient: HealthiePatient):
    try:
        logger.info("API: healthie-create-patient")
        db = DBClient()
        data = patient.dict()
        logger.debug(data)
        res = healthie.create_patient(data)
        logger.debug(res)
        user = res["data"]["createClient"]["user"]
        if "id" in user:
            db.insert_healthie_patient(user_id=user["id"], email=user["email"])
            print("Inserted into data")
        return {"status": True, "response": res}
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@router.post('/healthie-create-patient-all-in-one', tags=["healthie"])
async def healthie_create_patient_all_in_one_endpoint(patient: HealthiePatientAllInOne):
    try:
        logger.info("API: healthie-create-patient-all-in-one")
        db = DBClient()
        data1 = patient.dict()
        logger.debug(data1)
        # Create Patient API
        res = healthie.create_patient_all_in_one(data1)
        get_user_id = res["data"]["createClient"]["user"]
        logger.debug(res)
        user = get_user_id['id']
        if "id" in user:
            db.insert_healthie_patient(user_id=user["id"], email=user["email"])
        data1["user_id"] = str(get_user_id['id'])
        # storing metric data API
        Store_matric_data = await storing_metric_data_all_in_one_endpoint(StoringMatricDataAllInOne(**data1))
        data1["rel_user_id"] = str(get_user_id['id'])
        if user:
            # Upload document API
            upload_document_one = healthie.upload_document_all_in_one(data1)
            upload_document_one["data"]["createDocument"]["document"]["id"]
            data1["user_id"]: str(get_user_id['id'])
            data1["id"] = str(get_user_id['id'])
            data_to_update_patient = {
                'id': str(get_user_id['id']),
                'dob': data1['dob'],
                'gender': data1['gender'],
                'dietitian_id': data1['dietitian_id'],
                'height': data1['height']
            }
            # data1["policies"][0]["insurance_card_front_id"] = str(get_insurance_front_id)
            # print(data1["policies"][0])

            # Update Patient API
            update_patient = healthie.update_patient_all_in_one(data_to_update_patient)
                
        return {"status": True, "create_patient": res, "store_matric_data": Store_matric_data, "upload_document": upload_document_one, "update_patient": update_patient}
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@router.post('/healthie-get-patient', tags=["healthie"])
async def healthie_get_patient_endpoint(id: int):
    try:
        logger.info("API: healthie-get-patient")
        res = healthie.get_patient(id_=id)
        return res

    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@router.post('/healthie-get-patient-recent-conversation', tags=["healthie"])
async def healthie_get_patient_recent_conversation_endpoint(user: HealthieGetPatientRecentConversation):
    try:
        logger.info("API: healthie-get-patient-recent-conversation")
        data = user.dict()
        recent_conversation_id = healthie.get_patient_recent_conversation(user_id=data.get('user_id'))
        if not recent_conversation_id.get('data', {}).get('user', {}):
            raise Exception('User not found')
        recent_conversation_content = healthie.\
            retrieve_conversation_by_id(recent_conversation_id.
                                        get('data', {}).get('user', {}).
                                        get('last_conversation_id'))
        return recent_conversation_content
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}

@router.post('/healthie-get-patient-conversation-memberships', tags=["healthie"])
async def healthie_get_patient_conversation_membership_endpoint(user: HealthieGetPatientRecentConversation):
    try:
        logger.info("API: healthie-get-patient-conversation-memberships")
        data = user.dict()
        recent_conversations = healthie.get_patient_conversation_memberships(user_id=data.get('user_id'))
        return recent_conversations
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@router.post('/healthie-update-patient', tags=["healthie"])
async def healthie_update_patient_endpoint(patient: HealthiePatientUpdate):
    try:
        logger.info("API: healthie-update-patient")
        data = patient.dict()
        print("data", data)
        logger.debug(data)
        response = healthie.update_patient(data)
        logger.debug(response)
        return response

    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@router.post('/healthie-get-potential-appointment', tags=["healthie"])
async def healthie_get_potential_appointment_and_contactTypes_endpoint():
    try:
        logger.info("API: healthie-get-potential-appointment")
        response = healthie.get_potential_appointment_and_contactTypes_self_scheduling()
        logger.debug(response)
        return response

    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@router.post('/healthie-get-available-days', tags=["healthie"])
async def healthie_get_available_days_endpoint(patient: HealthieGetAvailableDays):
    try:
        logger.info("API: healthie-get-available-days")
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
        logger.info("API: healthie-get-available-slots")
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
        logger.info("API: healthie-book-the-appointment")
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
        logger.info("API: healthie-creating-appointment")
        data = patient.dict()
        logger.debug(data)
        response = healthie.creating_appointment(data)
        logger.debug(response)
        return response

    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@router.post('/healthie-deleting-appointment', tags=["healthie"])
async def healthie_deleting_appointment_endpoint(patient: HealthieDeletingAppointment):
    try:
        logger.info("API: healthie-deleting-appointment")
        data = patient.dict()
        logger.debug(data)
        response = healthie.deleting_appointment(data)
        logger.debug(response)
        return response

    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@router.post('/healthie-get-the-rescheduling-appointment_id', tags=["healthie"])
async def healthie_get_rescheduling_appointment_id_endpoint(patient: GetTheReschedulingAppointmentID):
    try:
        logger.info("API: healthie-get-the-rescheduling-appointment_id")
        data = patient.dict()
        logger.debug(data)
        response = healthie.get_the_rescheduling_appointment_id(data)
        logger.debug(response)
        return response

    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@router.post('/healthie-get-the-rescheduling-available_days', tags=["healthie"])
async def healthie_get_rescheduling_available_days_endpoint(patient: GetTheReschedulingAvailableDays):
    try:
        logger.info("API: healthie-get-the-rescheduling-available_days")
        data = patient.dict()
        logger.debug(data)
        response = healthie.get_rescheduling_available_days(data)
        logger.debug(response)
        return response

    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@router.post('/healthie-get-the-rescheduling-available_slots', tags=["healthie"])
async def healthie_get_rescheduling_available_slots_endpoint(patient: GetTheReschedulingAvailableSlots):
    try:
        logger.info("API: healthie-get-the-rescheduling-available_slots")
        data = patient.dict()
        logger.debug(data)
        response = healthie.get_rescheduling_available_slots(data)
        logger.debug(response)
        return response

    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@router.post('/healthie-update-the-rescheduling-appointment', tags=["healthie"])
async def healthie_update_rescheduling_appointment_endpoint(patient: UpdateTheReschedulingAppointment):
    try:
        logger.info("API: healthie-update-the-rescheduling-appointment")
        data = patient.dict()
        logger.debug(data)
        response = healthie.update_rescheduling_appointment(data)
        logger.debug(response)
        return response

    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@router.post('/healthie-storing-metric-data', tags=["healthie"])
async def storing_metric_data_endpoint(patient: StoringMatricData):
    try:
        logger.info("API: healthie-storing-metric-data")
        data = patient.dict()
        print("data1", data)
        
        if "weight" in data:
            weight_entry = {
                "metric_stat": data["weight"],
                "category": "Weight",
                "type": "MetricEntry",
                "user_id": data["user_id"],
                "created_at": data["created_at"]
            }
            healthie.storing_Metric_data(weight_entry)
            print("weight_entry", weight_entry)

        if "height" in data:
            height_entry = {
                "metric_stat": data["height"],
                "category": "Height",
                "type": "MetricEntry",
                "user_id": data["user_id"],
                "created_at": data["created_at"]
            }
            healthie.storing_Metric_data(height_entry)
            print("height_entry", height_entry)

        if "allergies" in data:
            allergies_entry = {
                "metric_stat": data["allergies"],
                "category": "Allergies",
                "type": "MetricEntry",
                "user_id": data["user_id"],
                "created_at": data["created_at"]
            }
            healthie.storing_Metric_data(allergies_entry)
            print("allergies_entry", allergies_entry)

        if "medications" in data:
            medications_entry = {
                "metric_stat": data["medications"],
                "category": "Medications",
                "type": "MetricEntry",
                "user_id": data["user_id"],
                "created_at": data["created_at"]
            }
            healthie.storing_Metric_data(medications_entry)
            print("medications_entry", medications_entry)

        if "age" in data:
            age_entry = {
                "metric_stat": data["age"],
                "category": "Age",
                "type": "MetricEntry",
                "user_id": data["user_id"],
                "created_at": data["created_at"]
            }
            healthie.storing_Metric_data(age_entry)
            print("age_entry", age_entry)

        if "gender" in data:
            gender_entry = {
                "metric_stat": data["gender"],
                "category": "Gender",
                "type": "MetricEntry",
                "user_id": data["user_id"],
                "created_at": data["created_at"]
            }
            healthie.storing_Metric_data(gender_entry)
            print("gender_entry", gender_entry)

        if "address" in data:
            address_entry = {
                "metric_stat": data["address"],
                "category": "Address",
                "type": "MetricEntry",
                "user_id": data["user_id"],
                "created_at": data["created_at"]
            }
            healthie.storing_Metric_data(address_entry)
            print("address_entry", address_entry)

        return {"status": "success"}

    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@router.post('/healthie-storing-metric-data_all_in_one', tags=["healthie"])
async def storing_metric_data_all_in_one_endpoint(patient: StoringMatricDataAllInOne):
    try:
        logger.info("API: healthie-storing-metric-data_all_in_one")
        data = patient.dict()
        weight_entry, height_entry, allergies_entry = None, None, None
        age_entry, gender_entry, address_entry = None, None, None
        if data.get("weight"):
            weight_entry = {
                "metric_stat": data["weight"],
                "category": "Weight",
                "type": "MetricEntry",
                "user_id": data["user_id"],
                "created_at": data["created_at"]
            }
            healthie.storing_Metric_data(weight_entry)
        if data.get("height"):
            height_entry = {
                "metric_stat": data["height"],
                "category": "Height",
                "type": "MetricEntry",
                "user_id": data["user_id"],
                "created_at": data["created_at"]
            }
            healthie.storing_Metric_data(height_entry)
        if data.get("allergies"):
            allergies_entry = {
                "metric_stat": data["allergies"],
                "category": "Allergies",
                "type": "MetricEntry",
                "user_id": data["user_id"],
                "created_at": data["created_at"]
            }
            healthie.storing_Metric_data(allergies_entry)
        if data.get("age"):
            age_entry = {
                "metric_stat": data["age"],
                "category": "Age",
                "type": "MetricEntry",
                "user_id": data["user_id"],
                "created_at": data["created_at"]
            }
            healthie.storing_Metric_data(age_entry)
        if data.get("gender"):
            gender_entry = {
                "metric_stat": data["gender"],
                "category": "Gender",
                "type": "MetricEntry",
                "user_id": data["user_id"],
                "created_at": data["created_at"]
            }
            healthie.storing_Metric_data(gender_entry)
        if data.get("address"):
            address_entry = {
                "metric_stat": data["address"],
                "category": "Address",
                "type": "MetricEntry",
                "user_id": data["user_id"],
                "created_at": data["created_at"]
            }
            healthie.storing_Metric_data(address_entry)
        return {
            "status": "success", "weight_entry": weight_entry, "height_entry": height_entry,
            "allergies_entry": allergies_entry, "age_entry": age_entry, "gender_entry": gender_entry,
            "address_entry": address_entry
        }
    except Exception as e:
        logger.exception(f"storing_metric_data_all_in_one_endpoint ==> {str(e)}")
        return {"status": "failed", "error": str(e)}


@router.post('/healthie-querying-filled-out-forms', tags=["healthie"])
async def querying_filled_out_forms_endpoint():
    try:
        logger.info("API: healthie-querying-filled-out-forms")
        response = healthie.querying_filled_out_forms()
        logger.debug(response)
        return response

    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@router.post('/healthie-querying-after-visit-summaries', tags=["healthie"])
async def querying_after_visit_summaries(patient: AfterVisitSummary):
    try:
        logger.info("API: healthie-querying-after-visit-summaries")
        data = patient.dict()
        logger.debug(data)
        response = healthie.querying_after_visit_summaries(data)
        logger.debug(response)
        return response

    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@router.post('/healthie-creating-filled-out-pa-form', tags=["healthie"])
async def creating_filled_out_pa_form_endpoint(patient: CreatingFilledOutPAForm):
    try:
        logger.info("API: healthie-creating-filled-out-pa-form")
        data = patient.dict()
        logger.debug(data)
        response = healthie.creating_filled_out_pa_forms(data)
        logger.debug(response)
        return response

    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}

@router.post('/healthie-creating-filled-out-forms', tags=["healthie"])
async def creating_filled_out_forms_endpoint(patient: CreatingFilledOutForms):
    try:
        logger.info("API: healthie-creating-filled-out-forms")
        data = patient.dict()
        logger.debug(data)
        response = healthie.creating_filled_out_forms(data)
        logger.debug(response)
        return response

    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@router.post('/healthie-create-allergy-sensitivity', tags=["healthie"])
async def healthie_create_allergy_sensitivity_endpoint(patient: HealthieCreateAllergySensitivity):
    try:
        logger.info("API: healthie-create-allergy-sensitivity")
        data = patient.dict()
        logger.debug(data)
        response = healthie.create_allergy_sensitivity(data)
        logger.debug(response)
        return response

    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}

@router.post('/healthie-create-medication', tags=["healthie"])
async def healthie_create_medication_endpoint(medication_list: List[HealthieCreateMedication]):
    try:
        logger.info("API: healthie-create-medication")
        response_list = []
        for medication in medication_list:
            data = medication.dict()
            logger.debug(data)
            response = healthie.create_medication(data)
            response_list.append(response)
            logger.debug(response)
        return response_list

    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}

@router.post('/healthie-create-new-docs', tags=["healthie"])
async def healthie_create_medication_endpoint(patient: HealthieCreateDocs):
    try:
        logger.info("API: healthie-create-new-docs")
        data = patient.dict()
        logger.debug(data)
        response = healthie.upload_document_all_in_one(data)
        logger.debug(response)
        return response

    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@router.post('/healthie-upload-document', tags=["healthie"])
async def healthie_create_document_endpoint(rel_user_id: str = Form(...), file_string: UploadFile = File(...),description: str = Form(...), from_date: str = Form(...), to_date: str = Form(...), include_in_charting: bool = Form(...), display_name: str = Form(...)):
    try:
        logger.info("API: healthie-upload-document")
        print("file_string", file_string)
        filename = await file_string.read()
        print(filename)
        if not filename:
            return {"status": "failed", "error": "No file uploaded"}
        elif filename:
            base64_string = base64.b64encode(filename).decode('utf-8')
            file_string = "data:application/pdf;base64," + base64_string
        else:
            return {"status": "failed", "error": "only valid pdf files!"}

        data = {"rel_user_id": rel_user_id, "file_string": file_string, "description": description, "from_date": from_date, "to_date": to_date, "include_in_charting": include_in_charting, "display_name": display_name}
        response = healthie.upload_document(data)
        print("response", response)
        return response

    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@router.post('/healthie-get-insurance-plans', tags=["healthie"])
async def healthie_get_insurance_plans_endpoint():
    try:
        logger.info("API: healthie-get-insurance-plans")
        response = healthie.get_insurance_plans()
        logger.debug(response)
        return response

    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@router.post('/healthie-get-custom-module-form', tags=["healthie"])
async def healthie_custom_module_form_completion_endpoint():
    try:
        logger.info("API: healthie-get-custom-module-form")
        response = healthie.get_custom_module_form_completion()
        logger.debug(response)
        return response

    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@router.post('/healthie-create-requested-form-completion', tags=["healthie"])
async def healthie_requested_form_completion_endpoint(patient: HealthieRequestedFormCompletion):
    try:
        logger.info("API: healthie-create-requested-form-completion")
        data = patient.dict()
        logger.debug(data)
        response = healthie.create_requested_form_completion(data)
        logger.debug(response)
        return response

    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


def get_as_base64(url):
    return base64.b64encode(requests.get(url).content)


# @router.post('/healthie-update-policy', tags=["healthie"])
# async def healthie_update_policy_endpoint(id : str = Form(...), type_string : str = Form(...), holder_first : str = Form(...), holder_mi : str = Form(...), holder_last : str = Form(...), holder_dob : str = Form(...), holder_gender : str = Form(...), holder_phone : str = Form(...), notes : str = Form(...), insurance_card_front_id: UploadFile = File(...), insurance_card_back_id: UploadFile = File(...)):
#     try:

#         if not insurance_card_front_id:
#             return {"status": "failed", "error": "No file"}
        
#         elif insurance_card_front_id.filename.lower().endswith(('.jpg')) or insurance_card_front_id.filename.lower().endswith(('.png')):
#             frontfile = await insurance_card_front_id.read()
#             base64_string = base64.b64encode(frontfile).decode('utf-8')
#             insurance_card_front_base64 = "data:"+ insurance_card_front_id.content_type +";base64," + base64_string
#             #insurance_card_front_base64 = get_s3_file_url(insurance_card_front_id)
#             #insurance_card_front_base64 = "https://s3.amazonaws.com/healthie-staging/image/1142/original/nextmed_logo.webp?1654006516"
        
#         else:
#             return {"status": "failed", "error": "Please provide jpg/png files!"}

#         if not insurance_card_back_id:
#             return {"status": "failed", "error": "No file"}
    
#         elif insurance_card_back_id.filename.lower().endswith(('.jpg')) or insurance_card_back_id.filename.lower().endswith(('.png')):
#             backfile = await insurance_card_back_id.read()
#             base64_string = base64.b64encode(backfile).decode('utf-8')
#             insurance_card_back_base64 = "data:"+ insurance_card_back_id.content_type +";base64," + base64_string
#             #insurance_card_back_base64 = get_s3_file_url(insurance_card_back_id)
#             #insurance_card_back_base64 = "https://s3.amazonaws.com/healthie-staging/image/1142/original/nextmed_logo.webp?1654006516"
        
#         else:
#             return {"status": "failed", "error": "Please provide jpg/png files!"}
            
#         if not insurance_card_front_base64:
#             return {"status": "failed", "error": "Only jpg or png files!"}      

#         if not insurance_card_back_base64:
#             return {"status": "failed", "error": "Only jpg or png files!"}

#         data = {"id": id, "type_string": type_string, "holder_first": holder_first, "holder_mi": holder_mi, "holder_last": holder_last, "holder_dob": holder_dob, "holder_gender": holder_gender, "holder_phone": holder_phone, "notes": notes, "insurance_card_front_id": insurance_card_front_base64, "insurance_card_back_id": insurance_card_back_base64}

#         print(data)
#         response = healthie.update_policy(data)
#         print("response", response)
#         return response
        
#     except Exception as e:
#         logger.exception(e)
#         return {"status": "failed", "error": str(e)}

@router.post('/healthie-update-policy', tags=["healthie"])
async def healthie_update_policy_endpoint(patient: HealthieUpdatePolicy):
    try:
        logger.info("API: healthie-update-policy")
        data = patient.dict()
        logger.debug(data)
        response = healthie.update_policy(data)
        logger.debug(response)
        return response

    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@router.post('/healthie-prescriptions', tags=["healthie"])
async def healthie_prescriptions_endpoint(patient: HealthiePrescription):
    try:
        logger.info("API: healthie-prescriptions")
        data = patient.dict()
        logger.debug(data)
        response = healthie.prescriptions(data)
        logger.debug(response)
        return response

    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


# @router.post('/healthie-create-conversation', tags=["healthie"])
# async def healthie_create_conversation_endpoint(patient: HealthieCreateConversation):
#     try:
#         data = patient.dict()
#         logger.debug(data)
#         response = healthie.create_conversation(data)
#         logger.debug(response)
#         return response
#     except Exception as e:
#         logger.exception(e)
#         return {"status": "failed", "error": str(e)}


@router.post('/healthie-create-conversation', tags=["healthie"])
async def healthie_create_conversation_endpoint(conversation:HealthieCreateConversation):
    try:
        logger.info("API: healthie-create-conversation")
        data = conversation.dict()
        res = healthie.create_conversation(data)
        return res
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}
    

# @router.post('/healthie-create-note', tags=["healthie"])
# async def healthie_create_note_endpoint(user_id : str = Form(...), conversation_id : str = Form(...), content : str = Form(...), attached_image_string : UploadFile = File(...), scheduled_at: str = Form(...)):
#     try:
#         filename = await attached_image_string.read()
#         print(filename)
#         if not filename:
#             return {"status": "failed", "error": "No file uploaded, please upload image"}
#         elif filename:
#             base64_string = base64.b64encode(filename).decode('utf-8')
#             attached_image_string = "data:application/pdf;base64," + base64_string
#         else:
#             return {"status": "failed", "error": "only valid pdf files!"}
#         data = {"user_id": user_id, "conversation_id": conversation_id, "content": content, "attached_image_string": attached_image_string, "scheduled_at": scheduled_at}
#         logger.debug(data)
#         response = healthie.create_note(data)
#         logger.debug(response)
#         return response
#     except Exception as e:
#         logger.exception(e)
#         return {"status": "failed", "error": str(e)}


@router.post('/healthie-retrieving-conversation', tags=["healthie"])
async def healthie_retrieving_conversation_endpoint(patient:HealthiePatientRetrieveChat):
    try:
        logger.info("API: healthie-retrieving-conversation")
        data = patient.dict()
        res = healthie.retrieve_conversation(id=data["id"], provider_id=data["provider_id"])
        print(res)
        return res

    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@router.post('/healthie-update-conversation', tags=["healthie"])
async def healthie_update_conversation_endpoint(patient: HealthieUpdateConversation):
    try:
        logger.info("API: healthie-update-conversation")
        data = patient.dict()
        logger.debug(data)
        print("data", data)
        response = healthie.update_conversation(data)
        logger.debug(response)
        return response

    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@router.post('/healthie-create-task', tags=["healthie"])
async def healthie_create_task_endpoint(patient: HealthieCreateTask):
    try:
        logger.info("API: healthie-create-task")
        data = patient.dict()
        logger.debug(data)
        response = healthie.create_task(data)
        logger.debug(response)
        return response
    except Exception as e:
        logger.exception(f"healthie_create_task_endpoint ==> {str(e)}")
        return {"status": "failed", "error": str(e)}


@router.post('/healthie-create-webhooks', tags=["healthie"])
async def healthie_create_webhooks_endpoint(patient: HealthiCreateWebhoks):
    try:
        logger.info("API:healthie-create-webhooks")
        data = patient.dict()
        logger.debug(data)
        print("data", data)
        response = healthie.create_webhooks(data)
        logger.debug(response)
        return response

    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@router.post('/healthie-webhook', tags=["healthie"])
async def healthie_webhook(request: Request):
    """
    Healthie webhook record payload
    """
    msg = "Success"
    logger.info("API: healthie-webhook")
    payload = await request.body()
    logger.info("healthie-webhook ==> " + str(payload))
    try:
        payload = json.loads(payload)
        if payload and payload.get('event_type', '') == "message.created":
            note_information = healthie.retrieve_note({"id": payload.get('resource_id')})
            conversation_id = note_information.get('data', {}).get('note', {}).get('conversation_id')
            if conversation_id:
                conversation_information = healthie.retrieve_conversation_by_id(id_=conversation_id)
                healthie_patient_id = conversation_information.get('data', {}).get('conversation', {}).get('patient_id')
                if healthie_patient_id:
                    healthie_patient_information = healthie.get_patient(id_=healthie_patient_id)
                    healthie_patient = healthie_patient_information.get('data', {}).get('user', {})
                    first_name = healthie_patient.get("first_name")
                    email = healthie_patient.get("email")
                    phone_number = healthie_patient.get("phone_number")
                    msg = f'Hi {first_name}, Your doctor has sent you a message. ' \
                          f'You can view it and respond at https://joinnextmed.com/messages/ ' \
                          f'Thanks'

                    send_text_email(sender='team@joinnextmed.com',
                                    recipient=email,
                                    subject='Next Medical New Message',
                                    content=msg)

                    try:
                        send_text_message(to_phone=phone_number,
                                          message=msg)
                    except Exception as e:
                        logger.exception(e)

    except Exception as e:
        logger.exception(e)
        msg = "Failure"
    return {"status": msg} 


@router.post('/healthie-list-conversations', tags=["healthie"])
async def healthie_list_conversations_endpoint(conversations: HealthieListConversations):
    try:
        logger.info("API: healthie-list-conversations")
        data = conversations.dict()
        logger.debug(data)
        response = healthie.retrieve_list_conversations(data)
        return response
    except Exception as e:
        logger.exception("healthie_list_endpoint ==> " + str(e))
        return {"status": "failed", "error": str(e)}


@router.get('/retrieve-healthie-prescriptions/{patient_id}', tags=["healthie"])
async def retrieve_healthie_prescriptions_endpoint(patient_id: int):
    try:
        logger.info("API: retrieve-healthie-prescriptions")
        response = healthie.retrieve_presecriptions({"patient_id": patient_id})
        return response
    except Exception as e:
        logger.exception("retrieve_healthie_prescriptions_endpoint ==> " + str(e))
        return {"status": "failed", "error": str(e)}


@router.post('/healthie-list-appointments', tags=["healthie"])
async def healthie_list_appointments_endpoint(request: HealthieListAppointments):
    try:
        logger.info("API: healthie-list-appointments")
        data = request.dict()
        logger.debug(data)
        response = healthie.list_appointments(data)
        return response
    except Exception as e:
        logger.exception("healthie_list_appointments_endpoint ==> " + str(e))
        return {"status": "failed", "error": str(e)}

@router.post('/healthie-send-message', tags=["healthie"])
async def healthie_send_message_endpoint(message: HealthieSendMessage):
    try:
        logger.info("API: healthie-send-message")
        data = message.dict()
        res = healthie.send_message(data)
        return res
    except Exception as e:
        logger.exception("healthie_send_message_endpoint ==> " + str(e))
        return {"status": "failed", "error": str(e)}

@router.post('/healthie-conversation-memberships', tags=["healthie"])
async def healthie_conversation_memberships_endpoint(client_id: int):
    try:
        logger.info("API: healthie-conversation-memberships")
        response = healthie.conversation_membership({"client_id": client_id})
        return response
    except Exception as e:
        logger.exception("healthie_conversation_memberships_endpoint ==> " + str(e))
        return {"status": "failed", "error": str(e)}
