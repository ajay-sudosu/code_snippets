from typing import Union

from sqlalchemy.orm import Session
from . import models, schemas
from sqlalchemy import text
from datetime import datetime
import logging


class OpenloopCapacityRepo:

    @staticmethod
    def fetch_by_state_abbr(db_session: Session, abbreviation: str):
        return db_session.query(models.OpenloopCapacity).filter(models.OpenloopCapacity.StateAbbreviation == abbreviation).first()

    @staticmethod
    def update_capacity(db_session: Session, openloop_capacity, new_capacity: int):
        if new_capacity == openloop_capacity.Capacity:
            return openloop_capacity
        setattr(openloop_capacity, 'Capacity', new_capacity)
        db_session.commit()
        db_session.refresh(openloop_capacity)
        return openloop_capacity

    @staticmethod
    def update_state_capacity(db_session: Session, abbreviation: str, new_capacity: int):
        openloop_capacity = db_session.query(models.OpenloopCapacity).filter(
            models.OpenloopCapacity.StateAbbreviation == abbreviation).first()
        if openloop_capacity is None:
            return None
        if new_capacity == openloop_capacity.Capacity:
            return openloop_capacity
        setattr(openloop_capacity, 'Capacity', new_capacity)
        db_session.commit()
        db_session.refresh(openloop_capacity)
        return openloop_capacity


class ZendeskNotifyCrud:

    @staticmethod
    def create(db_session: Session, notify: schemas.ZendeskNotifyBase):
        db_notify = models.ZendeskNotify(scheduled_ts=notify.scheduled_ts,
                                         email=notify.email,
                                         patient_id=notify.patient_id,
                                         patient_name=notify.patient_name,
                                         phone=notify.phone,
                                         event=notify.event,
                                         last_notify=notify.last_notify,
                                         completed=False)
        db_session.add(db_notify)
        db_session.commit()
        db_session.refresh(db_notify)
        return db_notify

    @staticmethod
    def update_completed(db_session: Session, row_id: int):
        db_notify = db_session.query(models.ZendeskNotify).filter(models.ZendeskNotify.id == row_id).first()
        if db_notify is None:
            return None
        setattr(db_notify, 'completed', True)
        db_session.commit()
        db_session.refresh(db_notify)
        return db_notify

    @staticmethod
    def get_notify_by_not_completed(db_session: Session):
        results = db_session.query(models.ZendeskNotify).filter(models.ZendeskNotify.completed.is_(False)).all()
        return [res.__dict__ for res in list(results)]


class ConfigCrud:

    @staticmethod
    def get_config_by_key(db_session: Session, key: str):
        return db_session.query(models.ConfigModel).filter(
            models.ConfigModel.key == key).first()

    @staticmethod
    def update_config_key_value(db_session: Session, key: str, new_value: int):
        db_config = db_session.query(models.ConfigModel).filter(
            models.ConfigModel.key == key).first()
        if db_config is None:
            return None
        setattr(db_config, 'value', new_value)
        ts = datetime.now()
        setattr(db_config, 'updated_at', ts.strftime("%Y/%m/%d %H:%M:%S"))
        db_session.commit()
        db_session.refresh(db_config)
        return db_config


class VisitsCrud:

    @staticmethod
    def get_visits_row_by_email(db_session: Session, email: str):
        sql = text(f'select * from visits where email="{email}"')
        results = db_session.execute(sql).mappings().all()
        return results

    @staticmethod
    def get_visits_by_mrn(db_session: Session, mrn: str):
        sql = text(f'select * from visits where mrn="{mrn}"')
        result = db_session.execute(sql).mappings().first()
        return result

    @staticmethod
    def get_visits_row_by_patient_id_md(db_session: Session, patient_id_md: str):
        try:
            sql = text(f'select * from visits where patient_id_md="{patient_id_md}"')
            results = db_session.execute(sql).mappings().all()
            return results
        except Exception as e:
            logging.exception(e)
            return []

    @staticmethod
    def update_visits_is_healthie_by_email(db_session: Session, email: str, value: str):
        sql = text(f'UPDATE visits SET is_healthie="{value}" WHERE email="{email}"')
        results = db_session.execute(sql)
        db_session.commit()
        return results

    @staticmethod
    def update_visits_is_async_by_email(db_session: Session, email: str, value: str):
        sql = text(f'UPDATE visits SET is_async="{value}" WHERE email="{email}"')
        results = db_session.execute(sql)
        db_session.commit()
        return results

    @staticmethod
    def get_visits_by_email(db_session: Session, email: str):
        sql = text(f'Select * from visits WHERE email="{email}"')
        results = db_session.execute(sql)
        db_session.commit()
        return results

    @staticmethod
    def get_visits_by_patient_name(db_session: Session, patient_name: str):
        sql = text(f'Select * from visits WHERE patient_name="{patient_name}"')
        results = db_session.execute(sql)
        db_session.commit()
        return results

    @staticmethod
    def update_visits_patient_id_md_by_email(db_session: Session, email: str, patient_id_md: str):
        sql = text(f'UPDATE visits SET patient_id_md="{patient_id_md}" WHERE email="{email}"')
        results = db_session.execute(sql)
        db_session.commit()
        return results

    @staticmethod
    def update_visits_schedule_first_visit_by_email(db_session: Session, email: str, value: int):
        sql = text(f'UPDATE visits SET schedule_first_visit={value} WHERE email="{email}"')
        results = db_session.execute(sql)
        db_session.commit()
        return results

    @staticmethod
    def update_visits_visit_no_showed_by_email(db_session: Session, email: str, value: str):
        sql = text(f'UPDATE visits SET visit_no_showed="{value}" WHERE email="{email}"')
        results = db_session.execute(sql)
        db_session.commit()
        return results

    @staticmethod
    def update_visits_first_visit_by_email(db_session: Session, email: str, value: str):
        sql = text(f'UPDATE visits SET first_visit="{value}" WHERE email="{email}"')
        results = db_session.execute(sql)
        db_session.commit()
        return results

    @staticmethod
    def update_visits_start_pa_process_by_email(db_session: Session, email: str, value: str):
        sql = text(f'UPDATE visits SET start_pa_process="{value}" WHERE email="{email}"')
        results = db_session.execute(sql)
        db_session.commit()
        return results
    
    @staticmethod
    def update_schedule_followup_visit_col_endpoint(db_session: Session, email: str):
        sql = text(f'update visits set first_visit=true where email="{email}"')
        results = db_session.execute(sql)
        db_session.commit()
        return results

    @staticmethod
    def update_visits_eligibility_check_by_email(
            db_session: Session,
            email: str,
            copay_amount: int,
            coinsurance_amount: int,
            eligibility_check: str,
            insurance_elig_checked: int,
            ccmEligible: str,
            ccmCopay: float,
            ccmCoinsurance: int,
            rpmEligible: str,
            rpmCopay: float,
            rpmCoinsurance: int
    ):
        """update visits row for insurance_elig_checked"""
        sql = text(f'UPDATE visits SET copay_amount={copay_amount}, coinsurance_amount={coinsurance_amount}, eligibility_check="{eligibility_check}", insurance_elig_checked={insurance_elig_checked}, ccmEligible="{ccmEligible}", ccmCopay={ccmCopay}, ccmCoinsurance={ccmCoinsurance},rpmEligible="{rpmEligible}", rpmCopay={rpmCopay}, rpmCoinsurance={rpmCoinsurance} WHERE email="{email}"')
        results = db_session.execute(sql)
        db_session.commit()
        return results

    @staticmethod
    def get_visits_by_patient_id(db_session: Session, patient_id: str):
        try:
            sql = text(f'SELECT * FROM visits WHERE patient_id="{patient_id}"')
            results = db_session.execute(sql).mappings().all()
            return results
        except Exception as e:
            logging.exception(e)
            return []

    @staticmethod
    def update_visits_drchrono_req(db_session: Session, req: str, ts: str, mrn: str):
        sql = text(f'update visits set drchrono_req="{req}", drchrono_req_ts="{ts}" where mrn="{mrn}"')
        results = db_session.execute(sql)
        db_session.commit()
        return results

    @staticmethod
    def update_visits_weight_medicine_type_by_healthie_id(db_session: Session, healthie_id: str, value: str):
        try:
            sql = text(f'UPDATE visits SET weight_medicine_type="{value}" WHERE healthie_id="{healthie_id}"')
            results = db_session.execute(sql)
            db_session.commit()
            return results
        except Exception as e:
            logging.exception(e)
            return None

    @staticmethod
    def update_visits_weight_medicine_type_by_mrn(db_session: Session, mrn: str, value: str):
        try:
            sql = text(f'UPDATE visits SET weight_medicine_type="{value}" WHERE mrn="{mrn}"')
            results = db_session.execute(sql)
            db_session.commit()
            return results
        except Exception as e:
            logging.exception(e)
            return None

    @staticmethod
    def update_visits_chief_complaint_by_healthie_id(db_session: Session, healthie_id: str, chief_complaint: str):
        try:
            sql = text(f'UPDATE visits SET chief_complaint="{chief_complaint}" WHERE healthie_id="{healthie_id}"')
            results = db_session.execute(sql)
            db_session.commit()
            return results
        except Exception as e:
            logging.exception(e)
            return None

    @staticmethod
    def update_visits_openloop_customer_id_by_email(db_session: Session, email: str, openloop_customer_id: str):
        try:
            sql = text(f'UPDATE visits SET openloop_customer_id="{openloop_customer_id}" WHERE email="{email}"')
            results = db_session.execute(sql)
            db_session.commit()
            return results
        except Exception as e:
            logging.exception(e)
            return None

    @staticmethod
    def update_visits_is_second_lab_order_by_email(db_session: Session, email: str, is_second_lab_order: bool):
        try:
            sql = text(f'UPDATE visits SET is_second_lab_order="{is_second_lab_order}" WHERE email="{email}"')
            results = db_session.execute(sql)
            db_session.commit()
            return results
        except Exception as e:
            logging.exception(e)
            return None


class MDIMappingCrud:

    @staticmethod
    def create(db_session: Session, mapping: schemas.MDIMappingSchema):
        db_mapping = models.MDIMapping(patient_id=mapping.patient_id,
                                       email=mapping.email,
                                       mdi_account_type=mapping.mdi_account_type)
        db_session.add(db_mapping)
        db_session.commit()
        db_session.refresh(db_mapping)
        return db_mapping

    @staticmethod
    def create_with_values(db_session: Session, patient_id: str, email: str, mdi_account_type: str):
        db_mapping = models.MDIMapping(patient_id=patient_id,
                                       email=email,
                                       mdi_account_type=mdi_account_type)
        db_session.add(db_mapping)
        db_session.commit()
        db_session.refresh(db_mapping)
        return db_mapping

    @staticmethod
    def fetch_by_patient_id(db_session: Session, patient_id: str):
        return db_session.query(models.MDIMapping).filter(models.MDIMapping.patient_id == patient_id).first()


class MDICaseMappingCrud:

    @staticmethod
    def create(db_session: Session, mapping: schemas.MDICaseMappingSchema):
        db_mapping = models.MDICaseMapping(
            case_id=mapping.case_id,
            patient_id=mapping.patient_id,
            mdi_account_type=mapping.mdi_account_type
        )
        db_session.add(db_mapping)
        db_session.commit()
        db_session.refresh(db_mapping)
        return db_mapping

    @staticmethod
    def create_with_values(db_session: Session, case_id: str, patient_id: str, mdi_account_type: str):
        db_mapping = models.MDICaseMapping(
            case_id=case_id,
            patient_id=patient_id,
            mdi_account_type=mdi_account_type
        )
        db_session.add(db_mapping)
        db_session.commit()
        db_session.refresh(db_mapping)
        return db_mapping

    @staticmethod
    def fetch_by_case_id(db_session: Session, case_id: str):
        return db_session.query(models.MDICaseMapping).filter(models.MDICaseMapping.case_id == case_id).first()


class QuestionCrud:

    @staticmethod
    def get_question_by_mrn(db_session: Session, mrn: str):
        sql = text(f'select * from question where mrn="{mrn}"')
        results = db_session.execute(sql).mappings().all()
        return results


class StripePauseSubscriptionCrud:

    @staticmethod
    def create_with_values(db_session: Session, subscription_id: str, email: str, status: str):
        ts = datetime.now()
        db_mapping = models.StripePauseSubscription(
            subscription_id=subscription_id,
            email=email,
            status=status,
            updated_at=ts.strftime("%Y/%m/%d %H:%M:%S")
        )
        db_session.add(db_mapping)
        db_session.commit()
        db_session.refresh(db_mapping)
        return db_mapping

    @staticmethod
    def update_status(db_session: Session, subscription_id: str, status: str):
        db_mapping = db_session.query(models.StripePauseSubscription).filter(
            models.StripePauseSubscription.subscription_id == subscription_id).first()
        if db_mapping is None:
            return None
        setattr(db_mapping, 'status', status)
        ts = datetime.now()
        setattr(db_mapping, 'updated_at', ts.strftime("%Y/%m/%d %H:%M:%S"))
        db_session.commit()
        db_session.refresh(db_mapping)
        return db_mapping

    @staticmethod
    def get_all_by_status(db_session: Session, status: str):
        return db_session.query(models.StripePauseSubscription).filter(
            models.StripePauseSubscription.status == status).all()


class CMMPAResultsCrud:
    @staticmethod
    def create_with_values(
            db_session: Session, mrn: str, email: str, name: str,
            date_added: str, mounjaro: Union[str, None], ozempic: Union[str, None],
            rybelsus: Union[str, None], saxenda: Union[str, None], wegovy: Union[str, None],
            preferred_drug_approved: bool, rejected_all: bool, date_started: Union[str, None]
    ):
        db_mapping = models.CMMPAResults(
            mrn=mrn,
            email=email,
            name=name,
            date_added=date_added,
            mounjaro=mounjaro,
            ozempic=ozempic,
            rybelsus=rybelsus,
            saxenda=saxenda,
            wegovy=wegovy,
            preferred_drug_approved=preferred_drug_approved,
            rejected_all=rejected_all,
            date_started=date_started,
            pa_processed=False
        )
        db_session.add(db_mapping)
        db_session.commit()
        db_session.refresh(db_mapping)
        return db_mapping

    @staticmethod
    def find_by_mrn(db_session: Session, mrn: str):
        return db_session.query(models.CMMPAResults).filter(
            models.CMMPAResults.mrn == mrn).all()

    @staticmethod
    def get_all_for_notify(db_session: Session):
        return db_session.query(models.CMMPAResults)\
            .filter(models.CMMPAResults.preferred_drug_approved == 0)\
            .filter(models.CMMPAResults.rejected_all == 0).all()

    @staticmethod
    def find_by_name(db_session: Session, name: str):
        return db_session.query(models.CMMPAResults).filter(
            models.CMMPAResults.name == name).all()

    @staticmethod
    def update_rejected_all_by_mrn(db_session: Session, mrn: str, rejected_all: bool):
        try:
            db_mapping = db_session.query(models.CMMPAResults).filter(
                models.CMMPAResults.mrn == mrn).first()
            if db_mapping is None:
                return None
            setattr(db_mapping, 'rejected_all', rejected_all)
            db_session.commit()
            db_session.refresh(db_mapping)
            return db_mapping
        except Exception as e:
            logging.exception(e)
            return None

    @staticmethod
    def update_pa_processed_by_mrn(db_session: Session, mrn: str, pa_processed: bool):
        try:
            db_mapping = db_session.query(models.CMMPAResults).filter(
                models.CMMPAResults.mrn == mrn).first()
            if db_mapping is None:
                return None
            setattr(db_mapping, 'pa_processed', pa_processed)
            db_session.commit()
            db_session.refresh(db_mapping)
            return db_mapping
        except Exception as e:
            logging.exception(e)
            return None
