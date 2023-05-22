import logging
from xmlrpc.client import Boolean
from spreadsheet import spreadsheet
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from typing import Optional
from db_client import DBClient
from fastapi import Request
import json
from fastapi.encoders import jsonable_encoder
from json import JSONEncoder
import requests
import base64
from datetime import datetime
from functions import *
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi import Depends
from auth.simple_auth.simple_jwt_auth import JWTBearer


security = HTTPBasic()
logger = logging.getLogger("fastapi")
router = APIRouter()


class SpreadsheetPatient(BaseModel):
    date_requested: str = Form(...)
    is_patient_policy_holder: str = Form(...)
    first_name: str = Form(...)
    last_name: str = Form(...)
    insurance_carrier: str = Form(...)
    insurance_member_id: str = Form(...)
    insurance_group_member: str = Form(...)
    dob: str = Form(...)
    email: str = Form(...)
    policy_holder_first_name: str = Form(...)
    policy_holder_last_name: str = Form(...)
    policy_holder_dob: str = Form(...)
    is_patient_eligible: str = Form(...)
    copay_amount: str = Form(...)
    coinsurance_percentage: str = Form(...)
    # wrap_request_in_array: str = Form(...)
    # file: UploadFile = File(...)
    # unflatten: str = Form(...)
    # signed_off_by: str
    # date: str
    # has_patient_notified: str


# @router.post('/spreadsheet-write-patient', tags=["spreadsheet"])
# async def spreadsheet_write_patient_endpoint(date_requested: str = Form(...),is_patient_policy_holder: str = Form(...),first_name:  str = Form(...),last_name: str = Form(...),insurance_carrier: str = Form(...),insurance_member_id: str = Form(...),insurance_group_member: str = Form(...),dob: str = Form(...),email: str = Form(...),policy_holder_first_name: str = Form(...),policy_holder_last_name: str = Form(...),policy_holder_dob: str = Form(...),is_patient_eligible: str = Form(...),copay_amount: str = Form(...),coinsurance_percentage: str = Form(...),wrap_request_in_array: str = Form(...),unflatten: str = Form(...),file: UploadFile = File(...),credentials: HTTPBasicCredentials = Depends(security)):
#     try:
#         file = jsonable_encoder(file)
#         print("file", file)
#         db = DBClient()
#         data = {"date_requested": date_requested, "is_patient_policy_holder": is_patient_policy_holder, "first_name": first_name, "last_name": last_name, "insurance_carrier": insurance_carrier, "insurance_member_id": insurance_member_id, "insurance_group_member": insurance_group_member, "dob": dob, "email": email, "policy_holder_first_name": policy_holder_first_name, "policy_holder_last_name": policy_holder_last_name, "policy_holder_dob": policy_holder_dob, "is_patient_eligible": is_patient_eligible, "copay_amount": copay_amount, "coinsurance_percentage": coinsurance_percentage, "wrap_request_in_array": wrap_request_in_array, "unflatten": unflatten, "file": str(file)}
#         logger.debug(data)
#         print("data", data)
#         res = spreadsheet.write_spreadsheet_data(data)
#         logger.debug(res)
#         print("res", data["is_patient_eligible"], data["copay_amount"])
#         if not email:
#             return {"error": "please provide an email"}
#         db.insert_spreadsheet_data(is_patient_eligible=data["is_patient_eligible"], copay_amount=data["copay_amount"], coinsurance_percentage=data["coinsurance_percentage"])
#         print("Inserted into data")
#         return {"status": True}
#     except Exception as e:
#         logger.exception(e)
#         return {"status": "failed", "error": str(e)}


@router.post('/spreadsheet-write-patient',dependencies=[Depends(JWTBearer())], tags=["spreadsheet"])
async def spreadsheet_write_patient_endpoint(spreadsheet_data: SpreadsheetPatient):
    try:
        logger.info("API: spreadsheet-write-patient")
        db = DBClient()
        data = spreadsheet_data.dict()
        logger.debug(data)
        print("data", data)
        res = spreadsheet.write_spreadsheet_data(data)
        logger.debug(res)
        print("res", data["is_patient_eligible"], data["copay_amount"])
        # user = res["data"]["createClient"]["user"]
        # print("user", user)
        # if "id" in user:
        db.insert_spreadsheet_data(is_patient_eligible=data["is_patient_eligible"], copay_amount=data["copay_amount"], coinsurance_percentage=data["coinsurance_percentage"])
        print("Inserted into data")
        return {"status": True}
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@router.post('/add-intake-eligibility')
async def add_intake_eligibility_endpoint(request: Request):
    try:
        logger.info("API: add-intake-eligibility")
        data = await request.json()
        logger.debug("add_intake_eligibility_endpoint ==>" + str(data))
        client = DBClient()
        res = client.intake_add_eligibility(
            datetime.strptime(data["date_requested"], "%d/%m/%Y %H:%M:%S"),
            data["is_patient_policy_holder"],
            data["first_name"],
            data["last_name"],
            data["insurance_carrier"],
            data["insurance_member_id"],
            data["insurance_group_member"],
            datetime.strptime(data["dob"], "%d/%m/%Y"),
            data["email"],
            data["policy_holder_first_name"],
            data["policy_holder_last_name"],
            datetime.strptime(data["policy_holder_dob"], "%d/%m/%Y"),
            data["is_patient_eligible"],
            data["copay_amount"],
            data["coinsurance_percentage"]
        )
        return res
    except Exception as e:
        return {"status": "failed", "error": str(e)}
