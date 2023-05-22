import logging
from fastapi import APIRouter, Request, status, Response, Depends, BackgroundTasks
from typing import Optional
from curexa import curexa
from db_client import DBClient
from mdintegrations import mdintegrations_api, mdi_instance_dict
from auth.jwk_model import get_current_user
from pydantic import BaseModel
from bg_task.curexa_tasks import curexa_webhook_handle
import uuid

logger = logging.getLogger("fastapi")
router = APIRouter()


class CurexaOrder(BaseModel):
    mdi_account_type: str
    case_id: str
    prescription_id: Optional[int]


class CurexaOrderAmazon(BaseModel):
    email: Optional[str]
    sex: Optional[str]
    patient_name: Optional[str]
    city_name: Optional[str]
    state: Optional[str]
    patient_address: Optional[str]
    second_address: Optional[str]
    zip_code: Optional[str]
    phone: Optional[str]
    otc_items: Optional[list]


@router.post('/create-order', tags=["curexa"])
async def curexa_create_order_endpoint(request: Request):
    try:
        logger.info("API: create-order")
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
    logger.info("API: curexa-create-order")
    logger.info("curexa_create_order_from_case_endpoint_data ==> " + str(order))
    mdi_api = mdi_instance_dict.get(order.mdi_account_type, "normal")
    logger.info(
        f"Sending order to curexa for {order.mdi_account_type} "
        f"case:{order.case_id} & prescription_id: {order.prescription_id}"
    )
    try:
        # fetch prescription
        prescriptions = mdi_api.get_prescription(order.case_id)
        prescriptions_list_to_create = []
        created_orders_list = []
        if len(prescriptions) == 0 or 'error' in prescriptions:
            logger.warning(f"No prescription found for case_id: {order.case_id}")
            raise Exception(f"No prescription found for case_id: {order.case_id}")
        else:
            if order.prescription_id:
                for presc in prescriptions:
                    if order.prescription_id == presc.get('dosespot_prescription_id'):
                        prescriptions_list_to_create.append(presc)
                if len(prescriptions_list_to_create) == 0:
                    raise Exception(
                        f"No prescription found for prescription_id: {order.prescription_id} "
                        f"against case_id: {order.case_id}"
                    )
            else:
                prescriptions_list_to_create.extend(prescriptions)

            # fetch case details
        case = mdi_api.get_case(order.case_id)
        if not case or 'error' in case:
            raise Exception(
                f"Please check if the case id: {order.case_id} "
                f"matches the correct mdi_account_type: {order.mdi_account_type}"
            )
        patient = case.get('patient')
        for prescription in prescriptions_list_to_create:
            if prescription.get('medication') is not None:
                rx_item = {
                    "rx_id": prescription.get('medication', {}).get('dosespot_medication_id'),
                    "medication_name": prescription.get('medication', {}).get('generic_product_name'),
                    "quantity_dispensed": prescription.get('quantity'),
                    "days_supply": prescription.get('days_supply'),
                    "medication_sig": prescription.get('directions'),
                    # 'medication_sig': 'Test prescription, please disregard.',
                    "non_child_resistant_acknowledgment": False
                }
            else:
                rx_item = {
                    "rx_id": prescription.get('dosespot_prescription_id'),
                    "medication_name": prescription.get('partner_compound', {}).get('title'),
                    "quantity_dispensed": prescription.get('quantity'),
                    "days_supply": prescription.get('days_supply'),
                    "medication_sig": prescription.get('directions'),
                    # 'medication_sig': 'Test prescription, please disregard.',
                    "non_child_resistant_acknowledgment": False
                }
            first_name = patient.get('first_name')
            last_name = patient.get('last_name', "")
            order_id = f"{prescription.get('dosespot_prescription_id')}"
            curexa_order = {
                "order_id": order_id,
                "patient_id": patient.get('email'),
                "patient_first_name": first_name,
                "patient_last_name": last_name,
                "patient_dob": patient.get('date_of_birth', '').replace('-', ""),
                "patient_gender": patient.get('gender_label', "male").lower(),
                "address_to_name": f"{first_name} {last_name}",
                "address_to_city": patient.get('address', {}).get('city_name'),
                "address_to_state": patient.get('address', {}).get('state', {}).get('abbreviation'),
                "address_to_street1": patient.get('address', {}).get('address'),
                "address_to_street2": patient.get('address', {}).get('address2'),
                "address_to_zip": patient.get('address', {}).get('zip_code'),
                "address_to_country": "US",
                "address_to_phone": patient.get('phone_number', "").replace('-', ''),
                "patient_known_allergies": patient.get('allergies'),
                "patient_other_medications": patient.get('current_medications'),
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
            if 'order_id' in res and res.get('order_id') == order_id:
                logger.warning(f"Sent order to curexa for {order.case_id} Successfully.")
                db = DBClient()
                order_id = res.get('order_id')
                email = patient.get('email')
                order_status = res.get('status')
                logger.info(f"Insert into curexa_orders: order_id: {order_id} for {email}")
                db.insert_curexa_order(email, order_id, order_status)
                created_orders_list.append(res)
            else:
                logger.warning(f"Sending order to curexa for {order.case_id} Failed.")
                raise Exception(res)
        return created_orders_list
    except Exception as e:
        logger.exception("curexa_create_order_from_case_endpoint ==> " + str(e))
        return {"status": "failed", "error": str(e)}


@router.get('/curexa-order-status', tags=["curexa"])
async def curexa_order_status_endpoint(
        email: Optional[str] = None,
        order_id: Optional[str] = None
):
    """Fetch order status from db"""
    try:
        logger.info("API: curexa-order-status")
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
        logger.info("API: curexa-webhook")
        logger.debug(request.headers)
        data = await request.json()
        logger.debug(data)

        background_tasks.add_task(curexa_webhook_handle, data)

        return {"success": "Being handled in background"}

    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@router.post('/curexa-create-order-amazon', tags=["curexa"])
async def curexa_create_order_for_amazon_patient(order: CurexaOrderAmazon):
    """
    Create Curexa Order.
    """
    try:
        logger.info("API: curexa-create-order-amazon")
        order_id = str(uuid.uuid4())
        curexa_order = {
            "order_id": order_id,
            "patient_id": order.email,
            "patient_gender": order.sex,
            "address_to_name": order.patient_name,
            "address_to_city": order.city_name,
            "address_to_state": order.state,
            "address_to_street1": order.patient_address,
            "address_to_street2": order.second_address,
            "address_to_zip": order.zip_code,
            "address_to_country": "US",
            "address_to_phone": order.phone,
            "carrier": "USPS",
            "otc_items": order.otc_items
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
            logger.warning(f"Sent order to curexa for {order.email} Successfully.")
            db = DBClient()
            order_id = res.get('order_id')
            email = order.email
            order_status = res.get('status')
            logger.info(f"Insert into curexa_orders: order_id: {order_id} for {email}")
            db.insert_curexa_order(email, order_id, order_status)
            return res
        else:
            logger.warning(f"Sending order to curexa for {order_id} Failed.")
            raise Exception(res)
    except Exception as e:
        logger.exception(f"curexa_create_order_for_amazon_patient ==> {str(e)}")
        return {"status": "failed", "error": str(e)}
