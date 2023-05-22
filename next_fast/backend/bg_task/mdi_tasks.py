import logging
from mdintegrations import mdi_instance_dict, mdintegrations_chat, mdintegrations_api, \
    mdi_accutane, mdi_weightloss, mdi_testosterone, MDintegrationsPatientPharmacy, detect_mdi_account_type
import time
from database.db import get_db


logger = logging.getLogger("fastapi")


def mdi_webhook_handle(data):
    """Handle different MDI webhook events"""
    try:
        mdintegrations_chat.handle_webhook(data)
    except Exception as e:
        logger.exception("mdi_webhook_handle => " + str(e))


def mdi_webhook_handle_accutane(data):
    """Handle different MDI webhook events for accutane account"""
    try:
        mdi_accutane.handle_webhook(data, test_type="accutane")
    except Exception as e:
        logger.exception("mdi_webhook_handle_accutane => " + str(e))


def mdi_webhook_handle_weightloss(data):
    """Handle different MDI webhook events for weightloss account"""
    try:
        mdi_weightloss.handle_webhook(data, test_type="weightloss")
    except Exception as e:
        logger.exception("mdi_webhook_handle_weightloss => " + str(e))


def mdi_webhook_handle_testosterone(data):
    """Handle different MDI webhook events for testosterone account"""
    try:
        mdi_testosterone.handle_webhook(data, test_type="testosterone")
    except Exception as e:
        logger.exception("mdi_webhook_handle_testosterone => " + str(e))


def mdi_webhook_handle_aging(data):
    """Handle different MDI webhook events for aging account"""
    try:
        mdi_instance = mdi_instance_dict.get('aging')
        mdi_instance.handle_webhook(data, test_type="aging")
    except Exception as e:
        logger.exception("mdi_webhook_handle_aging => " + str(e))


def mdi_webhook_handle_canada(data):
    """Handle different MDI webhook events for canada account"""
    try:
        mdi_instance = mdi_instance_dict.get('canada')
        mdi_instance.handle_webhook(data, test_type="canada")
    except Exception as e:
        logger.exception("mdi_webhook_handle_canada => " + str(e))


def mdi_webhook_handle_diagnostics(data):
    """Handle different MDI webhook events for diagnostics account"""
    try:
        mdi_instance = mdi_instance_dict.get('diagnostics')
        mdi_instance.handle_webhook(data, test_type="diagnostics")
    except Exception as e:
        logger.exception("mdi_webhook_handle_diagnostics => " + str(e))


def mdi_attach_pharmacy_to_patient(data: MDintegrationsPatientPharmacy):
    attempt = 0
    interval = 60
    set_as_primary = data.set_as_primary
    if set_as_primary is None:
        set_as_primary = True
    try:
        db_session = next(get_db())
        # find correct account
        test_type, mdi_api = detect_mdi_account_type(db_session, data.patient_id)

        while True:
            attempt += 1
            res = mdi_api.add_pharmacy_to_patient(
                patient_id=data.patient_id,
                pharmacy_id=data.pharmacy_id,
                set_as_primary=set_as_primary)
            if "error" in res:
                logger.warning(res)
                logger.info(f"Patient: {data.patient_id}, Attempt: {attempt} Failed.")
                if res.get('error') == "Patient needs to be synced to dosespot.":
                    time.sleep(interval)
                else:
                    return
            else:
                logger.info(f"Patient: {data.patient_id}, Attempt: {attempt} Successful.")
                return
    except Exception as e:
        logger.exception("mdi_attach_pharmacy_to_patient => " + str(e))
