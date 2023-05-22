from locale import currency
import logging
from fastapi import APIRouter, Request, status, Response, BackgroundTasks, Depends
import stripe
from typing import Optional
from pydantic import BaseModel
from config import STRIPE_API_KEY, is_prod
from bg_task.stripe_tasks import stripe_webhook_handle
from db_client import DBClient
from stripe_api import retrieve_customer_cards, update_customer_default_card, create_customer_card_on_stripe, \
    retrieve_customer_card_by_token
from sqlalchemy.orm import Session
from database.db import get_db
from database.crud import StripePauseSubscriptionCrud

logger = logging.getLogger("fastapi")
router = APIRouter()

stripe.api_key = STRIPE_API_KEY


class StripeRefund(BaseModel):
    charge: Optional[str]
    amount: Optional[int]
    metadata: Optional[dict]
    payment_intent: Optional[str]
    reason: Optional[str]
    # refund_application_fee: Optional[bool]
    # reverse_transfer:


class Invoice(BaseModel):
    customer: Optional[str]
    price: Optional[int]
    # refund_application_fee: Optional[bool]
    # reverse_transfer:


class UpdateSource(BaseModel):
    mrn: str
    token: str


@router.get('/stripe-fetch-refund', tags=["stripe"])
async def stripe_fetch_refund_endpoint(refund_id: str):
    """Retrieves the details of an existing refund."""
    try:
        logger.info("API: stripe-fetch-refund")
        logger.debug("fetching refund details: ", refund_id)
        response = stripe.Refund.retrieve(refund_id)
        return response

    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@router.post('/stripe-fetch-all', tags=["stripe"])
async def stripe_fetch_all_endpoint(request: Request):
    try:
        logger.info("API: stripe-fetch-all")
        data = await request.json()
        response = stripe.Invoice.list(customer=data["customer_id"])
        return response

    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@router.post('/create-stripe-card', tags=["stripe"])
async def create_stripe_card_endpoint(request: Request):
    try:
        logger.info("API: create-stripe-card")
        data = await request.json()
        customer_id = data["customer_id"]
        token = data["token"]
        response = stripe.Customer.create_source(customer_id, source=token)
        return response

    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@router.post('/create-new-card', tags=["stripe"])
async def create_stripe_card_endpoint(request: Request):
    try:
        logger.info("API: create-new-card")
        data = await request.json()
        customer_id = data["customer_id"]
        is_duplicate = "false"
        token = data["token"]
        new_card = stripe.Token.retrieve(token)
        old_card = stripe.Customer.retrieve(customer_id)
        if 'id' in old_card:
            old_card_data = old_card["sources"]["data"]
            for card in old_card_data:
                if card["fingerprint"] == new_card["card"]["fingerprint"]:
                    is_duplicate = "true"
                    break;
            if is_duplicate == "true":
                return {"status": "failed", "message": "Please enter a different card than you used originally."}
            else:
                response = stripe.Customer.create_source(customer_id, source=token)
                return {"status": "success", "data": response}
        else:
            response = stripe.Customer.create_source(customer_id, source=token)
            return {"status": "success", "data": response}


    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@router.post('/stripe-refund', tags=["stripe"])
async def stripe_refund_endpoint(refund: StripeRefund):
    """When you create a new refund, you must specify a Charge or a PaymentIntent object on which to create it.
Creating a new refund will refund a charge that has previously been created but not yet refunded.
Funds will be refunded to the credit or debit card that was originally charged."""
    try:
        logger.info("API: stripe-refund")
        logger.debug(refund.dict())
        response = stripe.Refund.create(**refund.dict())

        return response

    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@router.post('/stripe-update-subsription-saving', tags=["stripe"])
async def stripe_update_subsription_saving_endpoint(request: Request):
    """Updates an existing subscription to match the specified parameters.
    When changing prices or quantities, we optionally prorate the price we charge
    next month to make up for any price changes. """
    try:
        logger.info("API: stripe-update-subsription-saving")
        data = await request.json()
        subscription_id = data["subscription_id"]
        resume_at = data["resume_at"]
        response = stripe.Subscription.modify(subscription_id, pause_collection={"behavior": "mark_uncollectible",
                                                                                 "resumes_at": resume_at})
        return response

    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@router.post('/stripe-create-invoice', tags=["stripe"])
async def stripe_create_invoice_endpoint(request: Request):
    """Creates an item to be added to a draft invoice (up to 250 items per invoice).
    If no invoice is specified, the item will be on the next invoice created for the customer specified."""
    try:
        logger.info("API: stripe-create-invoice")
        data = await request.json()
        amount = data["amount"]
        if 'customer' in data:
            customer = data["customer"]
            response = stripe.InvoiceItem.create(customer=customer, amount=amount, currency="usd", )
            logger.debug(response)
            return response
        else:
            customer = stripe.Customer.create(source=data["token"])
            response = stripe.InvoiceItem.create(customer=customer["id"], amount=amount, currency="usd", )
            logger.debug(response)
            return {"data": response, "customer": customer["id"]}
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@router.post('/stripe-create-invoice-subscription', tags=["stripe"])
async def stripe_create_invoice_endpoint(request: Request):
    """Include a one-time charge or discount to the first subscription invoice using
    add_invoice_items with one-time price:"""
    try:
        logger.info("API: stripe-create-invoice-subscription")
        data = await request.json()
        items = data["items"]
        add_invoice_items = data["add_invoice_items"]
        coupon = data["coupon"]
        if 'customer' in data:
            customer = data["customer"]
            response = stripe.Subscription.create(customer=customer, items=items, add_invoice_items=add_invoice_items,
                                                  coupon=coupon)
            return {"data": response, "customer_id": customer}
        else:
            token = data["token"]
            customer = stripe.Customer.create(source=token)
            response = stripe.Subscription.create(customer=customer["id"], items=items,
                                                  add_invoice_items=add_invoice_items, coupon=coupon)
            return {"data": response, "customer_id": customer["id"]}

    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@router.post('/stripe-webhook', tags=["stripe"])
async def stripe_webhook(request: Request, background_tasks: BackgroundTasks):
    logger.info("API: stripe-webhook")
    logger.info("started.")

    payload = await request.body()
    sig_header = request.headers.get('STRIPE-SIGNATURE')

    # This is Stripe webhook secret for endpoint.
    if is_prod is False:
        endpoint_secret = 'whsec_dfb2ed553ffea56f117e7364994389b4c30869e582c2630de6f043138b041503'
    else:
        endpoint_secret = 'whsec_8iuPPiPc1pADBA8khbnPpH7AosXFhO1h'

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )

        background_tasks.add_task(stripe_webhook_handle, event)

        return {"success": "Being handled in background"}

    except Exception as e:
        logger.exception(e)
        return {"error": e}


@router.post('/stripe-new-payment-method', tags=["stripe"])
async def create_stripe_card_endpoint(request: Request):
    try:
        logger.info("API: stripe-new-payment-method")
        data = await request.json()
        customer_id = data["customer_id"]
        is_duplicate = "false"
        token = data["token"]
        new_card = stripe.Token.retrieve(token)
        old_card = stripe.Customer.retrieve(customer_id)
        if 'id' in old_card:
            old_card_data = old_card["sources"]["data"]
            for card in old_card_data:
                if card["fingerprint"] == new_card["card"]["fingerprint"]:
                    is_duplicate = "true"
                    break
            if is_duplicate == "true":
                return {"status": "failed", "message": "Please enter a different card than you used originally."}
            else:
                response = stripe.Customer.create_source(customer_id, source=token)
                if "id" in response:
                    new_card = stripe.Customer.modify(customer_id, default_source=response["id"])
                    return {"status": "success", "data": new_card}
                else:
                    return {"status": "failed", "error": "Card not added"}
        else:
            response = stripe.Customer.create_source(customer_id, source=token)
            if "id" in response:
                new_card = stripe.Customer.modify(customer_id, default_source=response["id"])
                return {"status": "success", "data": new_card}
            else:
                return {"status": "failed", "error": "Card not added"}

    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


# @router.get('/get-customer-cards/{mrn}')
async def get_customer_cards(mrn: str):
    """Retrieve Customer's Cards"""
    db = DBClient()
    try:
        visit = db.get_visits_by_mrn(mrn)
        if not visit:
            return {"status": "failed", "message": f"No data found against this mrn {mrn}"}
        customer_id = visit.get('customer_id')
        response = retrieve_customer_cards(customer_id)
        return {"status": "success", "data": response.get('data')}
    except Exception as e:
        logger.exception("get_customer_source ==> " + str(e))
        return {"status": "failed", "error": str(e)}


@router.post('/update-customer-default-card', tags=["stripe"])
async def update_customers_default_card(data: UpdateSource):
    """
    Update Customer's Default Card if exists already
    else create card and update it as default
    """
    try:
        logger.info("API: update-customer-default-card")
        client = DBClient()
        all_data = client.get_visits_data_by_mrn(data.mrn)
        if not all_data.get('data'):
            return {"status": "failed", "message": f"No visits found against mrn: {data.mrn}"}
        visit = all_data.get('data')[0]
        customer_id = visit.get("customer_id")
        if not customer_id:
            return {"status": "failed", "message": f"No customer_id found against mrn: {data.mrn}"}
        response = retrieve_customer_cards(customer_id)
        existing_cards = []
        for card in response:
            existing_cards.append(card.get('id'))
        if data.token not in existing_cards:
            new_card = create_customer_card_on_stripe(customer_id, data.token)
            card_id = new_card.get('id')
        else:
            card_details = retrieve_customer_card_by_token(data.token)
            card_id = card_details.get('card', {}).get('id')
        update_customer_default_card(customer_id, card_id)
        return {"status": "success"}
    except Exception as e:
        logger.exception("update_customers_default_card " + str(e))
        return {"status": "failed", "error": str(e)}


class StripePauseSubscription(BaseModel):
    subscription_id: str
    email: Optional[str]
    status: str


@router.post('/stripe-pause-subscription-create', tags=["stripe"])
async def stripe_pause_subscription_create(data: StripePauseSubscription, db: Session = Depends(get_db)):
    """Create stripe_pause_subscription table row"""
    logger.debug(data.dict())
    try:
        row = StripePauseSubscriptionCrud.create_with_values(
            db,
            subscription_id=data.subscription_id,
            email=data.email,
            status=data.status
        )
        return {"status": "success", "message": row}
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


class StripePauseSubscriptionUpdate(BaseModel):
    subscription_id: str
    status: str


@router.post('/stripe-pause-subscription-update', tags=["stripe"])
async def stripe_pause_subscription_update(data: StripePauseSubscriptionUpdate, db: Session = Depends(get_db)):
    """Update stripe_pause_subscription table row"""
    logger.debug(data.dict())
    try:
        row = StripePauseSubscriptionCrud.update_status(
            db,
            subscription_id=data.subscription_id,
            status=data.status
        )
        return {"status": "success", "message": row}
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}
