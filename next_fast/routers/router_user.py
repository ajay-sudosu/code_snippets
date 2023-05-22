from distutils.command.clean import clean
import secrets
from fastapi import APIRouter, Depends, Request , BackgroundTasks, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import logging
from auth.jwk_model import get_current_user
from auth.cognito import cognito_change_email
from db_client import DBClient
from auth.cognito import cognito_signup_apple_pay_user, cognito_signup_patient
from mdintegrations import mdintegrations_api, mdintegrations_chat, MDintegrationsPatient, \
    WEBHOOK_SECRET, WEBHOOK_TOKEN, MDintegrationsPatientPharmacy, MDICreateHerpesCase, MDICasePrescription, \
    MDIPatientId, MDICreatePrescriptionsCase, MDICasePrescriptionUpdate, MDISearchPharmacy
from stripe_api import update_subscription
from drchrono import drchrono, DrChronoInsuranceQuery, DrChronoLabOrder
from bg_task.mdi_tasks import mdi_attach_pharmacy_to_patient, mdi_webhook_handle
import stripe
from pydantic import BaseModel

logger = logging.getLogger("fastapi")
router = APIRouter()

security = HTTPBasic()
STRIPE_API_KEY = "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"
stripe.api_key =  STRIPE_API_KEY


def get_current_username(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, "admin")
    correct_password = secrets.compare_digest(credentials.password, "_Adm!n@nextmed@123_")
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


@router.get("/test", tags=["user"])
async def test(username: str = Depends(get_current_user)):
    return {"username": username}


@router.post('/get-patient-info', tags=["user"])
async def get_patient_info_endpoint(request: Request, email: str = Depends(get_current_user)):
    try:
        data = await request.json()
        logger.debug(data)
        client = DBClient()
        if email is None:
            result = client.get_patient_info(data.get("email"))
        else:
            result = client.get_patient_info(email)

        return result
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@router.post('/get-patient-profile', tags=["user"])
async def get_patient_profile_endpoint(request: Request):
    try:
        data = await request.json()
        logger.debug(data)
        client = DBClient()
        email = data["email"]
        if email is None:
            result = client.get_patient_profile(data.get("email"))
        else:
            result = client.get_patient_profile(email)

        return result
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@router.post('/register', tags=["user"])
async def register_endpoint(request: Request):
    data = await request.json()
    logger.debug(data)
    email_id = data.get('email')
    phone = data.get('phone')
    try:
        if data.get('userPayType') == "applePay":
            logger.debug(f"{email_id} is applePay.")
            result = cognito_signup_apple_pay_user(email_id, "", phone)
        else:
            password = data.get('password')
            result = cognito_signup_patient(email_id, password, phone)
        return {"status": "success", "temp_password": result}
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@router.post('/add-new-patient', tags=["user"])
async def consumer_add_endpoint(request: Request):
    data = await request.json()
    logger.debug(data)
    user_data = data["user_data"]
    consumer_data = data["consumer_data"]
    email_id = user_data['email']
    phone = user_data['phone']
    password = user_data['password']
    payment_id = consumer_data[0]["payment_id"]
    client = DBClient()
    try:
        result = cognito_signup_patient(email_id, password, phone)  
        if result :    
           for patient in consumer_data:
               xx  =  client.consumer_add_patient(
            patient["visit_date"],
            patient["visit_month"],
            patient["visit_year"],
            patient["patient_name"],
            patient["phone"],
            patient["address"],
            patient["current_date"],
            patient["current_month"],
            patient["current_year"],
            patient["current_time"],
            patient["nurse_time"],
            patient["nurse_email"],
            patient["apartment_number"],
            "",
            patient["receipt_email"],
            patient["dob_month"],
            patient["dob_date"],
            patient["dob_year"],
            patient["sex"],
            "",
            str(patient["care_option_text"]),
            0,
            "2020-01-01 10:10:10",
            patient["card_token"],
            patient["payment_id"],
            patient["zip_code"],
            0,
            patient["is_hiv"],
            patient["doctor_email"],
            patient["location"],
            patient["patient_symptoms"],
            patient["axle_patient"],
            patient["axle_address"],
            patient["provider"],
            patient["is_insurance"],
            patient["lab_fax"],
            patient["price"],
            patient["test_type"],
            patient["insuranceAmt"],
            patient["insurance"],
            patient["region_no"],
            patient["customer_id"],
            patient["patient_id_md"],
            patient["patient_id"],
            patient["path"],
            patient["subscription_id"], 
            patient["subscription"],
            patient["coupon"],
            patient["total_price"],
            patient["height"],
            patient["weight"],
            patient["airtable_id"])
        if xx != "failed":
                return {"status": "success", "mrn": xx}
        else:
            return {"status": "no nurse", "error": "no nurses available"}       
               
    except Exception as e:
        refund = stripe.Refund.create(
            payment_intent=payment_id),

        return {"status": "failed", "error": str(e)}


def _update_stripe_subscription_(subscription_id, patient_id_md, case_id, refills_ordered=1):
    """Update stripe subscription for refill count & new case id"""
    try:
        if subscription_id is None:
            logger.warning(f"Not Updating stripe subscription: {subscription_id}")
            return

        logger.info(f"Updating stripe subscription: {subscription_id} with "
                    f"patient_id_md: {patient_id_md},"
                    f"case_id: {case_id} & refills_ordered: {refills_ordered}")
        metadata = {
            "patient_id_md": patient_id_md,
            "case_id": case_id,
            "refills_ordered": refills_ordered
        }
        update_subscription(subscription_id, metadata=metadata)

    except Exception as e:
        logger.exception(e)


def add_pharmacy(data, background_tasks:BackgroundTasks):
    """Update stripe subscription for refill count & new case id"""
    try:
        background_tasks.add_task(mdi_attach_pharmacy_to_patient, data)
        
        return {"status": "success", "message": "Pharmacy being attached in background."}

    except Exception as e:
        logger.exception(e)


@router.post('/update-patient-data', tags=["user"])
async def update_patient_data_endpoint(request: Request):
    data = await request.json()
    email_id = data.get('email')
    case_data = data["case_data"]
    dr_chrono_data = data["dr_chrono_data"]
    dr_chrono_task_data = data["dr_chrono_task_data"]
    dr_chrono_appointment_data = data["dr_chrono_appointment_data"]
    md_data = data["md_data"]
    profile_data=data["profile_data"]
    ins_data = data["ins_data"]
    client = DBClient()
    case_id = ""
    count = 0
    patient_md = ""
    patient_dr = ""
    try:
        if count == 0:
            logger.debug(data)
            md_patient = mdintegrations_api.create_patient(md_data)
            logger.debug(md_patient)
            if 'patient_id' in md_patient:
                subscription_id = None
                patient_md = md_patient["patient_id"]
                if 'subscription_id' in case_data:
                    subscription_id = case_data['subscription_id']
                    del case_data['subscription_id']
                case_data["patient_id"]= md_patient["patient_id"]    
                create_md_case = mdintegrations_api.create_case(case_data)
                logger.debug(create_md_case)
                if 'case_id' in create_md_case:
                    case_id = create_md_case["case_id"]
                    _update_stripe_subscription_(subscription_id, md_patient['patient_id'], create_md_case['case_id'], refills_ordered=1)
            drchorno_patient = drchrono.patient_create(dr_chrono_data)
            if 'id' in drchorno_patient:
                patient_dr = drchorno_patient["id"]
                dr_chrono_appointment_data["patient"] = drchorno_patient["id"]
                res_apt = drchrono.appointment_create(dr_chrono_appointment_data)
                ins_data["patient_id"]=drchorno_patient["id"]
                dr_chrono_task_data["associated_items"] = [{"type":"Patient","value":drchorno_patient["id"]}]    
                task_res = drchrono.tasks_create(dr_chrono_task_data)
                update_ins = drchrono.patient_partial_update(ins_data)
            result = client.edit_patient_profile_new(profile_data["mrn"], profile_data["patient_name"], profile_data["insurance"], profile_data["pharmacy"], profile_data["patient_address"], profile_data["dob_date"], profile_data["dob_month"], profile_data["dob_year"], profile_data["sex"], profile_data['height'], profile_data['weight'], profile_data["current_medications"], profile_data["allergies"], profile_data['region_no'], patient_md, patient_dr, profile_data["is_user_verified"], profile_data["mobile"], profile_data["symptoms"], profile_data["cartQuestion"], profile_data["teleHealth"], profile_data["primaryDoc"], profile_data["insurance_payer_id"], profile_data["is_pregnent"], profile_data["isAppleUser"], profile_data["img_doc"], profile_data["agreement"], profile_data["apartment_number"], profile_data["address"],profile_data["pharmacy_ins_patient"],case_id)
            count = count + 1
            return result        
        
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@router.post('/add-case-to-support', tags=["user"])
async def add_case_to_support_endpoint(request: Request):
    data = await request.json()
    case_id = data["case_id"]
    try:
       case = mdintegrations_api.add_case_to_support(case_id)
       
       return case 
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


class UpdateEmail(BaseModel):
    current_email: str
    new_email: str


@router.post('/change-user-email', tags=["user"])
async def change_user_email_endpoint(data: UpdateEmail, username: str = Depends(get_current_username)):
    try:
        if username != 'admin':
            return {}
        logger.debug(data.dict())
        cognito_change_email(data.current_email, data.new_email)
        db = DBClient()
        db.update_visits_email(data.current_email, data.new_email)
        try:
            patient_list_res = drchrono.patients_list({"email": data.current_email})
            patient_list = patient_list_res.get('results', [])
            if len(patient_list) > 0:
                logger.info(
                    f"changing {data.current_email} to {data.new_email} in drchrono for id:{patient_list[0]['id']}...")
                drchrono.patient_partial_update({"email": data.new_email, "patient_id": patient_list[0]["id"]})
        except Exception as e:
            logger.exception(e)
        try:
            params = {
                "search": data.current_email
            }
            patient_list_res = mdintegrations_api.search_patient(params)
            for patient in patient_list_res:
                if patient.get("email") != data.current_email:
                    continue
                patient_id = patient.get("patient_id")
                logger.info(
                    f"changing {data.current_email} to {data.new_email} in MDI for id:{patient_id}...")
                data = {
                        "email": data.new_email
                    }
                res = mdintegrations_api.update_patient(patient_id, data)
                break
        except Exception as e:
            logger.exception(e)

        return {"status": "success"}
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@router.post('/update-ishealthie', tags=["user"])
async def update_healthie_endpoint(request: Request):
    data = await request.json()
    mrn = data["mrn"]
    is_healthie =data["is_healthie"]   
    client = DBClient()
    try:
       res = client.update_is_healthie(mrn,is_healthie)
       return res 
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}
