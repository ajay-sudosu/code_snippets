import logging
from fastapi import APIRouter, Request, status, Response, Depends
from typing import Optional
from gogomeds import gogomeds
from db_client import DBClient
from auth.jwk_model import get_current_user
from pydantic import BaseModel


logger = logging.getLogger("fastapi")
router = APIRouter()


class GogomedsOrder(BaseModel):
    case_id: str


@router.post('/gogomeds-create-order', tags=["gogomeds"])
async def gogomeds_create_order_endpoint(request: Request):
    """create GoGoMeds order."""
    try:
        logger.info("API: gogomeds-create-order")
        db = DBClient()
        data = await request.json()
        logger.debug(data)
        res = gogomeds.create_order(data)
        if "Value" in res and res["Value"][0]["AffiliateOrderNumber"] is not None:
            db.insert_gogomeds_order(data.get("AffiliateOrderNumber"), res["Value"][0]["AffiliateOrderNumber"], res["Value"][0]["OrderId"])
        return {"status": True, "response": res}
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@router.get('/gogomeds-order-status', tags=["gogomeds"])
async def gogomeds_order_status_endpoint(AffiliateOrderNumber: str):
    """Get GoGoMeds order."""
    try:
        logger.info("API: gogomeds-order-status")
        db = DBClient()
        gogomeds_affiliateordernumber = db.get_gogomeds_affiliateordernumber(AffiliateOrderNumber)
        print("gogomeds_affiliateordernumber", gogomeds_affiliateordernumber)
        res = gogomeds.order_status(gogomeds_affiliateordernumber)
        logger.debug(res)
        return {"status": True, "response": res}
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@router.post('/gogomeds-cancel-order', tags=["gogomeds"])
async def gogomeds_cancel_order_endpoint(AffiliateOrderNumber: str):
    """Cancel GoGoMeds order."""
    try:
        logger.info("API: gogomeds-cancel-order")
        db = DBClient()
        gogomeds_affiliateordernumber = db.get_gogomeds_affiliateordernumber(AffiliateOrderNumber)
        res = gogomeds.cancel_order(gogomeds_affiliateordernumber)
        print("res", res)
        logger.debug(res)
        return {"status": True, "response": res}
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}

@router.post('/gogomeds-search-process', tags=["gogomeds"])
async def gogomeds_search_process_endpoint(request: Request):
    """Search GoGoMeds order."""
    try:
        logger.info("API: gogomeds-search-process")
        db = DBClient()
        data = await request.json()
        logger.debug(data)
        res = gogomeds.search_process(data)
        return {"status": True, "response": res}
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@router.post('/gogomeds-mark-order', tags=["gogomeds"])
async def gogomeds_mark_order_endpoint(AffiliateOrderNumber: str):
    """Mark GoGoMeds order."""
    try:
        logger.info("API: gogomeds-mark-order")
        db = DBClient()
        gogomeds_affiliateordernumber = db.get_gogomeds_affiliateordernumber(AffiliateOrderNumber)
        res = gogomeds.mark_order(gogomeds_affiliateordernumber)
        print("res", res)
        logger.debug(res)
        return {"status": True, "response": res}
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}

@router.post('/gogomeds-update-shipping', tags=["gogomeds"])
async def gogomeds_update_shipping_endpoint(AffiliateOrderNumber: str, ShippingMethod:str):
    """Update GoGoMeds Shipping."""
    try:
        logger.info("API: gogomeds-update-shipping")
        db = DBClient()
        gogomeds_affiliateordernumber = db.get_gogomeds_affiliateordernumber(AffiliateOrderNumber)
        gogomeds_shippingmethod = db.get_gogomeds_shipping_method(ShippingMethod)
        res = gogomeds.update_shipping(gogomeds_affiliateordernumber, gogomeds_shippingmethod)

        print("res", res)
        logger.debug(res)
        return {"status": True, "response": res}
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}

@router.post('/gogomeds-order-note', tags=["gogomeds"])
async def gogomeds_order_note_endpoint(AffiliateOrderNumber: str):
    """Note GoGoMeds order."""
    try:
        logger.info("API: gogomeds-order-note")
        db = DBClient()
        gogomeds_affiliateordernumber = db.get_gogomeds_affiliateordernumber(AffiliateOrderNumber)
        res = gogomeds.order_note(gogomeds_affiliateordernumber)
        print("res", res)
        logger.debug(res)
        return {"status": True, "response": res}
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}



@router.post('/gogomeds-update-order-status', tags=["gogomeds"])
async def gogomeds_update_order_status_endpoint(AffiliateOrderNumber: str, OrderStatus:str):
    """Update GoGoMeds Order Status."""
    try:
        logger.info("API: gogomeds-update-order-status")
        db = DBClient()
        gogomeds_affiliateordernumber = db.get_gogomeds_affiliateordernumber(AffiliateOrderNumber)
        gogomeds_order_status = db.get_gogomeds_order_status(OrderStatus)
        res = gogomeds.order_status(gogomeds_affiliateordernumber, gogomeds_order_status)

        print("res", res)
        logger.debug(res)
        return {"status": True, "response": res}
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}

@router.post('/gogomeds-update-order-item-status', tags=["gogomeds"])
async def gogomeds_update_orderitem_status_endpoint(request: Request):
    """Update GoGoMeds Order Item Status."""
    try:
        logger.info("API: gogomeds-update-order-item-status")
        db = DBClient()
        data = await request.json()
        logger.debug(data)
        res = gogomeds.update_orderitem_status(data)
        return {"status": True, "response": res}
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}
