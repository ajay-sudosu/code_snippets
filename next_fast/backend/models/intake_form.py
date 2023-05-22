from datetime import datetime
from typing import Optional

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from pydantic import BaseModel
from sqlalchemy_db import Base


class IntakeForm(Base):
    __tablename__ = "intake_form"

    id = Column(Integer, primary_key=True)
    browser_id = Column(String)
    form_data = Column(String)
    current_step = Column(Integer)
    created_date = Column(DateTime, default=datetime.utcnow)
    updated_date = Column(DateTime, default=func.now())


class IntakeFormSaver(Base):
    __tablename__ = "intake_form_saver"

    mrn = Column(String, primary_key=True)
    form_data = Column(String)
    current_step = Column(Integer)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=func.now())


class IntakeFormPostSchema(BaseModel):
    browser_id: str
    form_data: dict
    current_step: int

class IntakeFormSaverPostSchema(BaseModel):
    mrn: str
    form_data: dict
    current_step: int


class IntakeFormGetResponseSchema(BaseModel):
    current_step: int
    browser_id: str
    form_data: Optional[dict]
    id: int
    created_date: datetime
    updated_date: datetime

    class Config:
        orm_mode = True
