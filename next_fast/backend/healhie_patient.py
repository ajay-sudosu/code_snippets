import logging
from math import remainder
from pickle import NONE
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Request
from healthie import healthie
from pydantic import BaseModel
from typing import Optional
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


class StoringMatricDataAllInOne(BaseModel):
    created_at : str
    weight : str
    height : str
    allergies : Optional[str]
    age : Optional[str]
    gender : Optional[str]
    address : Optional[str]

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
    address: str
    dob: str
    created_at: str
    include_in_charting: bool
    display_name: str
    file_string: str
    dont_send_welcome: bool

class HealthieMain:
    async def healthie_create_patient_all_in_one_endpoint(self,data1=None):
        try:
            db = DBClient()
            # data1 = patient.dict()
            print("data1", data1)
            logger.debug(data1)

            # Create Patient API
            res = healthie.create_patient_all_in_one(data1)
            print(res)
            get_user_id = res["data"]["createClient"]["user"]
            print(get_user_id['id'])
            logger.debug(res)
            user = get_user_id['id']
            print(user)
            if "id" in user:
                db.insert_healthie_patient(user_id=user["id"], email=user["email"])
                print("Inserted into data")

            data1["user_id"] = str(get_user_id['id'])

            # storing metric data API
            Store_matric_data = await storing_metric_data_all_in_one_endpoint(data1)
            data1["rel_user_id"] = str(get_user_id['id'])
            if user:
                # Upload document API
                upload_document_one = healthie.upload_document_all_in_one(data1)
                get_insurance_front_id = upload_document_one["data"]["createDocument"]["document"]["id"]
                data1["user_id"]: str(get_user_id['id'])
                data1["id"] = str(get_user_id['id'])

                # data1["policies"][0]["insurance_card_front_id"] = str(get_insurance_front_id)
                # print(data1["policies"][0])

                # Update Patient API
                update_patient = healthie.update_patient_all_in_one(data1)

            return {"status": True, "create_patient": res, "store_matric_data": Store_matric_data, "upload_document": upload_document_one, "update_patient": update_patient}
        except Exception as e:
            logger.exception(e)
            return {"status": "failed", "error": str(e)}

# @router.post('/healthie-storing-metric-data_all_in_one', tags=["healthie"])
async def storing_metric_data_all_in_one_endpoint(data):
    try:
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

        return {"status": "success", "weight_entry": weight_entry, "height_entry": height_entry, "allergies_entry": allergies_entry, "age_entry": age_entry, "gender_entry": gender_entry, "address_entry": address_entry}

    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}



main_healthie = HealthieMain()