"""
Updates for NXTMD-365
=====================
We need CRON to send out text & email notifications to patients who aren't verified yet.
TO achieve this we have the following fields in visits table:-
1- server_date_time
2- is_user_verified

We also need to send out text & email notifications to patients who haven't checked in yet.
TO achieve this we have the following fields in visits table:
1. curr_dose

We want to notify patient these times if not verified or not checkin
1- After 1, 4, 12, 48, 72 hours of booking
2- After 7 days of booking

"""
import json
import os
import pandas as pd
from pathlib import Path
from db_client import DBClient
import logging
import datetime
from utils import send_text_message, send_text_email
from dateutil.parser import parse


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


def int_to_time(time_int: int) -> tuple:
    """Convert int to hour & minutes
    419 -> hr = 4 & min = 19
    0 -> hr = 0 & min = 0
    """
    time_str = '%4d' % time_int
    time_str = time_str.replace(' ', '0')

    df = pd.to_datetime(time_str, format='%H%M')
    return df.hour, df.minute


def send_notifications(name: str, email: str, to_phone: str, message_type: str):
    """
    send text & email notifications
    name: receiver's name
    email: receiver's email
    to_phone: receiver's phone
    message_type: 'intake' or 'checkin'
    """
    subject = 'Your Action Needed'
    if message_type == 'checkin':
        message = f"Hi {name}, it’s time to get your next medication refill from NextMed. " \
                  f"To do so, you must fill out a quick 15 second check-in form by logging into " \
                  f"your NextMed portal at https://www.joinnextmed.com/login " \
                  f"Please do this ASAP as you will not receive your refill until you’ve completed the check-in."

    else:
        message = f"Dear {name}, You haven't filled your intake form. " \
                  f"You can not receive your lab testing or prescription without filling this out. " \
                  f"Please fill the intake form at https://www.joinnextmed.com/login to complete the process." \
                  f" Thanks."
    try:
        logging.debug(f"Sending text to {to_phone}")
        send_text_message(to_phone, message)
    except Exception as e:
        logging.exception(e)

    SENDER = 'team@joinnextmed.com'
    logging.debug(f"Sending email to {email}")
    send_text_email(sender=SENDER, recipient=email, subject=subject, content=message)


def workflow_intake_notify():
    try:
        current_ts = datetime.datetime.now()
        db = DBClient()
        # fetch list of not verified patients
        unverified_patients = db.get_not_verified_patients_from_visits()
        logging.debug(f"No. of unverified patients: {len(unverified_patients)}...")

        for patient in unverified_patients:
            try:
                logging.debug(patient)
                server_date_time = patient["server_date_time"]
                phone = patient["phone"]
                if server_date_time is None:
                    logging.debug(f"server_date_time is None. skipping {phone}...")
                    continue
                try:
                    booking_ts = datetime.datetime.strptime(patient["server_date_time"], "%d/%m/%Y %H:%M:%S")
                except Exception as e:
                    logging.exception(e)
                    booking_ts = datetime.datetime.strptime(patient["server_date_time"], "%d-%m-%Y:%H:%M:%S")

                patient_name = patient["patient_name"]
                email = patient["email"]

                # fetch notifications sent for this phone
                text_notification = db.get_notifications_text_sent(phone)

                if text_notification > 2:
                    logging.debug(f"already {text_notification} texts sent. skipping {phone}...")
                    continue
                elif text_notification == -1:
                    logging.debug(f"inserting into db.notifications {phone}...")
                    db.insert_notifications(phone)
                    text_notification = db.get_notifications_text_sent(phone)

                # find timedelta
                td = current_ts - booking_ts

                def send_update():
                    try:
                        send_notifications(patient_name, email, phone, 'intake')
                        logging.debug(f"incrementing notification for {phone}...")
                        db.increment_notifications_text_sent(phone)
                    except Exception as e1:
                        logging.exception(e1)

                if td.days > 2:
                    logging.debug(f"time delta >2 days. skipping {phone}...")
                    continue
                elif td.days == 2 and text_notification < 3:
                    send_update()
                elif td.days == 1 and text_notification < 2:
                    send_update()
                elif td.seconds >= 3600 and text_notification < 1:
                    send_update()
                else:
                    logging.debug(f"condition not met. skipping {phone}...")
                    continue
            except Exception as e:
                logging.exception(e)
    except Exception as e:
        logging.exception(e)


class CheckinNotify:

    filename = 'checkin_notify.json'
    max_notify_count = 7

    def __init__(self):
        self.unfilled_checkin_dict = {}
        self.dict_file = Path(self.filename)
        self.dict_file.touch(exist_ok=True)
        self.load_dict()
        self.current_ts = str(datetime.datetime.now())

    def load_dict(self):
        with open(self.dict_file, 'r') as openfile:
            try:
                self.unfilled_checkin_dict = json.load(openfile)
            except Exception as e:
                logging.exception(e)

    def save_dict(self):
        try:
            with open(self.dict_file, "w") as outfile:
                json.dump(self.unfilled_checkin_dict, outfile)
        except Exception as e:
            logging.exception(e)

    def increment_notifications_sent(self, email):
        try:
            self.unfilled_checkin_dict[email]['notifications_sent'] += 1
            self.unfilled_checkin_dict[email]['last_notification_ts'] = str(self.current_ts)
            self.save_dict()
        except Exception as e:
            logging.exception(e)

    def is_max_notify_sent(self, email):
        text_notification = self.unfilled_checkin_dict[email]['notifications_sent']
        if text_notification < self.max_notify_count:
            return False
        logging.info(f"already {text_notification} texts sent. skipping {email}...")
        return True

    def new_checkin_form(self, patient):
        logging.info(f"{patient}")
        email = patient.get('email')
        patient_name = patient.get('patient_name', '')
        phone = patient.get('phone', '')
        # add to dict
        self.unfilled_checkin_dict[email] = {
            'patient_name': patient_name,
            'phone': phone,
            'notifications_sent': 1,
            'first_notification_ts': str(self.current_ts),
            'last_notification_ts': str(self.current_ts)
        }
        # save to disk
        self.save_dict()
        # send notification
        send_notifications(name=patient_name, email=email, to_phone=phone, message_type='checkin')

    def get_timedelta(self, email):
        td = parse(self.current_ts) - parse(self.unfilled_checkin_dict[email]['first_notification_ts'])
        return td

    def notify(self, email):
        patient = self.unfilled_checkin_dict[email]
        # send notification
        send_notifications(name=patient.get('patient_name'),
                           email=email,
                           to_phone=patient.get('phone'),
                           message_type='checkin')
        self.increment_notifications_sent(email)

    def existing_checkin_form(self, email):
        def get_hours(td):
            return td.seconds//3600

        notify_hr_dict = {
            1: 1,
            2: 4,
            3: 12,
            4: 24,
            5: 48,
            6: 72,
            7: 168
        }
        patient = self.unfilled_checkin_dict[email]
        logging.debug(f"{patient}")
        if self.is_max_notify_sent(email):
            return

        time_delta = self.get_timedelta(email)
        sent_count = patient.get('notifications_sent')

        for count, interval in notify_hr_dict.items():
            if get_hours(time_delta) == interval and sent_count < count:
                self.notify(email)
                break

    def remove_checked_in(self, unfilled_checkin_forms):
        """remove patients who checked in from last time"""
        unfilled_emails = [v['email'] for v in unfilled_checkin_forms]

        for email in self.unfilled_checkin_dict.keys():
            if email not in unfilled_emails:
                del self.unfilled_checkin_dict[email]

        self.save_dict()

    def workflow(self):
        try:
            db = DBClient()
            # fetch list of patients for checkin
            unfilled_checkin_forms = db.get_not_checked_in_patients_from_visits()
            logging.debug(f"No. of unfilled checkin patients : {len(unfilled_checkin_forms)}...")

            if len(unfilled_checkin_forms):
                self.remove_checked_in(unfilled_checkin_forms)

            for patient in unfilled_checkin_forms:
                try:
                    # new checkin form
                    if patient['email'] not in self.unfilled_checkin_dict:
                        self.new_checkin_form(patient)
                        continue
                    # existing checkin form
                    self.existing_checkin_form(patient['email'])
                except Exception as e:
                    logging.exception(e)
        except Exception as e:
            logging.exception(e)


def workflow_checkin_notify():
    checkin = CheckinNotify()
    checkin.workflow()


def main():
    logging.info("Started")
    workflow_intake_notify()
    workflow_checkin_notify()
    logging.info("Finished")


if __name__ == '__main__':
    main()
