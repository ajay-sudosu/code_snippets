import logging
from fastapi import APIRouter, Request, status, Response, Depends, BackgroundTasks
from typing import Optional
from curexa import curexa
from db_client import DBClient
from mdintegrations import mdintegrations_api
from auth.jwk_model import get_current_user
from pydantic import BaseModel
from bg_task.curexa_tasks import curexa_webhook_handle

logger = logging.getLogger("fastapi")
router = APIRouter()


class CurexaOrder(BaseModel):
    case_id: str
    prescription_id: Optional[int]


@router.post('/create-order', tags=["curexa"])
async def curexa_create_order_endpoint(request: Request):
    try:
        data = await request.json()
        logger.debug(data)
        res = curexa.create_order(data)
        logger.debug(res)
        res = curexa.order_status(order_id=data['order_id'])
        logger.debug(res)
        if 'order_id' in res and res['order_id'] is not None:
            db = DBClient()
            order_id = res.get('order_id')
            email = data.get('patient_id')
            order_status = res.get('status')
            logger.info(f"Insert into curexa_orders: order_id: {order_id} for {email}")
            db.insert_curexa_order(email, order_id, order_status)
            return res
        raise Exception(res)

    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@router.post('/curexa-create-order', tags=["curexa"])
async def curexa_create_order_from_case_endpoint(order: CurexaOrder):
    """create curexa order from mdi case."""
    logger.info(f"Sending order to curexa for {order.case_id} & prescription_id: {order.prescription_id}")
    try:
        # fetch prescription
        prescriptions = mdintegrations_api.get_prescription(order.case_id)
        if len(prescriptions) == 0:
            logger.warning(f"No prescription found for case_id: {order.case_id}")
            raise Exception(f"No prescription found for case_id: {order.case_id}")
        if order.prescription_id is None:
            prescription = prescriptions[0]
        else:
            for presc in prescriptions:
                if order.prescription_id == presc['dosespot_prescription_id']:
                    prescription = presc
                    break
            else:
                prescription = prescriptions[0]

            # fetch case details
        case = mdintegrations_api.get_case(order.case_id)
        patient = case.get('patient')

        if prescription['medication'] is not None:
            rx_item = {
                "rx_id": prescription['medication']['dosespot_medication_id'],
                "medication_name": prescription['medication']['generic_product_name'],
                "quantity_dispensed": prescription['quantity'],
                "days_supply": prescription['days_supply'],
                "medication_sig": prescription['directions'],
                # 'medication_sig': 'Test prescription, please disregard.',
                "non_child_resistant_acknowledgment": False
            }
        else:
            rx_item = {
                "rx_id": prescription['dosespot_prescription_id'],
                "medication_name": prescription['partner_compound']['title'],
                "quantity_dispensed": prescription['quantity'],
                "days_supply": prescription['days_supply'],
                "medication_sig": prescription['directions'],
                # 'medication_sig': 'Test prescription, please disregard.',
                "non_child_resistant_acknowledgment": False
            }
        first_name = patient['first_name']
        last_name = patient.get('last_name', "")
        order_id = f"{prescription['dosespot_prescription_id']}"
        curexa_order = {
            "order_id": order_id,
            "patient_id": patient['email'],
            "patient_first_name": first_name,
            "patient_last_name": last_name,
            "patient_dob": patient['date_of_birth'].replace('-', ""),
            "patient_gender": patient.get('gender_label', "male").lower(),
            "address_to_name": f"{first_name} {last_name}",
            "address_to_city": patient['address']['city_name'],
            "address_to_state": patient['address']['state']['abbreviation'],
            "address_to_street1": patient['address']['address'],
            "address_to_street2": patient['address']['address2'],
            "address_to_zip": patient['address']['zip_code'],
            "address_to_country": "US",
            "address_to_phone": patient['phone_number'].replace('-', ''),
            "patient_known_allergies": patient['allergies'],
            "patient_other_medications": patient['current_medications'],
            "carrier": "USPS",
            "rx_items": [
                rx_item
            ]
        }
        for k, v in curexa_order.items():
            if v is None or v == 'None':
                curexa_order[k] = ""
        logger.info(curexa_order)
        res = curexa.create_order(curexa_order)
        logger.debug(res)
        res = curexa.order_status(order_id=order_id)
        logger.debug(res)
        if 'order_id' in res and res['order_id'] == order_id:
            logger.warning(f"Sent order to curexa for {order.case_id} Successfully.")
            db = DBClient()
            order_id = res.get('order_id')
            email = patient.get('email')
            order_status = res.get('status')
            logger.info(f"Insert into curexa_orders: order_id: {order_id} for {email}")
            db.insert_curexa_order(email, order_id, order_status)
            return res
        else:
            logger.warning(f"Sending order to curexa for {order.case_id} Failed.")
            raise Exception(res)
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@router.get('/curexa-order-status', tags=["curexa"])
async def curexa_order_status_endpoint(
        email: str,
        order_id: Optional[str] = None
):
    """Fetch order status from db"""
    try:
        logger.info(f"fetch order_status for email: {email} & order_id: {order_id}")
        db = DBClient()
        res = db.get_curexa_order(order_id=order_id, email=email)
        return res

    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@router.post('/curexa-webhook', tags=["curexa"])
async def curexa_webhook_endpoint(request: Request, background_tasks: BackgroundTasks):
    try:
        logger.debug(request.headers)
        data = await request.json()
        logger.debug(data)

        background_tasks.add_task(curexa_webhook_handle, data)

        return {"success": "Being handled in background"}

    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}
