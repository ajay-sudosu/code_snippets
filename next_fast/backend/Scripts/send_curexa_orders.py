import logging
from curexa import curexa
from db_client import DBClient
import uuid
from datetime import datetime

logger = logging.getLogger("fastapi")


def send_curexa_orders():
    """
    Get unprocessed visits and send it to Curexa
    """
    try:
        client = DBClient()
        all_data = client.get_is_amazon_unprocessed_visits()
        for visit in all_data.get('data'):
            order_date = datetime.strptime(visit.get("server_date_time"), "%d/%m/%Y %H:%M:%S")
            days = abs((order_date - datetime.now()).days)
            if days < 3:
                continue
            order_id = str(uuid.uuid4())
            curexa_order = {
                "order_id": order_id,
                "patient_id": visit.get('email', ""),
                "patient_gender": visit.get('sex', ""),
                "address_to_name": visit.get('patient_name', ""),
                "address_to_street1": visit.get('patient_address', ""),
                "address_to_country": "US",
                "address_to_phone": visit.get('phone', ""),
                "carrier": "USPS",
                "otc_items": [{
                    "name": visit.get("product_name", ""),
                    "quantity": visit.get("product_quantity", 1)
                }]
            }
            response = curexa.create_order(curexa_order)
            res = curexa.order_status(order_id=order_id)
            logger.debug(res)
            if 'order_id' in res and res['order_id'] == order_id:
                email = visit.get('email')
                order_id = res.get('order_id')
                order_status = res.get('status')
                logger.info(f"Insert into curexa_orders: order_id: {order_id} for {email}")
                client.insert_curexa_order(email, order_id, order_status)
            client.update_curexa_processed(mrn=visit.get('mrn'))
    except Exception as e:
        logger.exception("send_curexa_orders => " + str(e))


if __name__ == '__main__':
    send_curexa_orders()
