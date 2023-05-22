from auth.cognito import create_user_on_cognito
from config import STRIPE_API_KEY
from db_client import DBClient
import logging
from datetime import date, datetime
import stripe

logger = logging.getLogger("fastapi")
stripe.api_key = STRIPE_API_KEY


def create_account_from_amazon_seller():
    """
    Get unprocessed rows from amazon_seller
    and insert into visits
    """
    try:
        todays_date = date.today()
        start_datetime = "2020/01/01 10:10:10"
        flight_time = datetime.strptime(start_datetime, '%Y/%m/%d %H:%M:%S')
        client = DBClient()
        all_data = client.get_amazon_seller_queues()
        for data in all_data:
            res = None
            customer = None
            try:
                res = create_user_on_cognito(data.get('email'))
            except Exception as e:
                logger.exception("create_user_on_cognito => " + str(e))
            try:
                customer = stripe.Customer.create(
                    email=data.get('email')
                )
            except Exception as e:
                logger.exception("create_user_on_cognito => " + str(e))
            if res and customer:
                mrn = client.consumer_add_patient(
                    visit_date=todays_date.day,
                    visit_month=todays_date.month,
                    visit_year=todays_date.year,
                    patient_name="Test Test",
                    phone=data.get('phone'),
                    address="lab_test_location",
                    current_date=todays_date.day,
                    current_month=todays_date.month,
                    current_year=todays_date.year,
                    current_time=927,
                    nurse_time=1027,
                    nurse_email="rob@joinnextmed.com",
                    apartment_number="",
                    consumer_notes="",
                    receipt_email=data.get('email'),
                    dob_month=1,
                    dob_date=1,
                    dob_year=2000,
                    sex=0,
                    race="",
                    options="GLP-1 Weight Loss Program",
                    is_family=0,
                    flight_time=flight_time,
                    card_token=None,
                    payment_id="test_payment_id",
                    zip_code="",
                    is_flight=0,
                    is_hiv=1,
                    doctor_email="rob@joinnextmed.com",
                    location="new york",
                    patient_symptoms="",
                    axle_patient="",
                    axle_address="",
                    provider=None,
                    is_insurance=1,
                    lab_fax="",
                    price=99,
                    test_type="",
                    insuranceAmt=0,
                    insurance="Yes",
                    region_no="",
                    customer_id=customer["id"],
                    patient_id_md="",
                    patient_id="",
                    path="",
                    subscription_id="",
                    subscription="",
                    coupon="NEXT50!",
                    total_price=50,
                    height=0,
                    weight=0,
                    airtable_id="",
                    consent=1,
                    order_test_id="B2e**XH4twx4",
                    total_discount=0,
                    referrer="")
                if mrn:
                    client.update_amazon_seller_processed(
                        data.get('id'), data.get('product_name'),
                        mrn, data.get("product_quantity"), data.get("address")
                    )
    except Exception as e:
        logger.exception("create_account_from_amazon_seller => " + str(e))


if __name__ == '__main__':
    create_account_from_amazon_seller()
