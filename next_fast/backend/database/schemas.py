from typing import List, Optional
from pydantic import BaseModel


class OpenloopCapacityBase(BaseModel):
    StateAbbreviation: str


class OpenloopCapacitySchema(OpenloopCapacityBase):
    Capacity: int

    class Config:
        orm_mode = True


class ZendeskNotifyBase(BaseModel):
    scheduled_ts: str
    email: str
    patient_id: str
    patient_name: str
    phone: str
    event: str
    last_notify: bool


class ZendeskNotifySchema(ZendeskNotifyBase):
    id: int
    completed: bool

    class Config:
        orm_mode = True


class ConfigSchema(BaseModel):
    key: str
    value: int
    created_at: str
    updated_at: str

    class Config:
        orm_mode = True


class MDIMappingSchema(BaseModel):
    patient_id: str
    email: str
    mdi_account_type: str

    class Config:
        orm_mode = True


class MDICaseMappingSchema(BaseModel):
    case_id: str
    patient_id: str
    mdi_account_type: str

    class Config:
        orm_mode = True


class StripePauseSubscriptionSchema(BaseModel):
    subscription_id: str
    email: str
    status: str

    class Config:
        orm_mode = True


class CMMPAResultsSchema(BaseModel):
    mrn: str
    email: str
    name: str
    date_added: str
    mounjaro: str
    ozempic: str
    rybelsus: str
    saxenda: str
    wegovy: str
    preferred_drug_approved: bool
    rejected_all: bool
    date_started: str
    pa_processed: bool


class SmartScaleSchema(BaseModel):
    device_number: str
    recorded_date: str
    weight: str
    systolic: str
    diastolic: str
    pulse: str
    assignee_id: int
    device_type: str

    class Config:
        orm_mode = True
