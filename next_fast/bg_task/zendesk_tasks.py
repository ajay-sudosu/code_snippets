import logging
from sqlalchemy.orm import Session
from utils import send_text_message, send_text_email
from database.crud import OpenloopCapacityRepo, ZendeskNotifyCrud, VisitsCrud
from database.schemas import ZendeskNotifyBase
from database.db import get_db
from healthie import healthie
from mdintegrations import mdintegrations_chat
import datetime

logger = logging.getLogger("fastapi")
db: Session = next(get_db())


class ZendeskWebhookHandler:
    """class to handle Zendesk webhook payload"""
    def __init__(self, payload):
        self.payload = payload
        self.event_type = None
        self.email = None
        self.user = {}

    @staticmethod
    def send_notifications(email: str, to_phone: str, message: str):
        """
        send text & email notifications
        name: receiver's name
        email: receiver's email
        to_phone: receiver's phone
        message_type: 'intake' or 'checkin'
        """
        subject = 'Your Action Needed'
        try:
            logging.debug(f"Sending text to {to_phone}")
            send_text_message(to_phone, message)
        except Exception as e:
            logging.exception(e)

        SENDER = 'team@joinnextmed.com'
        logging.debug(f"Sending email to {email}")
        send_text_email(sender=SENDER, recipient=email, subject=subject, content=message)

    def zendesk_handle_yes_eligible(self):
        """Handle eligible == yes_eligible"""
        # "schedule_first_visit" to 1
        self.zendesk_update_db_schedule_first_visit()

        # notify user
        self.zendesk_get_healthie_patient()
        message = f"Hi {self.user.get('first_name')}, good news! It's time to schedule your first NextMed visit! " \
                  f"Please login to your NextMed portal here to book your visit and get started: " \
                  f"www.joinnextmed.com/login. We can't wait to meet you!"

        # notify user
        self.send_notifications(email=self.user.get('email'),
                                to_phone=self.user.get('phone_number'),
                                message=message)
        # Set cron tasks for reminder
        self.zendesk_set_cron_tasks('schedule_visit')

    def zendesk_handle_red_capacity(self):
        """Handle eligible == no_eligible OR capacity == red"""
        try:
            email = self.payload.get('email')
            # set is_healthie = 0
            VisitsCrud.update_visits_is_healthie_by_email(db, email, '0')
            # fetch patient details
            self.zendesk_get_healthie_patient()
            if 'female' == self.payload.get('gender'):
                gender = 1
            else:
                gender = 0
            # Create MDI account
            patient_payload = {
                "first_name": self.payload.get('first_name'),
                "last_name": self.payload.get('last_name'),
                "email": email,
                "gender": gender,
                "phone_number": self.user.get('phone_number'),
                "date_of_birth": self.payload.get('dob')
            }
            mdi_patient = mdintegrations_chat.create_patient(patient_payload)
            logging.debug(mdi_patient)
            # update visits for patient_id_md
            if 'patient_id' in mdi_patient:
                VisitsCrud.update_visits_patient_id_md_by_email(db, email, mdi_patient['patient_id'])
        except Exception as e:
            logging.exception(e)

    def zendesk_get_healthie_patient(self):
        try:
            patient_id = self.payload.get('patientId')
            # call healthie api to get patient details
            response = healthie.get_patient(patient_id)
            self.user = response.get('data', {}).get('user', {})
        except Exception as e:
            logger.exception(e)

    def zendesk_update_db_state_capacity(self):
        """Update state capacity"""
        try:
            state = self.payload.get('state')
            capacity = self.payload.get('capacity')

            # update state capacity to db
            logger.info(f"Updating OpenloopCapacity: {capacity} to {state}")
            if 'green' == capacity:
                capacity_val = 1
            else:
                capacity_val = 0
            OpenloopCapacityRepo.update_state_capacity(db, state, capacity_val)
        except Exception as e:
            logger.exception(e)

    def zendesk_update_db_elig_info(self):
        """Update copay_amount, coinsurance_amount, eligibility_check & insurance_elig_checked"""
        try:
            copay_amount = self.payload.get('copay')
            coinsurance_amount = self.payload.get('coinsurance')
            eligibility_check = self.payload.get('eligible')
            insurance_elig_checked = 1
            self.email = self.payload.get('email')

            # update above info to db
            logger.info(f"Updating Visits: insurance_elig_checked to 1 for {self.email}")
            VisitsCrud.update_visits_eligibility_check_by_email(
                db_session=db,
                email=self.email,
                copay_amount=int(copay_amount),
                coinsurance_amount=int(coinsurance_amount),
                eligibility_check=eligibility_check,
                insurance_elig_checked=insurance_elig_checked
            )
        except Exception as e:
            logger.exception(e)

    def zendesk_handle_eligibility_check(self):
        """Handle TYPE == elig_check"""
        eligible = self.payload.get('eligible')

        # update visits row
        self.zendesk_update_db_elig_info()
        # update openloop capacity
        self.zendesk_update_db_state_capacity()

        capacity = self.payload.get('capacity')
        # over capacity
        if 'red' == capacity:
            self.zendesk_handle_red_capacity()
        # under capacity
        else:
            if 'yes_eligible' == eligible:
                self.zendesk_handle_yes_eligible()
            elif 'no_eligible' == eligible:
                self.zendesk_handle_red_capacity()
            else:
                logger.warning(f"Unknown eligible: {eligible}")

    def zendesk_set_cron_task(self, event, ts_now, hour, last_notify=False):
        """Create new cron to db"""
        try:
            td = datetime.timedelta(hours=hour)
            ts_future = ts_now + td
            cron = ZendeskNotifyBase(
                scheduled_ts=ts_future.strftime("%Y/%m/%d %H:%M:%S"),
                email=self.user.get('email'),
                patient_id=self.payload.get('patientId'),
                patient_name=self.user.get('first_name'),
                phone=self.user.get('phone_number'),
                event=event,
                last_notify=last_notify)
            ZendeskNotifyCrud.create(db, cron)
        except Exception as e:
            logger.exception(e)

    def zendesk_set_cron_tasks(self, event):
        """Add cron task for 4, 12, 48, 72 & 96 hours"""
        ts_now = datetime.datetime.now()
        for hour in [4, 12, 24, 48, 72]:
            self.zendesk_set_cron_task(event, ts_now, hour)

        self.zendesk_set_cron_task(event, ts_now, 96, last_notify=True)

    def zendesk_update_db_schedule_first_visit(self, value=1):
        """update "schedule_first_visit" to 1"""
        try:
            VisitsCrud.update_visits_schedule_first_visit_by_email(db, self.email, value)
        except Exception as e:
            logger.exception(e)

    def zendesk_update_db_visit_no_showed(self, value="1"):
        """update "visit_no_showed " to 1"""
        try:
            VisitsCrud.update_visits_visit_no_showed_by_email(db, self.email, value)
        except Exception as e:
            logger.exception(e)

    def zendesk_handle_visit_status(self):
        """Handle TYPE == visit_status"""
        visit_status = self.payload.get('visitStatus')

        if 'visit_completed' == visit_status:
            # TODO : schedule next visit after 30 days
            pass
        elif 'visit_cancelled' == visit_status:
            # set "schedule_first_visit" to 1
            self.zendesk_update_db_schedule_first_visit()

            self.zendesk_get_healthie_patient()
            message = f"Hi {self.user.get('first_name')}, Your NextMed visit was cancelled. " \
                      f"You need to reschedule the visit as soon as possible from your NextMed portal. " \
                      f"Get started here: www.joinnextmed.com/login. Thanks!"

            # notify user
            self.send_notifications(email=self.user.get('email'),
                                    to_phone=self.user.get('phone_number'),
                                    message=message)
            # Set cron tasks for reminder
            self.zendesk_set_cron_tasks(visit_status)

        elif 'visit_noshow' == visit_status:
            # set visit_no_showed to 1
            self.zendesk_update_db_visit_no_showed()
            # set "schedule_first_visit" to 1
            self.zendesk_update_db_schedule_first_visit()
            # notify user
            self.zendesk_get_healthie_patient()
            message = f"Hi {self.user.get('first_name')}, Your NextMed visit was cancelled. " \
                      f"You need to reschedule the visit as soon as possible from your NextMed portal. " \
                      f"Get started here: www.joinnextmed.com/login. If you do not reschedule your visit, " \
                      f"you will be charged a $99 visit no-show fee. We are trying to help you reschedule. " \
                      f"If you have any questions please contact team@joinnextmed.com. Thanks!"
            self.send_notifications(email=self.user.get('email'),
                                    to_phone=self.user.get('phone_number'),
                                    message=message)
            # Set cron tasks for reminder
            self.zendesk_set_cron_tasks(visit_status)
        else:
            logger.warning(f"Unknown visitStatus: {visit_status}")

    def zendesk_get_healthie_all_prescriptions(self):
        try:
            patient_id = self.payload.get('patientId')
            # call healthie api to get patient details
            response = healthie.get_all_prescriptions(patient_id)
            data = response.get('data', {}).get('prescriptions', [])
            logger.debug(data)
            return data
        except Exception as e:
            logger.exception(e)
            return []

    @staticmethod
    def match_weight_medicine_type(product_name: str):
        """return weight_medicine_type type or None"""
        weight_medicine_type_list = ['ozempic', 'wegovy', 'mounjaro', 'rybelsus', 'saxenda', 'trulicity', 'victoza',
                                     'metformin']
        semaglutide_in_product_name = {
            '0.25': 'ozempic',
            '0.5': 'wegovy',
            '0.6': 'saxenda',
            '1.2': 'victoza',
            '3': 'rybelsus',
        }
        product_name = product_name.lower()

        if 'bupropion' in product_name or 'natrexone' in product_name:
            return 'contrave'

        for med in weight_medicine_type_list:
            if med in product_name:
                return med

        if 'semaglutide' in product_name:
            for key, val in semaglutide_in_product_name.items():
                if key in product_name:
                    return val
        return None

    def zendesk_handle_prescription_written(self):
        """Handle TYPE == erx"""
        self.zendesk_get_healthie_patient()
        prescriptions = self.zendesk_get_healthie_all_prescriptions()

        message = f"Hi {self.user.get('first_name')}, a new prescription has been ordered to your pharmacy. " \
                  f"Please call your chosen pharmacy to see when it will be ready before going to pick it up. " \
                  f"This process could take a few hours. Thanks!"

        # notify user
        self.send_notifications(email=self.user.get('email'),
                                to_phone=self.user.get('phone_number'),
                                message=message)
        if not prescriptions:
            logger.warning(f"No prescriptions found for {self.user.get('email')}, {self.payload.get('patientId')}")
            return

        for erx in prescriptions.reverse():
            product_name = erx.get('product_name', '')
            weight_medicine_type = self.match_weight_medicine_type(product_name)
            if weight_medicine_type:
                VisitsCrud.update_visits_weight_medicine_type_by_healthie_id(
                    db,
                    self.payload.get('patientId'),
                    weight_medicine_type
                )
                break

    def zendesk_workflow(self):
        try:
            self.event_type = self.payload.get('type')

            if 'elig_check' == self.event_type:
                self.zendesk_handle_eligibility_check()
            elif 'visit_status' == self.event_type:
                self.zendesk_handle_visit_status()
            elif 'erx' == self.event_type:
                self.zendesk_handle_prescription_written()
            else:
                logger.warning(f"Unknown Type: {self.event_type}")

        except Exception as e:
            logger.exception("ZendeskWebhookHandler.workflow => " + str(e))


def zendesk_webhook_handle(data):
    """Handle different zendesk webhook events"""
    try:
        logger.debug(data)
        handler = ZendeskWebhookHandler(data)
        handler.zendesk_workflow()
    except Exception as e:
        logger.exception("zendesk_webhook_handle => " + str(e))
