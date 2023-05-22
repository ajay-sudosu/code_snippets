import logging
from fastapi import APIRouter, Request, status, Response, Depends
from typing import Optional
from db_client import DBClient
from auth.jwk_model import get_current_user
from pydantic import BaseModel
from datetime import datetime

logger = logging.getLogger("fastapi")
router = APIRouter()


class WeightLossEntry(BaseModel):
    subscriptionType: str
    subscriptionId: str


@router.post('/add-weight-loss-queue-entry', tags=["misc"])
async def add_weight_loss_queue_entry_endpoint(wt_loss_entry: WeightLossEntry, email: str = Depends(get_current_user)):
    req = wt_loss_entry.dict()
    logger.debug(req)

    try:
        client = DBClient()
        if wt_loss_entry.subscriptionType.lower().strip() == "wegovy":
            maximum_refills = 5
        elif wt_loss_entry.subscriptionType.lower().strip() == "ozempic":
            maximum_refills = 1
        else:
            return {"status": "failed", "error": f"Not found subscriptionType: {wt_loss_entry.subscriptionType}"}

        today_date = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
        client.add_weight_loss_queue_entry(email, wt_loss_entry.subscriptionId, wt_loss_entry.subscriptionType,
                                           today_date, today_date, maximum_refills, 0, 'in_progress', '1st order')
        return {"status": "success", "message": f"weight loss entry created for {email}"}

    except Exception as e:
        return {"status": "failed", "error": str(e)}
