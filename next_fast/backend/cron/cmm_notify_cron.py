import datetime
import logging
import os
from logging.handlers import TimedRotatingFileHandler
from utils import send_text_message, send_text_email
from database.crud import CMMPAResultsCrud
from database.db import get_db

# logging
logger = logging.getLogger('cmm_notify_cron')
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s : %(levelname)s : %(funcName)s : %(message)s')

log_dir = os.path.join(os.getcwd(), 'log')
logging_file = os.path.join(
    log_dir,
    os.path.splitext(os.path.basename(__file__))[0] + datetime.datetime.now().strftime('%y%m%d') + '.log'
)
fh = TimedRotatingFileHandler(logging_file, when='d', interval=1, backupCount=5)
fh.setLevel(logging.DEBUG)
fh.setFormatter(formatter)
logger.addHandler(fh)

db_session = next(get_db())


class PAProcessNotify:
    def __init__(self):
        self.today = datetime.datetime.now()

    @staticmethod
    def notify(email: str, message: str):
        SENDER = 'team@joinnextmed.com'
        logger.debug(f"Sending email to {email}")
        subject = "NextMed PA Process Updates"
        send_text_email(sender=SENDER, recipient=email, subject=subject, content=message)

    def notify_day_1(self, name, email):
        message = f"""Hi {name}, thanks for completing your intake form and all requirements. 
        We are now starting your prior authorization process to get your medication covered by insurance. 
        This takes about 2 weeks on average so please sit tight and we will update you as things progress. 
        Please reach out to team@joinnextmed.com if you have any questions in the meantime."""
        self.notify(email, message)

    def notify_day_3(self, name, email):
        message = f"""Hi {name}, just a quick update. We've filed all the necessary paperwork with your insurance 
        company and are just waiting to hear back. We will keep you posted. On average, your PA may take about 
        another 2 weeks to get back."""
        self.notify(email, message)

    def notify_day_7(self, name, email):
        message = f"""Hi {name}, can you believe it's been a week? We're still waiting for your insurance 
        plan to get back to us. We'll share updates once we have them."""
        self.notify(email, message)

    def notify_day_14(self, name, email):
        message = f"""Hi {name}, unfortunately we're still waiting for your insurance plan. 
        We'll let you know once we have an update."""
        self.notify(email, message)

    def notify_day_21(self, name, email):
        message = f"""Hi {name}, we're still waiting for your plan to approve your PA. 
        We are working through a list of possible medications to get you covered which is causing some delays. 
        We will keep you posted."""
        self.notify(email, message)

    def notify_day_28(self, name, email):
        message = f"""Hi {name}, your insurance plan unfortunately has been very slow to get back to us. 
        We are still processing your PA with them (unfortunately we're waiting too). 
        We will be in touch soon."""
        self.notify(email, message)

    def notify_day_42(self, name, email):
        message = f"""Hi {name}, your plan is still processing your order. At this point, 
        it may make sense to take a generic medication. Please contact us at team@joinnextmed.com so we 
        can help you further. We apologize for the delays in this process, unfortunately much of it 
        is out of our control."""
        self.notify(email, message)

    def workflow(self):
        logger.info("================ Started ================")
        results = CMMPAResultsCrud.get_all_for_notify(db_session)
        logger.debug(f"No. of PA's in progress: {len(results)}...")

        for res in results:
            try:
                # date_added = datetime.datetime.strptime(res.date_added, "%Y/%m/%d %H:%M:%S")
                # td = self.today - date_added
                # if td.days == 1:
                #     self.notify_day_1(res.name, res.email)
                # elif td.days == 3:
                #     self.notify_day_3(res.name, res.email)
                # elif td.days == 7:
                #     self.notify_day_7(res.name, res.email)
                # elif td.days == 14:
                #     self.notify_day_14(res.name, res.email)
                # elif td.days == 21:
                #     self.notify_day_21(res.name, res.email)
                # elif td.days == 28:
                #     self.notify_day_28(res.name, res.email)
                # elif td.days == 42:
                #     self.notify_day_42(res.name, res.email)
                # else:
                #     logger.debug(f"date {td.days} do not match. skipping...")
                logger.debug("skipping for now...")

            except Exception as e:
                logger.exception(e)

        logger.info("================ Finished ================")


if __name__ == '__main__':
    notify = PAProcessNotify()
    notify.workflow()
