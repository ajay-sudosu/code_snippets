import logging
import datetime
from models.intake_form import IntakeForm
from sqlalchemy_db import get_db


logger = logging.getLogger("fastapi")


def delete_old_forms():
    db = next(get_db())
    logger.info("Deleting data older than 20 days")
    old_date = datetime.datetime.utcnow() - datetime.timedelta(days=20)
    db.query(IntakeForm).filter(IntakeForm.created_date < old_date).delete()
    logger.info("completed Deleting data older than 20 days")


if __name__ == "__main__":
    delete_old_forms()
