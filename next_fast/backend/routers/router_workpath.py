import logging
from fastapi import APIRouter, Request, status, Response, BackgroundTasks
from workpath import workpath_create_patient, workpath_create_intake

logger = logging.getLogger("fastapi")
router = APIRouter()


@router.post('/workpath-create-patient', tags=["workpath"])
async def workpath_create_patient_endpoint(request: Request):
    try:
        logger.info("API: workpath-create-patient")
        data = await request.json()
        logger.debug(data)
        return workpath_create_patient(data)
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@router.post('/workpath-create-intake', tags=["workpath"])
async def workpath_create_intake_endpoint(request: Request):
    try:
        logger.info("API: workpath-create-intake")
        data = await request.json()
        logger.debug(data)

        return workpath_create_intake(data)
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}
