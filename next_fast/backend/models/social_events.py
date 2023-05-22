from datetime import datetime
from typing import List, Optional

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from pydantic import BaseModel

from models.event_members import EventMembersSchema, EventMembersGetResponseSchema
from sqlalchemy_db import Base


class SocialEvents(Base):
    __tablename__ = "social_events"

    id = Column(Integer, primary_key=True)
    title = Column(String)
    start_date_time = Column(DateTime)
    end_date_time = Column(DateTime)
    description = Column(String)
    event_photo = Column(String)
    location = Column(String)
    event_member = relationship("EventMembers", cascade="all,delete")
    created_date = Column(DateTime, default=datetime.utcnow)
    updated_date = Column(DateTime, default=func.now())


class SocialEventsSchema(BaseModel):
    title: Optional[str]
    start_date_time: Optional[str]
    end_date_time: Optional[str]
    description: Optional[str]
    event_photo: Optional[str]
    location: Optional[str]
    event_members: Optional[List[EventMembersSchema]]


class SocialEventsGetResponseSchema(BaseModel):
    id: int
    title: Optional[str]
    start_date_time: Optional[datetime]
    end_date_time: Optional[datetime]
    description: Optional[str]
    event_photo: Optional[str]
    location: Optional[str]
    created_date: datetime
    updated_date: datetime
    event_member: Optional[List[EventMembersGetResponseSchema]]

    class Config:
        orm_mode = True
