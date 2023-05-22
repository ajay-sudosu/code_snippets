import os
from typing import Optional

import cognitojwt
import requests
import stripe
from fastapi import Request, FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

import stripe_api
from auth.JWTBearer import JWTBearer
from auth.cognito import confirm_signup, resend_temp_password, cognito_upload_image
from auth.jwk_model import jwks
from axle import *
from db_client import *
from functions import *
from mdintegrations import mdintegrations_api, mdintegrations_chat
from routers import (
    router_curexa, router_drchrono, router_user, router_mdi, router_workpath, router_stripe,
    router_misc, router_healthie, router_freshdesk, router_spreadsheet,
    router_covermymeds, router_health_check, router_zendesk, router_humhealth, router_gogomeds
)
from utils import get_log_level
from fastapi import FastAPI, Body
from auth.simple_auth.models import UserSchema, UserLoginSchema
from auth.simple_auth.simple_jwt_auth import signJWT

REGION = 'us-east-2'
USERPOOL_ID = 'us-east-2_WMP1mBeSc'
APP_CLIENT_ID = '3t6c0ijh7i1g4ngla0krrvh22b'

NURSE_USERPOOL_ID = 'us-east-2_7qwZG9iIB'
NURSE_APP_CLIENT_ID = '6o12h0t99duupbnvbv81kr5361'

PATIENT_USERPOOL_ID = 'us-east-2_vpCRfIvXD'
PATIENT_APP_CLIENT_ID = '66fovpj4vcp9488lb9o7n3rv58'

ALLOWED_EXTENSIONS = ['.png', '.jpg', '.jpeg']

directory = os.getcwd()

logging.basicConfig(
    level=get_log_level(),  # DEBUG,
    format='%(asctime)s : %(levelname)s : %(funcName)-9s : %(message)s'
)
logger = logging.getLogger("fastapi")

app = FastAPI()
authenticate = JWTBearer(jwks)
app.include_router(router_covermymeds.router)
app.include_router(router_curexa.router)
app.include_router(router_drchrono.router)
app.include_router(router_freshdesk.router)
app.include_router(router_healthie.router)
app.include_router(router_mdi.router)
app.include_router(router_misc.router)
# , dependencies=[Depends(authenticate)],)
app.include_router(router_spreadsheet.router)
app.include_router(router_stripe.router)
app.include_router(router_user.router)
app.include_router(router_workpath.router)
app.include_router(router_health_check.router)
app.include_router(router_zendesk.router)
app.include_router(router_gogomeds.router)
app.include_router(router_humhealth.router)


@app.on_event("startup")
async def startup_event():
    if is_prod:
        logger.info("Running in 'PROD' mode.")
    else:
        logger.info("Running in 'TEST' mode.")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# TEST_STRIPE_API_KEY = "sk_test_51HDCXXDM8fNsPiHldRWovc44FxPnQuoDj1L3pH5CLG21tlAMtsK3vtpzo6OG6XEkrK8x2s0dLRh4sPkZh10k5eZb00M9vBi863"
stripe.api_key = STRIPE_API_KEY

PLAID_REDIRECT_URI = None


# client = plaid.Client(client_id=PLAID_CLIENT_ID,
#                       secret=PLAID_SECRET,
#                       environment=PLAID_ENV,
#                       api_version='2019-05-29')


class GetLocations(BaseModel):
    is_covid: bool = False
    is_insurance: bool = True
    test_name: str
    zip_code: str


def process_multi_select(k):
    try:
        final = ""
        for i in k[0]["options"]:
            final += ", " + i
        return final[2::]
    except:
        return ""


def calculate_order_amount(price):
    return price


@app.post("/create-payment-intent-testing")
async def create_payment_testing(request: Request):
    try:
        stripe.api_key = "sk_test_51HDCXXDM8fNsPiHldRWovc44FxPnQuoDj1L3pH5CLG21tlAMtsK3vtpzo6OG6XEkrK8x2s0dLRh4sPkZh10k5eZb00M9vBi863"

        # logger.debug(customer)
        data = await request.json()
        logger.debug(data)
        token_id = data["token_id"]
        # customer = stripe.Customer.create(source = token_id)
        amt = calculate_order_amount(data['price'])
        if data["email"] == "veergadodia24@gmail.com" or data["email"] == "nand.vinchhi@gmail.com" or data[
            "email"] == "frank@joinnextmed.com":
            logger.debug("YES")
            amt = 50

        if data["is_card"] == 1:

            intent = stripe.PaymentIntent.create(
                amount=amt,
                currency='usd',
                payment_method_types=['card'],
                receipt_email=data["email"]

            )
        elif data["is_card"] == 3:
            intent = stripe.PaymentIntent.create(
                payment_method_types=["klarna"],
                amount=amt,
                currency='usd',
            )
        else:
            intent = stripe.PaymentIntent.create(
                amount=amt,
                currency='usd',
                receipt_email=data["email"],
            )
        if token_id == "":
            return {
                'clientSecret': intent['client_secret'],
                'id': intent["id"]}
        else:
            return {
                'clientSecret': intent['client_secret'],
                'id': intent["id"]}

    except Exception as e:
        logger.exception(e)
        return {"error": str(e)}


@app.post("/create-payment-intent")
async def create_payment(request: Request):
    try:
        data = await request.json()
        logger.debug(data)
        token_id = data["token_id"]
        meta_data = data["metadata"]
        amt = calculate_order_amount(data['price'])
        if data["email"] == "veergadodia24@gmail.com" or data["email"] == "nand.vinchhi@gmail.com" or data[
            "email"] == "frank@joinnextmed.com":
            logger.debug("YES")
            amt = 50
        if data["is_card"] == 1:

            intent = stripe.PaymentIntent.create(
                amount=amt,
                currency='usd',
                payment_method_types=['card'],
                receipt_email=data["email"],
                metadata=meta_data

            )
        elif data["is_card"] == 3:
            intent = stripe.PaymentIntent.create(
                payment_method_types=["klarna"],
                amount=amt,
                currency='usd',
                metadata=meta_data
            )
        else:
            intent = stripe.PaymentIntent.create(
                amount=amt,
                currency='usd',
                receipt_email=data["email"],
                metadata=meta_data
            )
        if token_id == "":
            return {
                'clientSecret': intent['client_secret'],
                'id': intent["id"]}
        else:

            customer = stripe.Customer.create(source=token_id)
            return {
                'clientSecret': intent['client_secret'],
                'id': intent["id"], 'customer_id': customer["id"]}

    except Exception as e:
        logger.exception(e)
        return {"error": str(e)}


@app.post("/add")
async def add_endpoint(request: Request):
    try:
        data = await request.json()
        logger.debug(data)

        if "card_token" not in data:
            data["card_token"] = ""
        client = DBClient()
        xx, visit = client.add_patient(
            data["patient_id"],
            data["doctor_email"],
            data["visit_date"],
            data["visit_month"],
            data["visit_year"],
            data["visit_time"],
            data["patient_name"],
            data["email"],
            data["phone"],
            data["address"],
            data["notes"],
            data["dob_date"],
            data["dob_month"],
            data["dob_year"],
            data["sex"],
            data["insurance"],
            data["chief_complaint"],
            data["urine"],
            data["strep"],
            data["flu"],
            data["covid"],
            data["ecg"],
            data["viral"],
            data["spirometry"],
            data["blood"],
            data["current_date"],
            data["current_month"],
            data["current_year"],
            data["current_time"],
            data["doctor_name"],
            data["nurse_time"],
            data["nurse_email"],
            data["apartment_number"],
            data["houseMember"],
            data["mobile"],
            data["live"],
            data["houseMember"],
            data["requested_tests"],
            data["zip_code"],
            data["is_flight"],
            data["location"],
            data["payment_token"],
            data["requested_test_price"],
            data["card_token"])
        if xx != "failed":
            return {"status": "success", "mrn": xx, "visit": visit}
        else:
            return {"status": "no nurse", "error": "no nurses available"}
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@app.post('/consumer-add')
async def consumer_add_endpoint(request: Request):
    try:
        data = await request.json()
        logger.debug(data)
        logger.debug("adding patient with name " +
                     data["patient_name"] + " and email " + data["receipt_email"])

        if "doctor_email" not in data:
            data["doctor_email"] = "rob@joinnextmed.com"
        client = DBClient()
        xx = client.consumer_add_patient(
            data["visit_date"],
            data["visit_month"],
            data["visit_year"],
            data["patient_name"],
            data["phone"],
            data["address"],
            data["current_date"],
            data["current_month"],
            data["current_year"],
            data["current_time"],
            data["nurse_time"],
            data["nurse_email"],
            data["apartment_number"],
            "",
            data["receipt_email"],
            data["dob_month"],
            data["dob_date"],
            data["dob_year"],
            data["sex"],
            "",
            str(data["care_option_text"]),
            0,
            "2020-01-01 10:10:10",
            data["card_token"],
            data["payment_id"],
            data["zip_code"],
            0,
            data["is_hiv"],
            data["doctor_email"],
            data["location"],
            data["patient_symptoms"],
            data["axle_patient"],
            data["axle_address"],
            data["provider"],
            data["is_insurance"],
            data["lab_fax"],
            data["price"],
            data["test_type"],
            data["insuranceAmt"],
            data["insurance"],
            data["region_no"],
            data["customer_id"],
            data["patient_id_md"],
            data["patient_id"],
            data["path"],
            data["subscription_id"], data["subscription"], data["coupon"], data["total_price"], data["height"],
            data["weight"], data["airtable_id"]
        )

        if xx != "failed":
            return {"status": "success", "mrn": xx}
        else:
            return {"status": "no nurse", "error": "no nurses available"}
    except Exception as e:
        logger.exception("consumer add patient failed!", str(e))
        refund = stripe.Refund.create(
            payment_intent=data["payment_id"],
        )
        return {"status": "failed", "error": str(e)}


@app.post('/consumer-add-test')
async def consumer_add_endpoint(request: Request):
    try:
        data = await request.json()
        logger.debug(data)

        logger.info("adding patient with name " +
                    data["patient_name"] + " and email " + data["receipt_email"])

        if "doctor_email" in data:
            pass
        else:
            data["doctor_email"] = "rob@joinnextmed.com"
        client = DBClient()
        xx = client.consumer_add_patient_test(
            data["visit_date"],
            data["visit_month"],
            data["visit_year"],
            data["patient_name"],
            data["phone"],
            data["address"],
            data["current_date"],
            data["current_month"],
            data["current_year"],
            data["current_time"],
            data["nurse_time"],
            data["nurse_email"],
            data["apartment_number"],
            "",
            data["receipt_email"],
            data["dob_month"],
            data["dob_date"],
            data["dob_year"],
            data["sex"],
            "",
            data["cartName"],
            0,
            "2020-01-01 10:10:10",
            data["card_token"],
            data["payment_id"],
            data["zip_code"],
            0,
            data["is_hiv"],
            data["doctor_email"],
            data["location"],
            data["patient_symptoms"],
            data["axle_patient"],
            data["axle_address"],
            data["provider"],
            data["is_insurance"],
            data["lab_fax"],
            data["price"],
            data["insuranceAmt"],
            data["insurance"],
            data["region_no"],
            data["customer_id"],
            data["patient_id_md"],
            data["patient_id"])

        if xx != "failed":
            return {"status": "success", "mrn": xx}
        else:
            return {"status": "no nurse", "error": "no nurses available"}
    except Exception as e:
        logger.exception("consumer add patient failed!", str(e))
        refund = stripe.Refund.create(
            payment_intent=data["payment_id"],
        )

        return {"status": "failed", "error": str(e)}


@app.post('/charge-card')
async def charge_card_endpoint(request: Request):
    try:
        data = await request.json()
        logger.debug(data)
        client = DBClient()
        result = client.charge_card(data["customer_id"], int(data["price"]))
        return result
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@app.post('/get-axle-services')
async def axle_get_services_endpoints(request: Request):
    try:
        data = await request.json()
        logger.debug(data)
        zipcode = data["zipcode"]
        return get_axle_services(zipcode)
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@app.post('/get-axle-availability')
async def axle_get_availability_endpoints(request: Request):
    try:
        data = await request.json()
        logger.debug(data)
        zip_code = data["zipcode"]
        serviceId = data["serviceId"]
        payload = {
            "zip_code": str(zip_code),
            "service_ids": serviceId
        }
        return get_axle_availability(json.dumps(payload))
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@app.post('/create-axle-patient')
async def axle_create_patient_endpoints(request: Request):
    try:
        data = await request.json()
        logger.debug(data)
        return create_axle_patient(json.dumps(data))
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@app.post('/create-axle-address')
async def axle_create_address_endpoints(request: Request):
    try:
        data = await request.json()
        logger.debug(data)
        return create_axle_address(json.dumps(data))
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@app.post('/create-axle-visits')
async def axle_create_visits_endpoints(request: Request):
    try:
        data = await request.json()
        logger.debug(data)
        return create_axle_visits(json.dumps(data))
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@app.post('/refund')
async def refund_endpoint(request: Request):
    try:
        data = await request.json()
        logger.debug(data)
        client = DBClient()
        result = client.refund(data["mrn"], int(data["amount"]))
        return result
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@app.post('/cancel-visit')
async def cancel_visit_endpoint(request: Request):
    try:
        data = await request.json()
        logger.debug(data)
        client = DBClient()
        result = client.cancel_visit(data["mrn"], data["is_canceled"])
        return result
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@app.post('/set-on-the-way')
async def set_on_the_way_endpoint(request: Request):
    try:
        data = await request.json()
        logger.debug(data)
        client = DBClient()
        result = client.set_on_the_way(data["mrn"])
        return result
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@app.post('/set-positive')
async def set_positive_endpoint(request: Request):
    try:
        data = await request.json()
        logger.debug(data)
        client = DBClient()
        result = client.set_positive(data["mrn"], data["value"])
        return result
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@app.post('/edit-patient-profile')
async def edit_patient_profile_endpoint(request: Request):
    try:
        data = await request.json()
        logger.debug(data)
        client = DBClient()
        result = client.edit_patient_profile(data["mrn"], data["patient_name"], data["insurance"], data["pharmacy"],
                                             data["patient_address"], data["dob_date"], data["dob_month"],
                                             data["dob_year"], data["sex"], data['height'], data['weight'],
                                             data["current_medications"], data["allergies"], data['region_no'],
                                             data['patient_id_md'], data['patient_id'], data["is_user_verified"],
                                             data["mobile"], data["symptoms"], data["cartQuestion"], data["teleHealth"],
                                             data["primaryDoc"], data["insurance_payer_id"], data["is_pregnent"],
                                             data["isAppleUser"], data["img_doc"], data["agreement"],
                                             data["apartment_number"], data["address"], data["pharmacy_ins_patient"])

        return result
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@app.post('/edit-patient-profile-fake')
async def edit_patient_profile_endpoint(request: Request):
    try:
        data = await request.json()
        logger.debug(data)
        client = DBClient()
        result = client.edit_patient_profile_fake(
            data["mrn"], data["patient_name"], data["insurance"],
            data["pharmacy"], data["patient_address"], data["dob_date"], data["dob_month"],
            data["dob_year"], data["sex"], data['height'], data['weight'],
            data["current_medications"], data["allergies"], data['region_no'],
            data['patient_id_md'], data['patient_id'], data["is_user_verified"],
            data["mobile"], data["symptoms"], data["cartQuestion"],
            data["teleHealth"], data["primaryDoc"], data["insurance_payer_id"],
            data["is_pregnent"], data["isAppleUser"], data["img_doc"],
            data["agreement"], data["apartment_number"], data["address"],
            data["pharmacy_ins_patient"], data["insurance_card_photo"],
            data["rx_card_photo"]
        )

        return result
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@app.post('/edit-patient-address')
async def edit_patient_address_endpoint(request: Request):
    try:
        data = await request.json()
        logger.debug(data)
        client = DBClient()
        result = client.edit_patient_address(data["mrn"], data["address"])

        return result
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@app.post('/send-mail-subscription')
async def send_mail_subscription_endpoint(request: Request):
    try:
        data = await request.json()
        logger.debug(data)
        client = DBClient()
        result = client.send_mail_subscription(data["email"], data["type"])

        return result
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@app.post('/send-mail-order')
async def send_mail_order_endpoint(request: Request):
    try:
        data = await request.json()
        logger.debug(data)
        client = DBClient()
        result = client.send_mail_order_conformation(
            data["email"], data["name"], data["test"])

        return result
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@app.post('/update-email')
async def edit_email_patient_endpoint(request: Request):
    try:
        data = await request.json()
        logger.debug(data)
        client = DBClient()
        result = client.edit_email_patient(data["email"], data["old_email"])

        return result
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@app.post('/patient-download-req')
async def patient_download_req(request: Request):
    try:
        data = await request.json()
        logger.debug(data)
        client = DBClient()
        result = client.patient_download_req(data["email"])

        return result
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@app.post('/patient-canceled-visit')
async def patient_canceled_visit(request: Request):
    try:
        data = await request.json()
        logger.debug(data)
        email = data["email"]
        reason = data["reason"]
        cancel_reason = data["cancel_reason"]
        client = DBClient()
        result = client.patient_cancel_visit(email, reason, cancel_reason)
        return result
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@app.post('/approve-customer')
async def edit_email_patient_endpoint(request: Request):
    try:
        data = await request.json()
        logger.debug(data)
        client = DBClient()
        result = client.approve_patient(data["approve"], data["email"])

        return result
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@app.post('/update-place-order')
async def update_place_order_endpoint(request: Request):
    try:
        data = await request.json()
        logger.debug(data)
        client = DBClient()
        result = client.edit_place_order(
            data["subscription_id"], data["order_value"])

        return result
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@app.post('/update-subscriptionId')
async def edit_subscriptionId_patient_endpoint(request: Request):
    try:
        data = await request.json()
        logger.debug(data)
        client = DBClient()
        result = client.edit_subscriptionId_patient(data["email"])
        return result
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@app.post('/update-refill-subscriptionId')
async def edit_refill_subscriptionId_patient_endpoint(request: Request):
    try:
        data = await request.json()
        logger.debug(data)
        client = DBClient()
        result = client.edit_refill_subscriptionId_patient(
            data["email"], data["refill"], data["subscriptionId"])
        return result
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@app.post('/update-retest')
async def edit_retest_patient_endpoint(request: Request):
    try:
        data = await request.json()
        logger.debug(data)
        client = DBClient()
        result = client.edit_retest_patient(data["email"], data["retest"])
        return result
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@app.post('/update-insurance')
async def edit_insurance_patient_endpoint(request: Request):
    try:
        data = await request.json()
        logger.debug(data)
        client = DBClient()
        result = client.edit_insurance_patient(data["email"])
        return result
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@app.post('/change-payment-id-with-mrn')
async def change_payment_Id_with_mrn(request: Request):
    try:
        data = await request.json()
        subId = data["subcriptionId"]
        mrn = data["mrn"]
        logger.debug(data)
        client = DBClient()
        result = client.edit_payment_id_with_mrn(subId, mrn)
        return result
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@app.post('/change-membership-val')
async def change_membership_val(request: Request):
    try:
        data = await request.json()
        mrn = data["mrn"]
        logger.debug(data)
        client = DBClient()
        result = client.change_membership_val(mrn)
        return result
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@app.post('/update-dr-md-id')
async def edit_md_drchrono_id_patient_endpoint(request: Request):
    try:
        data = await request.json()
        logger.debug(data)
        client = DBClient()
        result = client.edit_md_drchrono_id_patient(
            data["mrn"], data["patient_md_id"], data["patient_drchrono_id"], data["md_case_id"]
        )

        return result
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@app.post('/update-email')
async def edit_email_patient_endpoint(request: Request):
    try:
        data = await request.json()
        logger.debug(data)
        client = DBClient()
        result = client.edit_email_patient(data["email"], data["old_email"])

        return result
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@app.post('/update-insurance-and-pharmacy')
async def set_positive_endpoint(request: Request):
    try:
        data = await request.json()
        logger.debug(data)
        client = DBClient()
        result = client.update_pharmacy_and_insurance(
            data["insurance"], data["pharmacy"], data["mrn"])
        return result
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@app.post('/add-to-mailchimp')
async def add_to_mailchimp_endpoint(request: Request):
    try:
        data = await request.json()
        logger.debug(data)

        result = add_to_list(data["email"])
        return result
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@app.post('/get-duration')
async def get_duration_endpoint(request: Request):
    data = await request.json()
    logger.debug(data)
    try:
        result = get_duration(data["source"], data["dest"])
        return result
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "data": "N/A"}


@app.post('/send-nurse-location')
async def send_nurse_location_endpoint(request: Request):
    data = await request.json()
    logger.debug(data)
    try:
        client = DBClient()
        result = client.send_nurse_location(
            data["nurse_email"], data["lat"], data["lon"])
        return result
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@app.post('/get-nurse-location')
async def get_nurse_location_endpoint(request: Request):
    data = await request.json()
    logger.debug(data)
    try:
        client = DBClient()
        result = client.get_nurse_location(data["mrn"])
        return result
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@app.post('/get-tracking-data')
async def get_tracking_data_endpoint(request: Request):
    data = await request.json()
    logger.debug(data)
    try:
        client = DBClient()
        result = client.get_tracking_data(data["mrn"], data["email"])
        return result
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@app.post('/get-patient-visits')
async def get_patient_visits_endpoint(request: Request):
    data = await request.json()
    logger.debug(data)
    try:
        client = DBClient()
        result = client.get_patient_visits(data["email"])
        return result
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@app.post('/get-visits')
async def get_visits_endpoint(request: Request):
    data = await request.json()
    logger.debug(data)
    try:
        client = DBClient()
        result = client.get_visits(data["email"])
        return result
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@app.post('/get-patient-subcription')
async def get_patient_subscription_endpoint(request: Request):
    data = await request.json()
    logger.debug(data)
    try:
        client = DBClient()
        result = client.get_patient_subscription(data["email"])
        return result
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@app.post('/verify-dob')
async def verify_dob_endpoint(request: Request):
    data = await request.json()
    logger.debug(data)
    try:
        client = DBClient()
        result = client.verify_dob(
            data["email"], data["dob_date"], data["dob_month"], data["dob_year"])

        return result
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@app.post('/apply-coupon')
async def apply_coupon_endpoint(request: Request):
    data = await request.json()
    logger.debug(data)
    try:
        client = DBClient()
        result = client.apply_coupon(data["coupon_id"], data["email"])

        return result
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@app.post('/verify-register')
async def verify_register_endpoint(request: Request):
    data = await request.json()
    logger.debug(data)
    try:
        result = confirm_signup(data["email"])
        return result
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@app.post('/create-cart')
async def create_cart_endpoint(request: Request):
    data = await request.json()
    logger.debug(data)
    try:
        client = DBClient()
        result = client.create_cart(data["email"])

        return result
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@app.post('/unsubscribe')
async def unsubscribe_endpoint(request: Request):
    data = await request.json()
    logger.debug(data)
    try:
        client = DBClient()
        result = client.unsubscribe(data["email"])

        return result
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@app.post('/send-result')
async def send_result_endpoint(request: Request):
    data = await request.json()
    logger.debug(data)
    try:
        client = DBClient()
        client.send_result(data["email"], data["visit_date"], data["visit_month"], data["visit_year"],
                           data["pdf"], data["name"], data["phone"], data["mrn"], data["file_name"], data["test_name"])
        return {"status": "success"}
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@app.post('/send-result-doctor')
async def send_result_doctor_endpoint(request: Request):
    data = await request.json()
    logger.debug(data)
    try:
        client = DBClient()
        client.send_result_doctor(data["result_id"], data["result"])
        return {"status": "success"}
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@app.post('/mark-doctor-complete')
async def mark_doctor_complete_endpoint(request: Request):
    data = await request.json()
    logger.debug(data)
    try:
        client = DBClient()
        client.mark_doctor_complete(
            data["mrn"], data["is_complete"], data["notes"])
        return {"status": "success"}
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@app.post('/approve-visit')
async def approve_visit_endpoint(request: Request):
    data = await request.json()
    logger.debug(data)
    try:
        client = DBClient()
        client.approve_visit(data["mrn"])
        return {"status": "success"}
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@app.post('/delete-result')
async def delete_result_endpoint(request: Request):
    data = await request.json()
    logger.debug(data)
    try:
        client = DBClient()
        client.delete_result(data["result_id"])
        return {"status": "success"}
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@app.post('/resend-confirmation')
async def resend_confirmation_endpoint(request: Request):
    data = await request.json()
    logger.debug(data)
    try:
        client = DBClient()
        client.send_patient_email(
            data["email"], data["name"], data["date"], data["time"])
        return {"status": "success"}
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@app.post('/resend-password')
async def resend_password_endpoint(request: Request):
    data = await request.json()
    logger.debug(data)
    try:
        resend_temp_password(data["email"], data["name"])
        return {"status": "success"}
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@app.post('/upload-rapid')
async def upload_rapid_endpoint(request: Request):
    data = await request.json()
    logger.debug(data)
    try:
        client = DBClient()
        data = client.upload_rapid(
            data["mrn"], data["doctor_result"], data["type"])
        return {"status": "success", "data": data}
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@app.post('/dashboard-finish-visit')
async def dashboard_finish_visit_endpoint(request: Request):
    data = await request.json()
    logger.debug(data)
    try:
        client = DBClient()

        if "value" not in data:
            data["value"] = 1
        client.dashboard_finish_visit(data["mrn"], data["value"])
        return {"status": "success"}
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@app.post('/mobile-finish-visit')
async def mobile_finish_visit_endpoint(request: Request):
    data = await request.json()
    logger.debug(data)

    try:
        if "complaint" not in data:
            data["complaint"] = ""

        if "number_of_lines" not in data:
            data["number_of_lines"] = 0
        client = DBClient()
        mrn = data["mrn"]

        client.mobile_finish_visit(data["mrn"], data["timestamp"], data["insurance_id"], data["insurance_name"],
                                   data["ssn"], data["passport_number"], data["complaint"], data["number_of_lines"])

        return {"status": "success"}
    except Exception as e:
        logger.debug("mobile finish visit failed", str(e))
        return {"status": "failed", "error": str(e)}


@app.get('/get-results')
async def get_results_endpoint(request: Request):
    data = request.query_params
    logger.debug(data)
    try:
        client = DBClient()
        results = client.get_results(data["email"], data["mrn"])
        return StreamingResponse(BytesIO(results[0]), media_type="application/pdf")
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@app.post('/get-autofill-data')
async def get_autofill_endpoint(request: Request):
    data = await request.json()
    logger.debug(data)
    try:
        client = DBClient()
        results = client.get_autofill_data(data["email"])

        return {"status": "success", "data": results}
    except Exception as e:
        logger.exception(e)

        final = {
            "name": "",
            "phone": "",
            "dob_date": -1,
            "dob_month": -1,
            "dob_year": -1,
            "apartment_number": "",
            "sex": "Select",
            "address": ""
        }
        return {"status": "failed", "data": final, "error": str(e)}


@app.post('/get-results-mrn')
async def get_results_for_mrn_endpoint(request: Request):
    data = await request.json()
    logger.debug(data)
    try:
        client = DBClient()
        results = client.get_results_for_mrn(data["mrn"])

        return {"status": "success", "data": results}
    except Exception as e:
        logger.exception(e)

        return {"status": "failed", "error": str(e)}


@app.post('/feedback')
async def feedback_endpoint(request: Request):
    data = await request.json()
    logger.debug(data)

    try:
        client = DBClient()
        result = client.give_feedback(data["mrn"], data["recommend"], data["alternative"], data["friendly"],
                                      data["convenient"], data["comments"], data["non_covid"], data["future_tests"])

        return result
    except Exception as e:
        logger.exception(e)

        return {"status": "failed", "error": str(e)}


@app.post('/send-feedback')
async def feedback_endpoint(request: Request):
    data = await request.json()
    logger.debug(data)

    try:
        client = DBClient()
        result = client.send_feedback(
            data["recommend"], data["alternative"], data["comments"], data["future_tests"], data["email"], data["name"],
            data["current_time"])

        return result
    except Exception as e:
        logger.exception(e)

        return {"status": "failed", "error": str(e)}


@app.post('/get-feedback')
async def get_feedback_endpoint(request: Request):
    data = await request.json()
    logger.debug(data)
    try:
        client = DBClient()
        result = client.get_feedback()
        return {"status": "success", "data": result}
    except Exception as e:
        logger.exception(e)

        return {"status": "failed", "error": str(e)}


@app.post('/get-patient-feedback')
async def get_patient_feedback_endpoint(request: Request):
    data = await request.json()
    logger.debug(data)
    try:
        client = DBClient()
        result = client.get_patient_feedback()
        return {"status": "success", "data": result}
    except Exception as e:
        logger.exception(e)

        return {"status": "failed", "error": str(e)}


@app.post('/upload-log')
async def upload_log_endpoint(request: Request):
    data = await request.json()
    logger.debug(data)
    try:
        client = DBClient()
        client.upload_log(data["mrn"], data["notes"],
                          data["time"], data["log_result"])
        return {"status": "success"}
    except Exception as e:
        logger.exception(e)

        return {"status": "failed", "error": str(e)}


@app.post('/get-patients')
async def get_patients_endpoint(request: Request):
    data = await request.json()
    logger.debug(data)

    try:
        client = DBClient()
        patients = client.get_patients(data["doctor_email"])

        return {"status": "success", "data": patients}
    except Exception as e:
        logger.exception(e)

        return {"status": "failed", "error": str(e)}


@app.post('/add-biller')
async def add_biller_endpoint(request: Request):
    data = await request.json()
    logger.debug(data)

    try:
        client = DBClient()
        client.add_biller(data["doctor_email"],
                          data["biller_email"], data["biller_name"])

        return {"status": "success"}
    except Exception as e:
        logger.exception(e)

        return {"status": "failed", "error": str(e)}


@app.post('/get-biller')
async def get_biller_endpoint(request: Request):
    data = await request.json()
    logger.debug(data)

    try:
        client = DBClient()
        data = client.get_biller(data["doctor_email"])

        return {"status": "success", "data": data}
    except Exception as e:
        logger.exception(e)

        return {"status": "failed", "error": str(e)}


@app.post('/patient-dropdown')
async def patient_dropdown_endpoint(request: Request):
    data = await request.json()
    logger.debug(data)

    try:
        client = DBClient()
        patients = client.patient_dropdown(data["doctor_email"])

        return {"status": "success", "data": patients}
    except Exception as e:
        logger.exception(e)

        return {"status": "failed", "error": str(e)}


@app.post('/delete-patient')
async def delete_patient_endpoint(request: Request):
    data = await request.json()
    logger.debug(data)

    try:
        client = DBClient()
        client.delete_patient(data["patient_id"])

        return {"status": "success"}
    except Exception as e:
        logger.exception(e)

        return {"status": "failed", "error": str(e)}


@app.post('/edit')
async def edit_endpoint(request: Request):
    data = await request.json()
    logger.debug(data)

    try:
        client = DBClient()
        client.edit_patient(
            data["mrn"],
            data["visit_date"],
            data["visit_month"],
            data["visit_year"],
            data["visit_time"],
            data["exact_nurse_time"],
            data["patient_name"],
            data["email"],
            data["phone"],
            data["address"],
            data["notes"],
            data["sex"],
            data["insurance"],
            data["chief_complaint"],
            data["urine"],
            data["strep"],
            data["flu"],
            data["covid"],
            data["ecg"],
            data["viral"],
            data["spirometry"],
            data["blood"],
            data["apartment_number"],
            data["doctor_name"],
            data["dob_date"],
            data["dob_month"],
            data["dob_year"],
            data["requested_tests"],
            data["zip_code"],
            data["nurse_email"],
            data["nurse_name"],
            data["is_flight"],
            data["region_no"],
        )
        return {"status": "success"}
    except Exception as e:
        logger.exception(e)

        return {"status": "failed", "error": str(e)}


@app.post('/get-valid-times')
async def valid_times_endpoint(request: Request):
    data = await request.json()
    logger.debug(data)

    try:
        client = DBClient()
        times = client.get_possible_times(
            data["current_date"], data["current_month"], data["current_year"],
            data["zip_code"], data["current_time"], data["doctor_email"],
            data["location"]
        )
        return {"status": "success", "data": times}
    except Exception as e:
        logger.exception(e)

        return {"status": "failed", "error": str(e)}


@app.post('/get-lab-locations')
async def lab_locations_endpoint(location_data: GetLocations):
    data = location_data.dict()
    logger.debug(data)
    try:
        client = DBClient()
        return client.get_lab_locations(
            data.get("zip_code"),
            data.get("is_covid"),
            data.get("is_insurance"),
            data.get("test_name")
        )
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@app.post('/add-doctor-result')
async def add_doctor_result_endpoint(request: Request):
    data = await request.json()
    logger.debug(data)

    try:
        client = DBClient()
        final = client.add_doctor_result(
            data["mrn"], data["test"], json.dumps(data["results"]))

        return final
    except Exception as e:
        logger.exception(e)

        return {"status": "failed", "error": str(e)}


@app.post('/edit-doctor-result')
async def edit_doctor_result_endpoint(request: Request):
    data = await request.json()
    logger.debug(data)

    try:
        client = DBClient()
        final = client.edit_doctor_result(
            data["result_id"], json.dumps(data["new_results"]))

        return final
    except Exception as e:
        logger.exception(e)

        return {"status": "failed", "error": str(e)}


@app.post('/delete-doctor-result')
async def delete_doctor_result_endpoint(request: Request):
    data = await request.json()
    logger.debug(data)

    try:
        client = DBClient()
        final = client.delete_doctor_result(data["result_id"])

        return final
    except Exception as e:
        logger.exception(e)

        return {"status": "failed", "error": str(e)}


@app.post('/get-doctor-result')
async def get_doctor_result_endpoint(request: Request):
    data = await request.json()
    logger.debug(data)

    try:
        client = DBClient()
        final = client.get_doctor_result(data["mrn"])

        return final
    except Exception as e:
        logger.exception(e)

        return {"status": "failed", "error": str(e)}


@app.post('/get-doctor-result-portal')
async def get_doctor_result_portal_endpoint(request: Request):
    data = await request.json()
    logger.debug(data)

    try:
        client = DBClient()
        final = client.get_doctor_result(data["mrn"])

        return final
    except Exception as e:
        logger.exception(e)

        return {"status": "failed", "error": str(e)}


@app.post('/push-notification')
async def push_notification_endpoint(request: Request):
    data = await request.json()
    logger.debug(data)

    try:
        client = DBClient()
        client.update_token(data["email"], data["token"])
        return {"status": "success"}
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@app.post('/send-message')
async def send_message_endpoint(request: Request):
    data = await request.json()
    logger.debug(data)

    try:
        client = DBClient()
        client.send_message(data["phone"])

        return {"status": "success"}
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@app.post('/add-to-emr')
async def add_to_emr_endpoint(request: Request):
    data = await request.json()
    logger.debug(data)

    try:
        client = DBClient()
        client.add_to_emr(data["mrn"])

        return {"status": "success"}
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@app.post('/update')
async def update_endpoint(request: Request):
    data = await request.json()
    logger.debug(data)

    try:
        client = DBClient()
        client.update_details(
            data["mrn"],
            data["height"],
            data["weight"],
            data["blood_pressure"],
            data["spo2"],
            data["heart_rate"],
            data["respiratory_rate"],
            data["temperature"],
            data["visit_duration"]
        )
        return {"status": "success"}
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@app.post('/update-tests')
async def update_tests_endpoint(request: Request):
    data = await request.json()
    logger.debug(data)

    try:
        client = DBClient()
        client.update_tests_algo(
            data["mrn"],
            data["strep"],
            data["flu"],
            data["covid"]
        )
        return {"status": "success"}
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@app.post('/update-schedule')
async def update_schedule_endpoint(request: Request):
    data = await request.json()
    logger.debug(data)

    try:
        client = DBClient()
        client.update_schedule(data["day"], data["email"], data["start"], data["end"])
        return {"status": "success"}
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@app.post('/update-admins')
async def update_admins_endpoint(request: Request):
    data = await request.json()
    logger.debug(data)

    try:
        client = DBClient()
        client.update_admins(data["email"])
        return {"status": "success"}
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@app.post('/register-nurse')
async def register_nurse_endpoint(request: Request):
    data = await request.json()
    logger.debug(data)

    try:
        client = DBClient()
        client.create_nurse(
            data["email"], data["name"], data["address"],
            data["phone"], data["doctor_email"], data["city"]
        )
        return {"status": "success"}
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@app.post('/update-complaint')
async def update_complaint_endpoint(request: Request):
    data = await request.json()
    logger.debug(data)
    try:
        client = DBClient()
        client.update_chief_complaint(data["mrn"], data["complaint"])
        return {"status": "success"}
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@app.post('/update-note-to-patient')
async def update_note_to_patient_endpoint(request: Request):
    data = await request.json()
    logger.debug(data)
    try:
        client = DBClient()
        client.update_note_to_patient(data["mrn"], data["notes"])
        return {"status": "success"}
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@app.post('/update-notes')
async def update_notes_endpoint(request: Request):
    data = await request.json()
    logger.debug(data)

    try:
        client = DBClient()
        client.update_physical_exam_notes(data["mrn"], data["notes"])
        return {"status": "success"}
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@app.post('/delete')
async def delete_endpoint(request: Request):
    data = await request.json()
    logger.debug(data)

    try:
        client = DBClient()
        client.delete_visit(data["mrn"])
        return {"status": "success"}
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@app.post('/validate-address')
async def validate_address_endpoint(request: Request):
    data = await request.json()
    logger.debug(data)
    try:
        is_valid = validate_address(data["address"])

        if is_valid == True:
            return {"status": "success", "data": "valid"}
        else:
            return {"status": "success", "data": "invalid"}
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "data": "invalid", "error": str(e)}


@app.post('/add-doctor')
async def add_doctor_endpoint(request: Request):
    data = await request.json()
    logger.debug(data)

    try:
        client = DBClient()
        client.add_doctor_name(data["practice_email"], data["name"], data["doctor_email"], data["type"])
        return {"status": "success"}
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@app.post('/delete-doctor')
async def delete_doctor_endpoint(request: Request):
    data = await request.json()
    logger.debug(data)

    try:
        client = DBClient()
        client.delete_doctor_name(data["practice_email"], data["doctor_email"])
        return {"status": "success"}
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@app.post('/get-doctors')
async def get_doctors_endpoint(request: Request):
    data = await request.json()
    logger.debug(data)

    try:
        client = DBClient()
        x, a, nurses = client.get_doctor_names(data["practice_email"], data["location"])
        return {"status": "success", "data": x, "table-data": a, "nurses": nurses}
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@app.post('/get-schedule')
async def get_schedule_endpoint(request: Request):
    data = await request.json()
    logger.debug(data)

    try:
        client = DBClient()
        x = client.get_schedule(data["date"], data["month"], data["year"], data["location"])
        return x
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@app.post('/verify-login')
async def verify_login_endpoint(request: Request):
    data = await request.json()
    logger.debug(data)

    try:
        client = DBClient()
        v = client.verify_login(data["email"])
        return v
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@app.post('/sendbird-login')
async def sendbird_login_endpoint(request: Request):
    data = await request.json()
    logger.debug(data)

    try:
        client = DBClient()
        v = client.sendbird_login(data["email"])
        return v
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@app.post('/get-table')
async def get_table_endpoint(request: Request):
    data = await request.json()
    logger.debug(data)
    try:
        client = DBClient()
        location = data.get("location")
        if location:
            x = client.get_table(data["doctor_email"], location)
        else:
            x = client.get_table(data["doctor_email"])
        return {"status": "success", "data": x}
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@app.post('/get-table-new')
async def get_table_endpoint(request: Request):
    data = await request.json()
    logger.debug(data)

    try:
        client = DBClient()
        x = client.get_table_test(data["doctor_email"], data["location"])
        return {"status": "success", "data": x}
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@app.post('/get-calendar')
async def get_calendar_endpoint(request: Request):
    data = await request.json()
    logger.debug(data)

    try:
        client = DBClient()
        x = client.get_calendar(data["doctor_email"], data["location"], data["start_date"],
                                data["start_month"], data["start_year"], data["end_date"], data["end_month"],
                                data["end_year"])
        return {"status": "success", "data": x}
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@app.post('/get-modal-data')
async def get_modal_data_endpoint(request: Request):
    data = await request.json()
    logger.debug(data)

    try:
        client = DBClient()
        x = client.get_modal_data(data["mrn"])
        return {"status": "success", "data": x}
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@app.post('/upload-images')
async def upload_images_endpoint(request: Request):
    type_to_path = {
        "left_ear": "/visual_diagnostics/tympanic_membranes/left/",
        "right_ear": "/visual_diagnostics/tympanic_membranes/right/",
        "throat": "/visual_diagnostics/orapharynx/",
        "skin": "/visual_diagnostics/dermatological/",
        "spirometry": "/spirometry/",
        "strep": "/strep/",
        "flu": "/flu/",
        "front_insurance": "/insurance/front/",
        "back_insurance": "/insurance/back/",
        "rapid": "/rapid/",
        "pcr": "/pcr/"
    }

    try:
        files = await request.form()
        # logger.debug(data)

        for i in files:
            file = files.get(i)
            mrn = file.filename.split(".")[0]
            path = type_to_path[i]
            push_image_to_s3(await file.read(), mrn + path)
        return {"status": "success"}
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


def get_as_base64(url):
    return base64.b64encode(requests.get(url).content)


def allowed_file(filename):
    ext = os.path.splitext(os.path.basename(filename))[1]
    return ext in ALLOWED_EXTENSIONS


@app.post('/upload-patient-image')
async def upload_patient_image_endpoint(file: UploadFile = File(...), email: str = Form(...)):
    try:
        logger.debug(file)
        filename = file.filename
        if allowed_file(filename) is False:
            raise Exception("Invalid file type.")
        contents = await file.read()

        if upload_image_to_s3(file.filename, contents) is False:
            raise Exception("Error uploading to S3. Try Again.")
        url = get_s3_file_url(filename)
        response = cognito_upload_image(email, url)
        base64_string = get_as_base64(url).decode("utf-8")
        if response:
            return {"status": "success", "url": base64_string}
        else:
            return {"status": "Failure"}
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@app.post('/get-nurse')
async def get_nurse_endpoint(request: Request):
    data = await request.json()
    logger.debug(data)

    try:
        client = DBClient()

        x = client.get_nurse_visits(
            data["nurse_email"],
            int(data["date"]),
            int(data["month"]),
            int(data["year"])
        )
        return {"status": "success", "data": x}
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@app.get('/get-dashboard')
async def get_dashboard_endpoint(request: Request):
    data = request.query_params
    logger.debug(data)
    try:
        mrn = data["mrn"]
        image_type = data["type"]
        if image_type == "left_ear":
            s3_data = get_data_from_s3(
                mrn + "/visual_diagnostics/tympanic_membranes/left")
        elif image_type == "right_ear":
            s3_data = get_data_from_s3(
                mrn + "/visual_diagnostics/tympanic_membranes/right")
        elif image_type == "left_eye":
            s3_data = get_data_from_s3(
                mrn + "/visual_diagnostics/ocular_images/left")
        elif image_type == "right_eye":
            s3_data = get_data_from_s3(
                mrn + "/visual_diagnostics/ocular_images/right")
        elif image_type == "throat":
            s3_data = get_data_from_s3(mrn + "/visual_diagnostics/orapharynx")
        elif image_type == "skin":
            s3_data = get_data_from_s3(mrn + "/visual_diagnostics/dermatological")
        elif image_type == "spirometry":
            s3_data = get_data_from_s3(mrn + "/spirometry")
        elif image_type == "ecg":
            s3_data = get_data_from_s3(mrn + "/electrocardiogram")
        elif image_type == "strep":
            s3_data = get_data_from_s3(mrn + "/strep")
        elif image_type == "flu":
            s3_data = get_data_from_s3(mrn + "/flu")
        elif image_type == "rapid":
            s3_data = get_data_from_s3(mrn + "/rapid")
        elif image_type == "pcr":
            s3_data = get_data_from_s3(mrn + "/pcr")
        else:
            s3_data = ["nothing.png", BytesIO(bytes("", 'utf-8'))]

        id_token = data["id_token"]
        verified_claims: dict = cognitojwt.decode(
            id_token,
            REGION,
            USERPOOL_ID,
            app_client_id=APP_CLIENT_ID,
            testmode=False
        )

        if 'sub' in verified_claims:
            return StreamingResponse(s3_data[1], media_type="image/png")
        else:
            s3_data = ["nothing.png", BytesIO(bytes("", 'utf-8'))]
            return StreamingResponse(s3_data[1], media_type="image/png")
    except Exception as e:
        logger.exception(e)
        s3_data = ["nothing.png", BytesIO(bytes("", 'utf-8'))]
        return StreamingResponse(s3_data[1], media_type="image/png")


@app.get('/get-label')
async def get_label_endpoint(request: Request):
    data = request.query_params
    logger.debug(data)
    try:
        mrn = data["mrn"]

        s3_data = get_data_from_s3(mrn + "/label")
        id_token = data["id_token"]
        verified_claims: dict = cognitojwt.decode(
            id_token,
            REGION,
            NURSE_USERPOOL_ID,
            app_client_id=NURSE_APP_CLIENT_ID,
            testmode=False
        )
        if 'sub' in verified_claims:
            return StreamingResponse(s3_data[1], media_type="application/pdf")
        else:
            s3_data = ["nothing.pdf", BytesIO(bytes("", 'utf-8'))]
            return StreamingResponse(s3_data[1], media_type="application/pdf")
    except Exception as e:
        logger.exception(e)
        s3_data = ["nothing.pdf", BytesIO(bytes("", 'utf-8'))]
        return StreamingResponse(s3_data[1], media_type="application/pdf")


@app.get('/get-pdf-result')
async def get_pdf_result_endpoint(request: Request):
    data = request.query_params
    logger.debug(data)
    try:

        result_id = data["result_id"]

        client = DBClient()
        s3_data = client.get_result_pdf(result_id)
        id_token = data["id_token"]
        try:
            verified_claims: dict = cognitojwt.decode(
                id_token,
                REGION,
                PATIENT_USERPOOL_ID,
                app_client_id=PATIENT_APP_CLIENT_ID,
                testmode=False
            )
        except:
            verified_claims = {}

        try:
            verified_claims1: dict = cognitojwt.decode(
                id_token,
                REGION,
                USERPOOL_ID,
                app_client_id=APP_CLIENT_ID,
                testmode=False
            )
        except:
            verified_claims1 = {}
        if 'sub' in verified_claims or 'sub' in verified_claims1:
            return StreamingResponse(BytesIO(s3_data[0]), media_type="application/pdf")
        else:
            s3_data = ["nothing.pdf", BytesIO(bytes("", 'utf-8'))]
            return StreamingResponse(s3_data[1], media_type="application/pdf")
    except Exception as e:
        logger.exception(e)
        s3_data = ["nothing.pdf", BytesIO(bytes("", 'utf-8'))]
        return StreamingResponse(s3_data[1], media_type="application/pdf")


@app.get('/get-fax-form')
async def get_fax_form_endpoint(request: Request):
    data = request.query_params
    try:

        mrn = data["mrn"]

        client = DBClient()

        id_token = data["id_token"]
        try:
            verified_claims: dict = cognitojwt.decode(
                id_token,
                REGION,
                PATIENT_USERPOOL_ID,
                app_client_id=PATIENT_APP_CLIENT_ID,
                testmode=False
            )
        except:
            verified_claims = {}

        try:
            verified_claims1: dict = cognitojwt.decode(
                id_token,
                REGION,
                USERPOOL_ID,
                app_client_id=APP_CLIENT_ID,
                testmode=False
            )
        except:
            verified_claims1 = {}
        if 'sub' in verified_claims or 'sub' in verified_claims1:
            s3_data = client.get_fax_form(mrn)

            return StreamingResponse(BytesIO(s3_data[0]), media_type="application/pdf")
        else:
            return {"status": "failed", "error": "Invalid Access token"}
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": "Invalid Access token"}


@app.post('/get-db-data')
async def get_edit_endpoint(request: Request):
    data = await request.json()
    logger.debug(data)

    try:
        client = DBClient()
        x = client.get_edit_data(data["mrn"], data["email"], data["location"])
        return {"status": "success", "data": x}
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@app.post('/get-family-members')
async def get_family_members_endpoint(request: Request):
    data = await request.json()
    logger.debug(data)

    try:
        client = DBClient()
        x = client.get_family_members(data["address"], data["name"])

        return {"status": "success", "data": x}
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@app.post('/get-pharmacies')
async def get_pharmacies_endpoints(request: Request):
    # 1 field pharmacy_name  must be present in data
    try:
        data = await request.json()
        logger.debug(data)
        pharmacy_name = data["pharmacy_name"]
        name = data["name"]
        if len(name) > 2:
            res = mdintegrations_chat.get_pharmacies1(pharmacy_name, name)
        else:
            res = mdintegrations_chat.get_pharmacies(pharmacy_name)
        logger.debug(res)
        if res is not None:
            return res
        raise Exception(res)

    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@app.post('/mdintegrations-add-file-to-case')
async def mdintegrations_add_file_to_case(request: Request):
    # two fields case_id & file_id must be present in data
    try:
        data = await request.json()
        logger.debug(data)
        res = mdintegrations_api.add_file_to_case(
            case_id=data.get('case_id'), file_id=data.get('file_id'))
        logger.debug(res)
        if 'file_id' in res:
            return res
        raise Exception(res)

    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@app.post('/mdintegrations-case-set-message-as-read')
async def mdintegrations_case_set_message_as_read_endpoint(request: Request):
    # two fields case_id & case_message_id must be present in data
    try:
        data = await request.json()
        logger.debug(data)
        res = mdintegrations_chat.set_message_as_read(case_id=data.get('case_id'),
                                                      case_message_id=data.get('case_message_id'))
        logger.debug(res)
        if 'case_message_id' in res:
            return res
        raise Exception(res)

    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@app.post('/mdintegrations-case-detach-message-file')
async def mdintegrations_case_detach_message_file_endpoint(request: Request):
    # 3 fields case_id, case_message_id & file_id must be present in data
    try:
        data = await request.json()
        logger.debug(data)
        res = mdintegrations_chat.detach_message_file(case_id=data.get('case_id'),
                                                      case_message_id=data.get(
                                                          'case_message_id'),
                                                      file_id=data.get('file_id'))
        logger.debug(res)
        if res is []:
            return res
        raise Exception(res)

    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@app.post('/mdintegrations-case-update-message')
async def mdintegrations_case_update_message_endpoint(request: Request):
    # 2 fields case_id, case_message_id  must be present in data
    try:
        data = await request.json()
        logger.debug(data)
        case_id = data.get('case_id')
        del data['case_id']
        case_message_id = data.get('case_message_id')
        del data['case_message_id']
        res = mdintegrations_chat.update_message(case_id=case_id,
                                                 case_message_id=case_message_id,
                                                 data=data)
        logger.debug(res)
        if 'case_message_id' in res:
            return res
        raise Exception(res)

    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@app.post('/stripe-list-subscriptions')
async def stripe_list_subscriptions(
        customer_id: Optional[str] = None,
        price: Optional[str] = None,
        status: Optional[str] = 'all',
        limit: Optional[int] = 10,
):
    try:
        response = stripe_api.list_subscriptions(
            customer_id, price, status, limit
        )
        logger.debug(response)

        if 'data' in response:
            return response.get('data')
        raise Exception(response)
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@app.post('/stripe-create-subscription')
async def stripe_create_subscription(item: stripe_api.Subscription):
    try:
        res = stripe_api.create_subscription(item)
        logger.debug(res)
        if 'id' in res:
            return res
        raise Exception(res)

    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@app.post('/stripe-get-subscription')
async def stripe_get_subscription(request: Request):
    try:
        data = await request.json()
        logger.debug(data)
        subscription_id = data["subscription_id"]
        response = stripe_api.get_subscription(subscription_id)
        logger.debug(response)

        if 'id' in response:
            return response
        raise Exception(response)
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@app.post('/stripe-get-subscription-db')
async def get_subscription_email_db(request: Request):
    try:
        data = await request.json()
        client = DBClient()
        logger.debug(data)
        email = data["email"]
        response = client.get_subscription_email(email)
        logger.debug(response)

        return response

    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@app.post('/stripe-cancel-subscription')
async def stripe_cancel_subscription(request: Request):
    try:

        data = await request.json()
        logger.debug(data)
        subscription_id = data["subscription_id"]
        response = stripe_api.cancel_subscription(subscription_id)
        logger.debug(response)

        if 'id' in response:
            return response
        raise Exception(response)
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@app.post('/stripe-get-product')
async def stripe_get_product(request: Request):
    try:

        data = await request.json()
        logger.debug(data)
        product_id = data["product_id"]
        response = stripe_api.get_product(product_id)
        logger.debug(response)

        if 'id' in response:
            return response
        raise Exception(response)
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@app.post('/get-payment-method')
async def get_payment_method(request: Request):
    # stripe.api_key="sk_test_51HDCXXDM8fNsPiHldRWovc44FxPnQuoDj1L3pH5CLG21tlAMtsK3vtpzo6OG6XEkrK8x2s0dLRh4sPkZh10k5eZb00M9vBi863"
    data = await request.json()
    logger.debug(data)
    try:
        customer = data["customer_id"]
        result = stripe.PaymentMethod.list(
            customer=customer,
            type="card"
        )
        if result:
            return result
        else:
            return "no data"
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@app.post('/subscription-create')
async def subscription_create(request: Request):
    # stripe.api_key="sk_test_51HDCXXDM8fNsPiHldRWovc44FxPnQuoDj1L3pH5CLG21tlAMtsK3vtpzo6OG6XEkrK8x2s0dLRh4sPkZh10k5eZb00M9vBi863"
    data = await request.json()
    logger.debug(data)
    try:
        customer = data["customer_id"]
        metadata = data["metadata"]
        items = data["items"]
        result = stripe.Subscription.create(
            customer=customer,
            items=items,
            metadata=metadata
        )
        if result:
            return {"status": "subscription created successfully", "result": result}
        else:
            return {"status": "failed", "error": "no subcription created"}
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@app.post('/subscription-create-trial')
async def subscription_create_trial(request: Request):
    # stripe.api_key="sk_test_51HDCXXDM8fNsPiHldRWovc44FxPnQuoDj1L3pH5CLG21tlAMtsK3vtpzo6OG6XEkrK8x2s0dLRh4sPkZh10k5eZb00M9vBi863"
    data = await request.json()
    logger.debug(data)
    try:
        if 'token_id' in data:
            customer = stripe.Customer.create(source=data["token_id"])
        else:
            customer = data["customer_id"]

        items = data["items"]
        trial = data["trial"]
        result = stripe.Subscription.create(
            customer=customer,
            items=items,
            trial_end=trial
        )
        if result:
            return {"status": "success", "message": "Subscription creates successfully",
                    "subscriptionId": result["id"]}
        else:
            return {"status": "failed", "error": "no subcription created"}
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@app.post('/subscription-weigthloss-payment')
async def subscription_create_trial(request: Request):
    data = await request.json()
    subscription_data = data["subscription"]
    one_time = data["one_time"]
    logger.debug(data)
    try:
        customer = subscription_data["customer_id"]
        items = subscription_data["items"]
        trial = subscription_data["trial"]
        payment_Id = one_time["payment_id"]
        metaData = one_time["metadata"]
        amount = one_time["amount"]
        result = stripe.PaymentIntent.create(
            amount=amount,
            currency='usd',
            customer=customer,
            payment_method=payment_Id,
            off_session=True,
            confirm=True,
            metadata=metaData
        )
        if result:
            sub = stripe.Subscription.create(
                customer=customer,
                items=items,
                trial_end=trial
            )
            if sub:
                return {"status": "success", "message": "Subscription creates successfully",
                        "subscriptionId": sub["id"]}
            else:
                return {"status": "failed", "error": "no subcription created"}
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@app.post('/post-payment-charge')
async def get_payment_method(request: Request):
    # stripe.api_key="sk_test_51HDCXXDM8fNsPiHldRWovc44FxPnQuoDj1L3pH5CLG21tlAMtsK3vtpzo6OG6XEkrK8x2s0dLRh4sPkZh10k5eZb00M9vBi863"
    data = await request.json()
    logger.debug(data)
    try:
        customer_id = data["customer_id"]
        payment_Id = data.get("payment_id")
        metaData = data["metadata"]
        amount = data["amount"]
        result = stripe.PaymentIntent.create(
            amount=amount,
            currency='usd',
            customer=customer_id,
            payment_method=payment_Id,
            off_session=True,
            confirm=True,
            metadata=metaData
        )
        if result:
            return result
        else:
            return "no data"
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@app.post('/create-payment-subcription')
async def get_payment_method(request: Request):
    try:
        data = await request.json()
        logger.debug(data)
        metadata = data["metadata"]
        token_id = data["token_id"]
        customerId = data["customerId"]
        items = data["items"]
        coupon = data["coupon"]
        if customerId == "new":
            customer = stripe.Customer.create(source=token_id)
            if coupon == "no":
                subscription = stripe.Subscription.create(
                    customer=customer["id"],
                    items=items,
                    metadata=metadata
                )
                if subscription and subscription["id"]:
                    return {"status": "success", "message": "Subscription creates successfully",
                            "subscriptionId": subscription["id"], customerId: customer["id"]}
                else:
                    return {"status": "failed", "message": "subscription not created"}
            else:
                subscription = stripe.Subscription.create(
                    customer=customer["id"],
                    items=items,
                    coupon=coupon,
                    metadata=metadata
                )
                if subscription and subscription["id"]:
                    return {"status": "success", "message": "Subscription creates successfully",
                            "subscriptionId": subscription["id"], customerId: customer["id"]}
                else:
                    return {"status": "failed", "message": "subscription not created"}
        else:
            if coupon == "no":
                subscription = stripe.Subscription.create(
                    customer=customerId,
                    items=items,
                    metadata=metadata
                )
                if subscription and subscription["id"]:
                    return {"status": "success", "message": "Subscription creates successfully",
                            "subscriptionId": subscription["id"]}
                else:
                    return {"status": "failed", "message": "subscription not created"}
            else:
                subscription = stripe.Subscription.create(
                    customer=customerId,
                    items=items,
                    coupon=coupon,
                    metadata=metadata
                )
                if subscription and subscription["id"]:
                    return {"status": "success", "message": "Subscription creates successfully",
                            "subscriptionId": subscription["id"]}
                else:
                    return {"status": "failed", "message": "subscription not created"}

    except Exception as e:
        logger.exception(e)
        return {"error": str(e)}


@app.post('/create-payment-subcription-testing')
async def get_payment_method(request: Request):
    try:
        data = await request.json()
        logger.debug(data)
        token_id = data["token_id"]
        metadata = data["metadata"]
        customerId = data["customerId"]
        items = data["items"]
        coupon = data["coupon"]
        if customerId == "new":
            email=data["email"]
            customer = stripe.Customer.create(source=token_id,email=email)
            if coupon == "no":
                subscription = stripe.Subscription.create(
                    customer=customer["id"],
                    items=items,
                    metadata=metadata
                )
                if subscription:
                    return {"subscription": subscription, customerId: customer["id"]}
                else:
                    return {"status": "failed", "message": "subscription not created"}
            else:
                subscription = stripe.Subscription.create(
                    customer=customer["id"],
                    items=items,
                    coupon=coupon,
                    metadata=metadata
                )
                if subscription:
                    return {"subscription": subscription, customerId: customer["id"]}
                else:
                    return {"status": "failed", "message": "subscription not created"}
        else:
            if coupon == "no":
                subscription = stripe.Subscription.create(
                    customer=customerId,
                    items=items,
                    metadata=metadata
                )
                if subscription:
                    return {"subscription": subscription}
                else:
                    return {"status": "failed", "message": "subscription not created"}
            else:
                subscription = stripe.Subscription.create(
                    customer=customerId,
                    items=items,
                    coupon=coupon,
                    metadata=metadata
                )
                if subscription:
                    return {"subscription": subscription}
                else:
                    return {"status": "failed", "message": "subscription not created"}

    except Exception as e:
        logger.exception(e)
        return {"error": str(e)}


@app.post('/add-subscription')
async def add_subscription(request: Request):
    try:
        data = await request.json()
        logger.debug(data)
        client = DBClient()
        xx = client.add_subscription_patient(
            data["subscriptionId"],
            data["email"],
            data["testName"])

        if xx:
            return {"status": "success", "subscription": xx}
        else:
            return {"status": "failed", "error": "no subscription created"}
    except Exception as e:
        return {"status": "failed", "error": str(e)}


@app.post('/add-subscription-prescriptions')
async def add_subscription_prescriptions(request: Request):
    try:
        data = await request.json()
        logger.debug(data)
        client = DBClient()
        xx = client.add_subscription_patient_prescriptions(
            data["subscriptionId"],
            data["email"],
            data["testName"])

        if xx:
            return {"status": "success", "subscription": xx}
        else:
            return {"status": "failed", "error": "no subscription created"}
    except Exception as e:
        return {"status": "failed", "error": str(e)}


@app.post('/get-invoice')
async def get_invoice(request: Request):
    # stripe.api_key="sk_test_51HDCXXDM8fNsPiHldRWovc44FxPnQuoDj1L3pH5CLG21tlAMtsK3vtpzo6OG6XEkrK8x2s0dLRh4sPkZh10k5eZb00M9vBi863"
    data = await request.json()
    logger.debug(data)
    try:
        invoice_id = data["invoice_id"]
        result = stripe.Invoice.retrieve(
            invoice_id
        )
        if result:
            return result
        else:
            return "no data"
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@app.post('/create-customer-applepay')
async def create_customer_applepay(request: Request):
    data = await request.json()
    logger.debug(data)
    try:
        payment_id = data["payment_id"]
        email = data["email"]
        customer = stripe.Customer.create(email=email)
        customerVal = stripe.PaymentMethod.attach(
            payment_id,
            customer=customer["id"],
        )
        customerModify = stripe.Customer.modify(
            customer["id"],
            invoice_settings={"default_payment_method": payment_id}
        )

        if customerVal:
            return customerVal
        else:
            return "no data"
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@app.post('/retrive-customer-subscription')
async def retrive_customer_subscription(request: Request):
    data = await request.json()
    logger.debug(data)
    try:
        subscription_id = data["subscriptionId"]
        subscription = stripe.Subscription.retrieve(subscription_id)
        if subscription:
            return subscription
        else:
            return {"status": "false", "message": "no data"}
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@app.post('/update-customer-method')
async def update_customer_method(request: Request):
    data = await request.json()
    logger.debug(data)
    token = data["token"]
    customer_id = data["customer_id"]
    try:
        add_card = stripe.Customer.modify(customer_id, source=token)
        if add_card["id"]:
            return {"status": "success", "data": add_card}
        else:
            return {"status": "failed", "error": "Bad request not updated"}
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@app.post('/create-credit-customer')
async def update_customer_method(request: Request):
    data = await request.json()
    logger.debug(data)
    amount = data["amount"]
    customer_id = data["customer_id"]
    try:
        credit = stripe.Customer.create_balance_transaction(
            customer_id,
            amount=amount,
            currency='usd', )
        if credit["id"]:
            return {"status": "success", "data": credit}
        else:
            return {"status": "failed", "error": "Bad request not updated"}
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@app.post('/get-card-lists')
async def retrive_customer_subscription(request: Request):
    data = await request.json()
    logger.debug(data)
    customer_id = data["customer_id"]
    try:
        card_id = stripe.Customer.retrieve(customer_id)
        if card_id:
            list_card = stripe.Customer.retrieve_source(customer_id, card_id["default_source"])
            return {"status": "success", "data": list_card}
        else:
            return {"status": "failed", "error": "Bad request"}
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@app.post('/update-customer-subscription')
async def update_customer_subscription(request: Request):
    data = await request.json()
    logger.debug(data)
    try:
        subscription_id = data["subscriptionId"]
        price_key = data["price_key"]
        subscription = stripe.Subscription.retrieve(subscription_id)
        update_subscription = stripe.Subscription.modify(
            subscription.id,
            cancel_at_period_end=False,
            proration_behavior='always_invoice',
            items=[{
                'id': subscription['items']['data'][0].id,
                'price': price_key,
            }]
        )
        if update_subscription:
            return update_subscription
        else:
            return {"status": "false", "message": "no data"}
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}

users = []

@app.post("/user/signup", tags=["user"])
async def create_user(user: UserSchema = Body(...)):
    users.append(user) # replace with db call, making sure to hash the password first
    return signJWT(user.username)

def check_user(data: UserLoginSchema):
    for user in users:
        print("user", user)
        if user.username == data.username and user.password == data.password:
            return True
    return False

@app.post("/user/login", tags=["user"])
async def user_login(user: UserLoginSchema = Body(...)):
    if check_user(user):
        return signJWT(user.username)
    return {
        "error": "Wrong login details!"
    }
