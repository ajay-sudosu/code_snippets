import json
import logging
from fastapi import APIRouter,BackgroundTasks
from bg_task.covermymeds import CoverMedsPatientFillForm ,cover_my_meds_fill_form
from db_client import DBClient

logger = logging.getLogger("fastapi")
router = APIRouter()


@router.post('/covermeds-fill-form')
def cover_meds_fill_form_endpoint(patient: CoverMedsPatientFillForm, background_tasks: BackgroundTasks):
    """Fill form of covermymeds for new patient in the background using selenium"""
    try:
        db = DBClient()
        req = patient
        logger.debug(req)
        if db.get_visits_by_patient_id(patient.patient_id):
            patient = cover_my_meds_fill_form(req)
            background_tasks.add_task(cover_my_meds_fill_form, patient)
        else:
            return {f"status": "failure", "message": f"Patient id {patient.patient_id} not valid Please provide valid Patient id"}
        return {"status": "success", "message": "covermeds Order being created in background."}

    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}
