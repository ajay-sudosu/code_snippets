import datetime
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from pydantic import BaseModel

from sqlalchemy_db import Base


class PatientWeight(Base):
    __tablename__ = "patient_weight"

    id = Column(Integer, primary_key=True)
    mrn = Column(String, unique=True)
    weight = Column(String)
    created_date = Column(DateTime, default=datetime.datetime.utcnow)
    updated_date = Column(DateTime, default=func.now())


class PatientWeightSchema(BaseModel):
    mrn: str
    weight: float
