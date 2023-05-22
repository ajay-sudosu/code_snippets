from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from sqlalchemy_db import Base


class FailedSubscriptions(Base):
    __tablename__ = "failed_subscriptions"

    id = Column(Integer, primary_key=True)
    patient_name = Column(String)
    patient_email = Column(String)
    patient_phone = Column(String)
    is_processed = Column(Integer)
    created_date = Column(DateTime, default=datetime.utcnow)
    updated_date = Column(DateTime, default=func.now())
