import logging
from models.failed_subscriptions import FailedSubscriptions
from sqlalchemy_db import get_db
from utils import send_text_email, send_text_message
from db_client import DBClient

logger = logging.getLogger("fastapi")


def notify_failed_payment_customers():
    try:
        db = next(get_db())
        failed_subscriptions = db.query(FailedSubscriptions).filter(FailedSubscriptions.is_processed == 0).all()
        if not failed_subscriptions:
            return
        client = DBClient()
        for failed_subscription in failed_subscriptions:
            data = failed_subscription.__dict__
            patient_email = data.get("patient_email")
            first_name = data.get('patient_name')
            mrn = None
            if not patient_email:
                continue
            all_data = client.get_patient_visits(patient_email)
            for visit in all_data.get('data'):
                if visit.get('phone') == data.get('patient_phone'):
                    mrn = visit.get('mrn')
                    break
            sender = 'team@joinnextmed.com'
            subject = 'NextMed: Payment Failed Alert'
            content = f"""
            Hi {first_name}, Your credit card has been declined for your NextMed Program! 
            Please update your payment method ASAP at this url: www.joinnextmed.com/update-payment?id={mrn} 
            You will not receive additional medication or refills without filling out your card! 
            Make sure to update it soon!
            """
            try:
                send_text_email(sender, patient_email, subject, content)
            except Exception as e:
                logger.exception(f"sending_text_email_alert failed for {patient_email} => {str(e)}")
            try:
                send_text_message(data.get('patient_phone'), content)
                failed_subscription.is_processed = 1
            except Exception as e:
                logger.exception(f"sending_text_messages_alert failed for {patient_email} => {str(e)}")
            logger.info(f"sending alerts completed for {patient_email}")
        db.commit()
    except Exception as e:
        logger.exception("notify_failed_payment_customers => " + str(e))


if __name__ == '__main__':
    notify_failed_payment_customers()
