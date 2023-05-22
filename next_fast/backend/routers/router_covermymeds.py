import logging
from fastapi import APIRouter, BackgroundTasks, Depends, Request
from bg_task.covermymeds import CoverMedsPatientFillForm, cover_my_meds_fill_form
from database.crud import CMMPAResultsCrud
from database.db import get_db
from sqlalchemy.orm import Session
from pydantic import BaseModel
import datetime

logger = logging.getLogger("fastapi")
router = APIRouter()


@router.post('/covermymeds-pa-request', tags=["covermymeds"])
async def covermymeds_pa_request_endpoint(patient: CoverMedsPatientFillForm, background_tasks: BackgroundTasks):
    """Fill form of covermymeds for new patient in the background using selenium"""
    try:
        logger.info("API: covermymeds-pa-request")
        logger.debug(patient.dict())
        background_tasks.add_task(cover_my_meds_fill_form, patient)
        return {"status": "success", "message": "covermymeds PA request being created in background."}

    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


class CMMInsert(BaseModel):
    mrn: str
    email: str
    name: str


@router.post('/covermymeds-insert', tags=["covermymeds"])
def covermymeds_insert(data: CMMInsert, db_session: Session = Depends(get_db)):
    """"""
    try:
        logger.info("API: covermymeds-insert")
        logger.debug(data.dict())
        ts = datetime.datetime.now()
        CMMPAResultsCrud.create_with_values(
            db_session,
            mrn=data.mrn,
            email=data.email,
            name=data.name,
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
        return {"status": "success", "data": "inserted to db"}
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}
