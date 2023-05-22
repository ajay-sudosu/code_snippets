import json
import logging
from fastapi import APIRouter,BackgroundTasks
from novocare import NovoCarePatientFillForm, novo_care_fill_form
from db_client import DBClient

logger = logging.getLogger("fastapi")
router = APIRouter()


@router.post('/novocare-fill-form')
def novo_care_fill_form_endpoint(Patient: NovoCarePatientFillForm, background_tasks: BackgroundTasks):
    """Fill form of novocare for new patient in the background using selenium"""
    try:
        logger.info("API: novocare-fill-form")
        db = DBClient()
        req = Patient
        
        logger.debug(req)
        if not Patient.first_name or not Patient.last_name or not Patient.dob or not Patient.zip_code or not Patient.sex or not Patient.RxBIN or not Patient.RxPCN or not Patient.RxGroup or not Patient.member_id or not Patient.city or not Patient.durg_quantity or not Patient.drug_days_supply or not Patient.primary_diagnosis or not Patient.find_your_medication or not Patient.doctor_name:
            if not Patient.first_name:
                return {"message": "Patient first_name is required"}
            elif not Patient.last_name:
                return {"message": "Patient last_name is required"}
            elif not Patient.dob:
                return {"message": "Patient dob is required"}
            elif not Patient.zip_code:
                return {"message": "Patient zip_code is required"}
            elif not Patient.sex:
                return {"message": "Patient Gender is missing"}
            elif not Patient.RxBIN:
                return {"message": "RxBIN number is missing "}
            elif not Patient.RxPCN:
                return {"message": "RxPCN number is missing "}
            elif not Patient.RxGroup:
                return {"message": "RxGroup number is missing "}
            elif not Patient.member_id:
                return {"message": "Patient member_id is missing"}
            elif not Patient.city:
                return {"message": "Patient city is missing"}
            elif not Patient.durg_quantity:
                return {"message": "Patient durg_quantity is missing"}
            elif not Patient.drug_days_supply:
                return {"message": "Patient drug_days_supply is missing"}
            elif not Patient.primary_diagnosis:
                return {"message": "Patient primary_dialgnosis is missing"}
            elif not Patient.find_your_medication:
                return {"message": "Patient find_your_medication is missing"}
            elif not Patient.doctor_name:
                return {"message": "Patient Doctor name is missing"}
        
        if db.get_visits_by_patient_id_for_novocare(Patient.patient_id):
            Patient = novo_care_fill_form(req)
            background_tasks.add_task(novo_care_fill_form, Patient)
        else:
            return {f"status": "failure", "message": f"Patient id {Patient.patient_id} not valid Please provide valid Patient id"}
        return {"status": "success", "message": "covermeds Order being created in background."}

    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}

