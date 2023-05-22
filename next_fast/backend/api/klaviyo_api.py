import requests
import json
import base64
import logging
from datetime import datetime, timezone

# from db_client import DBClient
logger = logging.getLogger("fastapi")

url = "https://a.klaviyo.com/api/track"

TOKEN = "WxSAWz"
API_KEY = "pk_fbb54c9e8a9ac48c2dd26ab88712707445"


def subscribe_profile_to_sms(email):
    url = "https://a.klaviyo.com/api/v2/list/SaxvxN/subscribe"
    headers = {
        "Content-Type": "application/json",
        "Cache-Control": "no-cache"
    }
    data = {
        "api_key": API_KEY,
        "profiles": [
            {
                "$consent": ["sms"],
                "email": email,
                "sms_consent": True
            }
        ]
    }
    try:
        logger.debug(f"Sending klaviyo request: {data}")

        response = requests.request("POST", url, headers=headers, json=data)

        logger.debug(response.json())
    except Exception as e:
        logger.exception(e)


def send_klaviyo_track_profile(data):
    # client = DBClient()
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json'
    }
    email_id = data["customer_properties"]["$email"]
    
    # result = client.get_patient_profile(email_id)
    # if result and result["consent_klaviyo"] == "1":
    subscribe_profile_to_sms(email=data["customer_properties"]["$email"])
    try:
        logger.debug(f"Sending klaviyo request: {data}")
        s = json.dumps(data)
        encoded_string = base64.b64encode(s.encode('utf-8'))

        payload = {"data": encoded_string}

        response = requests.request(
            "GET", url, headers=headers, params=payload)
        if response.text == "1":
            logger.debug(f"Successfully sent klaviyo request: {data}")
        else:
            logger.warning(f"Failed klaviyo request: {data}")
    except Exception as e:
        logger.exception(e)


def klaviyo_track_profile(email, item_name, item_type, item_value, patient_name,
                          is_insurance=None, patient_address=None, phone_number=None,
                          refills=None, event="ordered product"):

    # dt_now = datetime.now(tz=timezone.utc)
    # timestamp = dt_now.strftime("%y%m%d%H%M%S%f")

    data = {
        "token": TOKEN,
        "event": event,
        "customer_properties": {
            "$email": email,
            "$value": item_value,
            "item_name": item_name,
            "item_type": item_type,
            "name": patient_name,
            "testPrice": item_value,
            "totalPrice": item_value,
        },
    }

    if is_insurance is not None:
        data["customer_properties"]["insurance"] = is_insurance
        data["customer_properties"]["insurancePrice"] = 0.0

    if patient_address is not None:
        data["customer_properties"]["address"] = patient_address

    if refills is not None:
        data["customer_properties"]["refills"] = refills

    if phone_number is not None:
        data["customer_properties"]["$phone_number"] = phone_number

    send_klaviyo_track_profile(data)


def curexa_klaviyo_track_profile(email, patient_name, order_id, status, status_details,
                                 carrier, tracking_number, event="curexa update"):
    data = {
        "token": TOKEN,
        "event": event,
        "customer_properties": {
            "$email": email,
            "order_id": order_id,
            "status": status,
            "status_details": status_details,
            "name": patient_name,
            "carrier": carrier,
            "tracking_number": tracking_number,
        },
    }
    send_klaviyo_track_profile(data)


def curexa_klaviyo_track_month_cron(email, month, event="weight checkin"):
    data = {
        "token": TOKEN,
        "event": event,
        "customer_properties": {
            "$email": email,
            "$check_in_month": month
        },
    }
    send_klaviyo_track_profile(data)


def klaviyo_mdi_prescription_approved(email, patient_name, display_name,
                                      pharmacy_name=None, event="mdi prescription approved"):
    data = {
        "token": TOKEN,
        "event": event,
        "customer_properties": {
            "$email": email,
            "display_name": display_name,
            "name": patient_name
        },
    }
    if pharmacy_name is not None:
        data["customer_properties"]["pharmacy_name"] = pharmacy_name

    send_klaviyo_track_profile(data)


def stripe_subscription_payment_failed(email, patient_name, item_name, item_type, failure_reason,
                                       payment_attempt_time, subscription_renewal_time, payment_amount):
    """send klaviyo notification to klaviyo on stripe failed payment"""
    data = {
        "token": TOKEN,
        "event": "Subscription Payment Failed",
        "customer_properties": {
            "$email": email,
            "name": patient_name,
            "item_name": item_name,
            "item_type": item_type,
            "failure_reason": failure_reason,
            "payment_status": "Failed",
            "last_payment_attempt_time": payment_attempt_time,
            "subscription_renewal_time": subscription_renewal_time,
            "payment_amount": payment_amount,
            "totalPrice": payment_amount,
        },
    }

    send_klaviyo_track_profile(data)


if __name__ == '__main__':
    # klaviyo_track_profile("fpliii@gmail.com", "Wegovy", "weightloss", 119, 1, "Frank", "New Rochelle, New York, United States",refills=3,)
    data = {'order_id': '70902948', 'status': 'out_for_delivery', 'status_details': None,
            'carrier': 'USPS', 'tracking_number': '92001901755477000932144136'}
    stripe_subscription_payment_failed(
        email="fpliii@gmail.com",
        patient_name=f"Frank",
        payment_attempt_time="02 May 2022",
        subscription_renewal_time="02 May 2022",
        payment_amount=10300
    )
    # stripe_subscription_payment_failed("fpliii@gmail.com")
