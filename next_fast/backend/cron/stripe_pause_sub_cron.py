import logging
import os
from logging.handlers import TimedRotatingFileHandler
import datetime
from database.crud import StripePauseSubscriptionCrud
from database.db import get_db
from sqlalchemy.orm import Session
from stripe_api import get_subscription, pause_subscription

# logging
logger = logging.getLogger('stripe_pause')
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


db: Session = next(get_db())


class PauseSubscriptionCron:

    def __init__(self):
        self.tomorrow = datetime.datetime.now() + datetime.timedelta(days=1)

    def workflow(self):
        try:
            # fetch all subscriptions to be paused
            active_subscriptions = StripePauseSubscriptionCrud.get_all_by_status(db, status='active')
            logger.info(f"Total Active subscriptions to be paused: {len(active_subscriptions)}")
            # iterate over the list
            for sub in active_subscriptions:
                try:
                    # fetch sub's renewal date
                    subscription = get_subscription(sub.subscription_id)

                    # if renewal date is tomorrow: pause subscription
                    current_period_end_ts = subscription.get('current_period_end')
                    current_period_end = datetime.datetime.fromtimestamp(current_period_end_ts)
                    if current_period_end.date() == self.tomorrow.date():
                        logger.debug(f"Pausing sub: {sub.subscription_id}")
                        response = pause_subscription(sub.subscription_id)
                        logger.debug(response)

                        logger.debug(f"updating status=paused for sub: {sub.subscription_id}")
                        # update db for status
                        StripePauseSubscriptionCrud.update_status(
                            db,
                            subscription_id=sub.subscription_id,
                            status='paused'
                        )
                    else:
                        logger.debug(f"Date doesn't match. skipping sub: {sub.subscription_id}")
                except Exception as e:
                    logger.exception(e)

        except Exception as e:
            logger.exception(e)


def main():
    logger.info("Started")

    cron = PauseSubscriptionCron()
    cron.workflow()

    logger.info("Finished")
    logging.shutdown()


if __name__ == '__main__':
    main()
