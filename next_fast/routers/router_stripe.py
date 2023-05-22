import logging
from fastapi import APIRouter, Request, status, Response, BackgroundTasks
import stripe
from typing import Optional
from pydantic import BaseModel
from config import STRIPE_API_KEY, is_prod
from bg_task.stripe_tasks import stripe_webhook_handle


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


@router.get('/stripe-fetch-refund', tags=["stripe"])
async def stripe_fetch_refund_endpoint(refund_id: str):
    """Retrieves the details of an existing refund."""
    try:
        logger.debug("fetching refund details: ", refund_id)
        response = stripe.Refund.retrieve(refund_id)
        return response

    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@router.post('/stripe-refund', tags=["stripe"])
async def stripe_refund_endpoint(refund: StripeRefund):
    """When you create a new refund, you must specify a Charge or a PaymentIntent object on which to create it.
Creating a new refund will refund a charge that has previously been created but not yet refunded.
Funds will be refunded to the credit or debit card that was originally charged."""
    try:
        logger.debug(refund.dict())
        response = stripe.Refund.create(**refund.dict())

        return response

    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@router.post('/stripe-webhook', tags=["stripe"])
async def stripe_webhook(request: Request, background_tasks: BackgroundTasks):
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
