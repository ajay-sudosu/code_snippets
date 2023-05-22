import datetime
import logging
import os
from database.db import get_db
from sqlalchemy.orm import Session
from database.crud import ZendeskNotifyCrud, VisitsCrud
from utils import send_text_message, send_text_email
from healthie import healthie
from mdintegrations import mdintegrations_chat
from api.freshdesk_api import fr_api

log_dir = os.path.join(os.getcwd(), 'log')
logging_file = os.path.join(log_dir,
                            os.path.splitext(os.path.basename(__file__))[0] +
                            datetime.datetime.now().strftime('%y%m%d') +
                            '.log')
logging.basicConfig(
    level=logging.DEBUG,  # DEBUG,
    format='%(asctime)s : %(levelname)s : %(funcName)s : %(message)s',
    filename=logging_file,
    filemode='a',
)

db: Session = next(get_db())


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


def schedule_visit(notify):
    patient_name = notify.get('patient_name', '')
    email = notify.get('email')
    phone = notify.get('phone')
    message = f"Hi {patient_name}, good news! It's time to schedule your first NextMed visit! " \
              f"Please login to your NextMed portal here to book your visit and get started: www.joinnextmed.com/login. " \
              f"We can't wait to meet you!"

    send_notifications(email=email, to_phone=phone, message=message)
    ZendeskNotifyCrud.update_completed(db, notify.get('id'))


def last_notify_action(notify):
    """set is_healthie = 0 and create MDI patient / store mdi patient id in visits col so the MDI logic works."""
    try:
        email = notify.get('email')
        phone = notify.get('phone')
        # set is_healthie = 0
        VisitsCrud.update_visits_is_healthie_by_email(db, email, '0')
        # fetch patient details
        healthie_patient = healthie.get_patient()
        try:
            patient_id = notify.get('patientId')
            # call healthie api to get patient details
            response = healthie.get_patient(patient_id)
            healthie_patient = response.get('data', {}).get('user', {})
        except Exception as e:
            logging.exception(e)
        if 'female' == healthie_patient.get('gender'):
            gender = 1
        else:
            gender = 0
        # Create MDI account
        patient_payload = {
            "first_name": healthie_patient.get('first_name'),
            "last_name": healthie_patient.get('last_name'),
            "email": email,
            "gender": gender,
            "phone_number": phone,
            "date_of_birth": healthie_patient.get('dob')
        }
        mdi_patient = mdintegrations_chat.create_patient(patient_payload)
        logging.debug(mdi_patient)
        # update visits for patient_id_md
        if 'patient_id' in mdi_patient:
            VisitsCrud.update_visits_patient_id_md_by_email(db, email, mdi_patient['patient_id'])
    except Exception as e:
        logging.exception(e)


def visit_cancelled(notify):
    """"""
    patient_name = notify.get('patient_name', '')
    email = notify.get('email')
    phone = notify.get('phone')
    message = f"Hi {patient_name}, your NextMed visit was cancelled. You need to reschedule the visit as " \
              f"soon as possible from your NextMed portal. Get started here: www.joinnextmed.com/login."

    if notify.get('last_notify', False):
        last_notify_action(notify)
    else:
        send_notifications(email=email, to_phone=phone, message=message)

    ZendeskNotifyCrud.update_completed(db, notify.get('id'))


def visit_noshow(notify):
    patient_name = notify.get('patient_name', '')
    email = notify.get('email')
    phone = notify.get('phone')
    message = f"Hi {patient_name}, your NextMed visit was cancelled. You need to reschedule the visit as " \
              f"soon as possible from your NextMed portal. Get started here: www.joinnextmed.com/login." \
              f"If you do not reschedule your visit, you will be charged a $99 visit no-show fee. " \
              f"We are trying to help you reschedule. If you have any questions please contact team@joinnextmed.com"

    if notify.get('last_notify', False):
        last_notify_action(notify)

        # send a ticket to support for no show fee
        payload = {
            "email": "team@joinnextmed.com",
            "description": f"patient email: {email}",
            "subject": "VISIT NO SHOW, CHARGE $99 FEE",
            "status": 2,
            "priority": 4
        }

        try:
            logging.info(f"Creating Freshdesk Ticket: {email}")
            res = fr_api.create_ticket(payload)
            logging.debug(res)
        except Exception as e:
            logging.exception(e)
    else:
        send_notifications(email=email, to_phone=phone, message=message)
    ZendeskNotifyCrud.update_completed(db, notify.get('id'))


def main():
    ts_now = datetime.datetime.now()
    try:
        # fetch all uncompleted notify list
        not_completed_notify_list = ZendeskNotifyCrud.get_notify_by_not_completed(db)
        logging.info(f"Found {len(not_completed_notify_list)} entries in zendesk_notify.")
        for notify in not_completed_notify_list:
            try:
                logging.debug(notify)
                notify_ts = datetime.datetime.strptime(notify["scheduled_ts"], "%Y/%m/%d %H:%M:%S")

                if ts_now.hour != notify_ts.hour:
                    logging.debug("Hours doesn't match. Skipping")
                    continue
                if ts_now.day != notify_ts.day:
                    logging.debug("Day doesn't match. Skipping")
                    continue
                if ts_now.month != notify_ts.month:
                    logging.debug("Month doesn't match. Skipping")
                    continue
                if ts_now.year != notify_ts.year:
                    logging.debug("Year doesn't match. Skipping")
                    continue
                event = notify["event"]
                if 'schedule_visit' == event:
                    run = schedule_visit
                elif 'visit_cancelled' == event:
                    run = visit_cancelled
                elif 'visit_noshow' == event:
                    run = visit_noshow
                else:
                    logging.info(f"Unknown event: {event}, skipping...")
                    continue
                # check if schedule_first_visit == 1 then only execute
                email = notify["email"]
                visits = VisitsCrud.get_visits_row_by_email(db, email)
                for visit in visits:
                    if visit.get('schedule_first_visit') == 1 or visit.get('schedule_first_visit') == '1':
                        # run the appropriate function assigned above
                        run(notify)
                        break
            except Exception as e:
                logging.exception(e)

    except Exception as e:
        logging.exception(e)


if __name__ == '__main__':
    main()
