import logging
from fastapi import APIRouter, Request, status, Response, Depends
from api.affirm_api import affirm_api
from pydantic import BaseModel
from typing import Optional

logger = logging.getLogger("fastapi")
router = APIRouter()


class AffirmUpdateTransaction(BaseModel):
    transaction_id: str
    order_id: Optional[str]
    reference_id: Optional[str]
    shipping_carrier: Optional[str]
    shipping_confirmation: Optional[str]
    shipping: Optional[dict]


class AffirmCaptureTransaction(BaseModel):
    transaction_id: str
    order_id: Optional[str]
    reference_id: Optional[str]
    shipping_carrier: str
    shipping_confirmation: str
    amount: int
    metadata: Optional[dict]


class AffirmAuthorizeTransaction(BaseModel):
    transaction_id: str
    order_id: str


class AffirmRefundTransaction(BaseModel):
    transaction_id: str
    amount: int
    reference_id: Optional[str]
    transaction_event_count: int
    metadata: Optional[dict]


@router.get('/affirm-get-transaction', tags=["affirm"])
async def affirm_get_transaction_endpoint(transaction_id: str):
    """Reads the details of a transaction."""
    try:
        response = affirm_api.read_transaction(transaction_id)
        logger.debug(response)
        return response

    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@router.post('/affirm-update-transaction', tags=["affirm"])
async def affirm_update_transaction_endpoint(transaction: AffirmUpdateTransaction):
    """Updates the specified transaction by setting the values of the parameters passed.
    Any parameters not provided will be left unchanged."""
    try:
        data = transaction.dict()
        logger.debug(data)
        del data["transaction_id"]
        response = affirm_api.update_transaction(
            transaction.transaction_id, body=data)
        logger.debug(response)
        return response

    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@router.post('/affirm-capture-transaction', tags=["affirm"])
async def affirm_capture_transaction_endpoint(transaction: AffirmCaptureTransaction):
    """Capture an authorized transaction to capture or settle the funds."""
    try:
        data = transaction.dict()
        logger.debug(data)
        del data["transaction_id"]
        response = affirm_api.capture_transaction(
            transaction.transaction_id, body=data)
        logger.debug(response)
        return response

    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@router.post('/affirm-authorize-transaction', tags=["affirm"])
async def affirm_authorize_transaction_endpoint(transaction: AffirmAuthorizeTransaction):
    """Authorizes a transaction. Transaction authorization occurs after a user completes
    the Affirm checkout flow and returns to the merchant site."""
    try:
        data = transaction.dict()
        logger.debug(data)
        response = affirm_api.authorize_transaction(body=data)
        logger.debug(response)
        return response

    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@router.post('/affirm-refund-transaction', tags=["affirm"])
async def affirm_refund_transaction_endpoint(transaction: AffirmRefundTransaction):
    """Refund a transaction that was previously created but that hasn't been refunded yet."""
    try:
        data = transaction.dict()
        logger.debug(data)
        del data["transaction_id"]
        response = affirm_api.refund_transaction(
            transaction.transaction_id, body=data)
        logger.debug(response)
        return response

    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}
