from db_client import DBClient
from api.klaviyo_api import curexa_klaviyo_track_profile
import logging

logger = logging.getLogger("fastapi")


def curexa_webhook_handle(data):
    """Handle different curexa events"""

    if 'order_id' in data:
        try:
            db = DBClient()
            order_id = data.get('order_id')
            logger.info(f"Update curexa_orders status for order_id: {order_id}")
            db.update_curexa_order(**data)
            orders = db.get_curexa_order(order_id=order_id)
            for order in orders.get("data", []):
                email = order.get("email")
                if email is not None:
                    profile = db.get_patient_profile(email)
                    curexa_klaviyo_track_profile(
                        email=email,
                        patient_name=profile.get("patient_name"),
                        **data
                    )
                    break
        except Exception as e:
            logger.exception(e)
    else:
        logger.warning("order_id is None")
