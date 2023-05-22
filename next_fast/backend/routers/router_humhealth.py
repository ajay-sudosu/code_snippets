import logging
from database.db import get_db
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, status
from db_client import DBClient
from functions import field_validations_for_patient_enrollment
from database.models import RpmPatientEnrollment, RpmProgramEnrollment, OpenloopCapacity, SmartScale
from database.schemas import SmartScaleSchema
logger = logging.getLogger("fastapi")
router = APIRouter()

@router.post('/humhealth', tags=["humhealth"])
async def humhealth_enrollment(mrn, db: Session = Depends(get_db)):
    try:
        logger.info('humhealth endpoint is accessed.')
        db_client = DBClient()
        patient_obj = db_client.fetch_patient_from_visits(mrn)
        if not patient_obj:
            return {"status": "failed", "data": []}
        # patient enrollment
        patient_data = {
            "patient_name": patient_obj['patient_name'],
            "dob_date": patient_obj['dob_date'],
            "dob_month": patient_obj['dob_month'],
            "dob_year": patient_obj['dob_year'],
            "address": patient_obj['patient_address'],
            "phone": patient_obj['phone'],
            "zipcode": patient_obj['zip_code']
        }
        validation_status, data = field_validations_for_patient_enrollment(patient_data)
        if not validation_status:
            return {"status": "failed", "data": data}
        data["gender"] = "Male" if patient_obj['sex'] != 1 else "Female"
        data["record_identifier"] = "PATIENT_ENROLL"
        data["mrn"] = mrn
        data["facility_name"] = "Nextmed"
        data["physician_name"] = "John Dov"
        data["clinician_name"] = "John Dov"
        data["patient_middle_name"] = None
        data["home_phone"] = None
        data["work_phone"] = None
        data["other_phone"] = None
        patient_add = RpmPatientEnrollment(**data)
        # program enrolllment
        program_add = RpmProgramEnrollment(mrn=data["mrn"], record_identifier="RPM-PRG-ENROLL",
                                           consent_type="Written", consent_recorded_date=None, consent_signed_date=None,
                                           monthly_call_task_creation='Y',
                                           vendor_unique_transaction_id=data["vendor_unique_transaction_id"])
        db.add(patient_add)
        db.add(program_add)
        db.flush()
        db.commit()
        logger.info("rpm_patient_enrollment created successfully.")
        logger.info("rpm_program_enrollment created successfully.")

        # updating visits for is_humhealth
        logger.info("Updating visits table for is_humhealth.")
        result = db_client.update_visits_humhealth(mrn)
        logger.info("visits table updated successfully.")
        return {"status": "success", "data": data.get("mrn")}
    except Exception as e:
        logger.exception(e)
        db.rollback()
        return {"status": "failed", "error": str(e)}


@router.post('/humhealth-smart-scale', tags=["humhealth"])
async def humhealth_webhook_endpoint(data: SmartScaleSchema, db: Session = Depends(get_db)):
    try:
        logger.info("smart scale endpoint accessed.")
        data = data.dict()
        add_data = SmartScale(**data)
        db.add(add_data)
        db.flush()
        db.commit()
        logger.info("Smart scale data has been inserted successfully.")
        return {"status": "success", "data": data.get("device_number")}
    except Exception as e:
        logger.exception(e)
        db.rollback()
        return {"status": "failed", "error": str(e)}
