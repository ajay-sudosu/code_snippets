from sqlalchemy import Column, Integer, String, Boolean
from database.db import Base


class OpenloopCapacity(Base):
    __tablename__ = "openloop_capacity"

    StateName = Column(String(255))
    StateAbbreviation = Column(String(10), primary_key=True, index=True)
    Capacity = Column(Integer, nullable=False, default=1)


class ZendeskNotify(Base):
    __tablename__ = "zendesk_notify"

    id = Column(Integer, primary_key=True, index=True)
    scheduled_ts = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    patient_id = Column(String(255))
    patient_name = Column(String(255))
    phone = Column(String(255))
    event = Column(String(255))
    last_notify = Column(Boolean, default=False, nullable=False)
    completed = Column(Boolean, default=False, nullable=False)


class ConfigModel(Base):
    __tablename__ = 'config'

    key = Column(String(255), nullable=False, primary_key=True, index=True)
    value = Column(Integer, nullable=False)
    created_at = Column(String(255), nullable=False)
    updated_at = Column(String(255))


class MDIMapping(Base):
    __tablename__ = 'mdi_mapping'

    patient_id = Column(String(255), primary_key=True, index=True)
    email = Column(String(255))
    mdi_account_type = Column(String(255), nullable=False)


class MDICaseMapping(Base):
    __tablename__ = 'mdi_case_mapping'

    case_id = Column(String(255), primary_key=True, index=True)
    patient_id = Column(String(255))
    mdi_account_type = Column(String(255), nullable=False)


class StripePauseSubscription(Base):
    __tablename__ = 'stripe_pause_subscription'

    subscription_id = Column(String(255), primary_key=True, index=True)
    email = Column(String(255))
    status = Column(String(255), nullable=False)
    updated_at = Column(String(255))


class CMMPAResults(Base):
    __tablename__ = 'pa_results'

    mrn = Column(String(255))
    email = Column(String(255), primary_key=True)
    name = Column(String(255), primary_key=True)
    date_added = Column(String(255))
    mounjaro = Column(String(255))
    ozempic = Column(String(255))
    rybelsus = Column(String(255))
    saxenda = Column(String(255))
    wegovy = Column(String(255))
    preferred_drug_approved = Column(Boolean, default=False)
    rejected_all = Column(Boolean, default=False)
    date_started = Column(String(255))
    pa_processed = Column(Boolean, default=False)


class RpmPatientEnrollment(Base):
    __tablename__ = 'rpm_patient_enrollment'

    mrn = Column(String(255), nullable=False, primary_key=True, index=True)
    record_identifier = Column(String(255))
    patient_first_name = Column(String(255))
    patient_middle_name = Column(String(255), nullable=True)
    patient_last_name = Column(String(255))
    dob = Column(String(255))
    gender = Column(String(255))
    facility_name = Column(String(255))
    physician_name = Column(String(255))
    clinician_name = Column(String(255))
    address_line_one = Column(String(255), nullable=True)
    address_line_two = Column(String(255), nullable=True)
    zipcode = Column(Integer, nullable=True)
    city = Column(String(255), nullable=True)
    state = Column(String(255), nullable=True)
    mobile_phone = Column(String(255), nullable=True)
    home_phone = Column(String(255), nullable=True)
    work_phone = Column(String(255), nullable=True)
    other_phone = Column(String(255), nullable=True)
    vendor_unique_transaction_id = Column(Integer, nullable=True)


class RpmProgramEnrollment(Base):
    __tablename__ = 'rpm_program_enrollment'

    mrn = Column(String(255), nullable=False, primary_key=True, index=True)
    record_identifier = Column(String(255))
    consent_type = Column(String(255))
    consent_signed_date = Column(String(255), nullable=True)
    consent_recorded_date = Column(String(255), nullable=True)
    monthly_call_task_creation = Column(String(5), nullable=True)
    vendor_unique_transaction_id = Column(Integer, nullable=True)


class SmartScale(Base):
    __tablename__ = 'smart_scale'

    id = Column(Integer, primary_key=True, index=True)
    device_number = Column(String(255), nullable=True)
    recorded_date = Column(String(255), nullable=True)
    weight = Column(String(255), nullable=True)
    systolic = Column(String(255), nullable=True)
    diastolic = Column(String(255), nullable=True)
    pulse = Column(String(255), nullable=True)
    assignee_id = Column(Integer, nullable=True)
    device_type = Column(String(255), nullable=True)
