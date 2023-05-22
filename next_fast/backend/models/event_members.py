from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from pydantic import BaseModel
from sqlalchemy_db import Base


class EventMembers(Base):
    __tablename__ = "event_members"

    id = Column(Integer, primary_key=True)
    event_id = Column(Integer, ForeignKey("social_events.id"))
    status = Column(String)
    mrn = Column(String)
    created_date = Column(DateTime, default=datetime.utcnow)
    updated_date = Column(DateTime, default=func.now())


class Status(str, Enum):
    going = 'going'
    maybe_going = 'maybe_going'
    not_going = 'not_going'


class EventMembersSchema(BaseModel):
    status: Status
    mrn: Optional[str]


class EventMembersPostSchema(BaseModel):
    status: Status
    mrn: Optional[str]
    event_id: int


class EventMembersGetResponseSchema(BaseModel):
    event_id: int
    created_date: datetime
    mrn: Optional[str]
    id: int
    updated_date: datetime
    status: str

    class Config:
        orm_mode = True
