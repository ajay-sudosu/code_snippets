import json
import logging
from fastapi import APIRouter, Request, status, Response, BackgroundTasks
from typing import Optional
from bg_tasks import DrChronoNewLabOrder, drchrono_send_new_lab_order, \
    frontend_test_names_to_code_labcorp, frontend_test_names_to_code_quest, \
    frontend_test_names_to_health_gorilla
from drchrono import drchrono, DrChronoInsuranceQuery, DrChronoLabOrder
from db_client import DBClient

logger = logging.getLogger("fastapi")
router = APIRouter()


@router.post('/drchono-create-appointment', tags=["drchrono"])
async def drchrono_create_appointment_endpoint(request: Request):
    try:
        data = await request.json()
        logger.debug(data)
        res = drchrono.appointment_create(data)
        logger.debug(res)
        if 'id' in res:
            return res
        raise Exception(res)

    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@router.get('/drchrono-doctors-list', tags=["drchrono"])
async def drchrono_doctors_list_endpoint(
        cursor: Optional[str] = None,
        doctor: Optional[int] = None,
        page_size: Optional[int] = None,
):
    try:
        params = {
            "cursor": cursor,
            "doctor": doctor,
            "page_size": page_size,
        }
        res = drchrono.doctor_list(params=params)
        logger.debug(res)
        if 'results' in res:
            return res
        raise Exception(res)
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@router.post('/drchrono-insurances-list', tags=["drchrono"])
async def drchrono_insurances_list_endpoint(query: DrChronoInsuranceQuery):
    """Get a list of drchrono insurances"""
    try:
        req = query.dict()
        logger.debug(req)
        res = drchrono.insurances_list(req)
        if 'results' in res:
            return res
        raise Exception(res)
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@router.get('/drchrono-lab-documents-list', tags=["drchrono"])
async def drchrono_lab_documents_list_endpoint():
    try:
        res = drchrono.lab_documents_list()
        logger.debug(res)
        if 'results' in res:
            return res
        raise Exception(res)
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@router.get("/drchrono-lab-documents-read/{lab_document_id}", tags=["drchrono"])
async def drchrono_lab_documents_read_endpoint(lab_document_id: int):
    try:
        res = drchrono.lab_documents_read(lab_document_id)
        logger.debug(res)
        if 'id' in res:
            return res
        raise Exception(res)
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@router.get('/drchrono-lab-orders-list', tags=["drchrono"])
async def drchrono_lab_orders_list_endpoint():
    try:
        res = drchrono.lab_orders_list()
        logger.debug(res)
        if 'results' in res:
            return res
        raise Exception(res)
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@router.post('/drchrono-lab-orders-create', tags=["drchrono"])
async def drchrono_lab_orders_create_endpoint(laborder: DrChronoLabOrder):
    try:
        res = drchrono.lab_orders_create(laborder.dict())
        logger.debug(res)
        if 'id' in res:
            return res
        raise Exception(res)
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


'''
@app.delete("/drchrono/lab-orders-delete/{lab_order_id}")
async def drchrono_lab_orders_delete_endpoint(lab_order_id: int):
    try:
        res = drchrono.lab_orders_delete(lab_order_id)
        logger.debug(res)
        return res
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@app.post("/drchrono/lab-orders-update/{lab_order_id}")
async def drchrono_lab_orders_update_endpoint(lab_order_id: int):
    try:
        res = drchrono.lab_orders_update(lab_order_id)
        logger.debug(res)
        if 'id' in res:
            return res
        raise Exception(res)
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}
'''


@router.get("/drchrono-lab-orders-read/{lab_order_id}", tags=["drchrono"])
async def drchrono_lab_orders_read_endpoint(lab_order_id: int):
    try:
        res = drchrono.lab_orders_read(lab_order_id)
        logger.debug(res)
        if 'id' in res:
            return res
        raise Exception(res)
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@router.post("/drchrono-lab-orders-results", tags=["drchrono"])
async def drchrono_lab_orders_results_endpoint(request: Request):
    try:
        data = await request.json()
        logger.debug(data)
        patient_id = data["patient_id"]
        client = DBClient()
        response = client.get_lab_order_results(patient_id=patient_id)
        client.connection.close()
        for d in response["data"]:
            d['drchrono_results'] = json.loads(d['drchrono_results'])
        return response
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@router.post('/drchono-create-patient', tags=["drchrono"])
async def drchrono_create_patient_endpoint(request: Request):
    try:
        data = await request.json()
        logger.debug(data)
        res = drchrono.patient_create(data)
        if 'id' in res:
            return res
        raise Exception(res)

    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@router.post('/drchrono-partial-update-patient', tags=["drchrono"])
async def drchrono_partial_update_patient_endpoint(request: Request):
    try:
        data = await request.json()
        logger.debug(data)
        if data:
            res = drchrono.patient_partial_update(data)
            logger.debug(res)
            return res
        else:
            return {"status": "failed", "error": "Provide some data to update"}
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@router.get('/drchrono-patients-list', tags=["drchrono"])
async def drchrono_patients_list_endpoint(
        chart_id: Optional[str] = None,
        cursor: Optional[str] = None,
        date_of_birth: Optional[str] = None,
        doctor: Optional[int] = None,
        email: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        page_size: Optional[int] = None,
):
    try:
        params = {
            "chart_id": chart_id,
            "cursor": cursor,
            "date_of_birth": date_of_birth,
            "doctor": doctor,
            "email": email,
            "first_name": first_name,
            "last_name": last_name,
            "page_size": page_size,
        }
        res = drchrono.patients_list(params=params)
        logger.debug(res)
        if 'results' in res:
            return res
        raise Exception(res)
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@router.post('/drchrono-send-lab-order', tags=["drchrono"])
async def drchrono_send_lab_order_endpoint(laborder: DrChronoNewLabOrder, background_tasks: BackgroundTasks):
    """Create lab order for new patient in the background using selenium"""
    try:
        req = laborder.dict()
        logger.debug(req)
        order_type = req.get('order_type')
        if order_type.lower() not in ["labcorp", "quest", "bioreference"]:
            return {"status": "failed", "error": f"invalid order_type: {order_type}"}

        # check patient_id
        patient_id = req.get('patient_id')
        res = drchrono.patients_read(patient_id)
        logger.debug(res)
        if 'id' not in res:
            return {"status": "failed", "error": f"invalid patient: {patient_id}"}

        test_codes = []
        if order_type.lower() == "bioreference":
            target_code = frontend_test_names_to_health_gorilla.keys()
            for favorite in req.get('test_names', []):
                favorite = favorite.strip()
                if favorite not in target_code:
                    logger.error(f"invalid testname: {favorite}")
                    return {"status": "failed", "error": f"invalid test: {favorite}"}
                code = frontend_test_names_to_health_gorilla[favorite]
                test_codes.append(code)
            laborder.test_names = test_codes
        elif order_type.lower() == "labcorp":
            target_code = frontend_test_names_to_code_labcorp.keys()
            for favorite in req.get('test_names', []):
                favorite = favorite.strip()
                if favorite not in target_code:
                    logger.error(f"invalid testname: {favorite}")
                    return {"status": "failed", "error": f"invalid test: {favorite}"}
                code = frontend_test_names_to_code_labcorp[favorite]
                test_codes.append(code)
            laborder.test_names = test_codes
        else:
            target_code = frontend_test_names_to_code_quest.keys()
            for favorite in req.get('test_names', []):
                favorite = favorite.strip()
                if favorite.startswith("STD"):
                    favorite = f"{favorite} {req.get('patient_gender')}"
                if favorite not in target_code:
                    logger.error(f"invalid testname: {favorite}")
                    return {"status": "failed", "error": f"invalid test: {favorite}"}
                code = frontend_test_names_to_code_quest[favorite]
                test_codes.append(code)
            laborder.test_names = test_codes

        background_tasks.add_task(drchrono_send_new_lab_order, laborder)
        return {"status": "success", "message": "Lab Order being created in background."}
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@router.get('/drchrono-sublabs-list', tags=["drchrono"])
async def drchrono_patients_list_endpoint(
        cursor: Optional[str] = None,
        page_size: Optional[int] = None,
):
    try:
        params = {
            "cursor": cursor,
            "page_size": page_size,
        }
        res = drchrono.sublabs_list(params=params)
        logger.debug(res)
        if 'results' in res:
            return res
        raise Exception(res)
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@router.get('/drchrono-tasks-list', tags=["drchrono"])
async def drchrono_tasks_list_endpoint(cursor: Optional[str] = None):
    try:
        param = {
            "cursor": cursor
        }
        res = drchrono.tasks_list(params=param)
        logger.debug(res)
        if 'results' in res:
            return res
        raise Exception(res)
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@router.post('/drchrono-tasks-create', tags=["drchrono"])
async def drchrono_tasks_create_endpoint(request: Request):
    try:
        data = await request.json()
        logger.debug(data)
        res = drchrono.tasks_create(body=data)
        logger.debug(res)
        if 'id' in res:
            return res
        raise Exception(res)
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@router.post('/drchrono-tasks-update/{task_id}', tags=["drchrono"])
async def drchrono_tasks_update_endpoint(task_id, request: Request):
    try:
        data = request.json()
        logger.debug(data)
        res = drchrono.tasks_update(task_id, body=data)
        logger.debug(res)
        return res
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@router.get('/drchrono-tasks-read/{task_id}', tags=["drchrono"])
async def drchrono_tasks_read_endpoint(task_id):
    try:
        res = drchrono.tasks_read(task_id)
        logger.debug(res)
        if 'id' in res:
            return res
        raise Exception(res)
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@router.get('/drchrono-users-list', tags=["drchrono"])
async def drchrono_users_list_endpoint(cursor: Optional[str] = None):
    """Get a list of drchrono users"""
    try:
        param = {
            "cursor": cursor
        }
        res = drchrono.users_list(params=param)
        logger.debug(res)
        if 'results' in res:
            return res
        raise Exception(res)
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}
