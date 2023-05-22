import logging
from fastapi import APIRouter, Request, status, Response, BackgroundTasks, Depends, HTTPException
from bg_task.zendesk_tasks import zendesk_webhook_handle
from database.db import get_db
from database.crud import OpenloopCapacityRepo
from database import schemas
from sqlalchemy.orm import Session

logger = logging.getLogger("fastapi")
router = APIRouter()

WEBHOOK_SECRET = '__zendesk__123@#'
WEBHOOK_TOKEN = 'Bearer eyJraWQiOiJPcFVSUHJRTnBLWmpGdCtaS3Ryb2I5Qm0xQVJTR25kUHBmWFk4WGhWcVwvWT0iLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiIwMGFhYTk2Mi03OTRjLTQ4YWYtOGNkZC1lNmMzNWYxMjdjOWUiLCJlbWFpbF92ZXJpZmllZCI6dHJ1ZSwiaXNzIjoiaHR0cHM6XC9cL2NvZ25pdG8taWRwLnVzLWVhc3QtMi5hbWF6b25hd3MuY29tXC91cy1lYXN0LTJfdnBDUmZJdlhEIiwicGhvbmVfbnVtYmVyX3ZlcmlmaWVkIjp0cnVlLCJjb2duaXRvOnVzZXJuYW1lIjoiMDBhYWE5NjItNzk0Yy00OGFmLThjZGQtZTZjMzVmMTI3YzllIiwiYXVkIjoiNjZmb3ZwajR2Y3A5NDg4bGI5bzduM3J2NTgiLCJldmVudF9pZCI6ImNiMjE5NTU0LWM2OGUtNDNmZS1iZjgyLTc2MjE2ODNlMGFjNCIsInRva2VuX3VzZSI6ImlkIiwiYXV0aF90aW1lIjoxNjY2MTYwODA5LCJwaG9uZV9udW1iZXIiOiIrOTE4ODI2MDA2NTA4IiwiZXhwIjoxNjY2MjQ3MjA5LCJpYXQiOjE2NjYxNjA4MDksImVtYWlsIjoidGFyaXF1ZUBqb2lubmV4dG1lZC5jb20ifQ.BhjplLmjGExJAGJXajUJ7bQvWS9usiDeBvSOhiKu7JVhzgpAz8udNaJfe1ZoUuoji4PEIQmv_puE3R6X2QefVjX1_LvLDeravO88a5BOgPRYWA8g-F6RooaMafGsLzBCYiz6Hi0Amyl3hRojwaIs1dSoY136Sax15p9eoV5FvcqdxE14WBjBCH07OePyyLXHxt8Js4w2FhulOCcWyOZMkOGAi-JJsWLV4U7uXCg2F0NHBCZ_e0VnoqLaSv71uoGADKGZdLNYfkSt5fjMjGGqiSVMhbZxZ6pZrG2p1hIJ1hL2IjweaAOKoPxGn0o_iB8Fb_EzwJf3AlwJ7YJfQyRGBw'


@router.post('/zendesk-webhook', tags=["zendesk"])
async def zendesk_webhook_endpoint(request: Request, response: Response, background_tasks: BackgroundTasks):
    try:
        logger.info("API: zendesk-webhook")
        # check token
        token = request.headers.get('Authorization')
        if token != WEBHOOK_TOKEN:
            response.status_code = status.HTTP_403_FORBIDDEN
            return {"message": "Invalid Token"}

        # # check header
        # signature = request.headers.get('X-Zendesk-Webhook-Signature')
        # signature_ts = request.headers.get('X-Zendesk-Webhook-Signature-Timestamp')
        # if signature is None or signature_ts is None:
        #     response.status_code = status.HTTP_403_FORBIDDEN
        #     return {"status": "failed", "error": "HTTP header 'Signature' is missing"}

        # # check header
        # content_type = request.headers.get('Content-Type')
        # if content_type is None:
        #     response.status_code = status.HTTP_403_FORBIDDEN
        #     return {"status": "failed", "error": "HTTP header 'content_type' is missing"}
        # elif content_type != 'application/json':
        #     response.status_code = status.HTTP_403_FORBIDDEN
        #     return {"status": "failed", "error": "unsupported content_type"}

        '''# find algo & hash
        algo, msg_hash = signature.split('=')
        # logger.debug(algo, msg_hash)

        # get raw request body
        raw_data = await request.body()
        # calculate hash
        digest_maker = hmac.new(bytes(WEBHOOK_SECRET, 'utf-8'), raw_data, hashlib.sha256)

        # check hash for authentication
        cal_hash = digest_maker.hexdigest()
        # logger.debug(cal_hash)
        if cal_hash != msg_hash:
            response.status_code = status.HTTP_403_FORBIDDEN
            return {"message": "Secret Key Mismatch"}'''

        data = await request.json()
        background_tasks.add_task(zendesk_webhook_handle, data)

        return {"status": "success", "data": "Being handled in bg."}
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@router.get('/get-openloop-capacity', tags=["openloop"])
async def get_openloop_capacity_endpoint(abbreviation: str, db: Session = Depends(get_db)):
    """Get openloop_capacity from db"""
    try:
        logger.info("API: get-openloop-capacity")
        openloop_capacity = OpenloopCapacityRepo.fetch_by_state_abbr(db, abbreviation=abbreviation)
        if openloop_capacity is None:
            raise HTTPException(status_code=404, detail="State not found")
        return {"status": "success", "data": openloop_capacity}
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@router.post('/update-openloop-capacity', tags=["openloop"])
async def update_openloop_capacity_endpoint(capacity: schemas.OpenloopCapacitySchema, db: Session = Depends(get_db)):
    """Update openloop_capacity in db"""
    try:
        logger.info("API: update-openloop-capacity")
        logger.debug(capacity.dict())
        openloop_capacity = OpenloopCapacityRepo.fetch_by_state_abbr(db, abbreviation=capacity.StateAbbreviation)
        if openloop_capacity is None:
            raise HTTPException(status_code=404, detail="State not found")
        updated_openloop_capacity = OpenloopCapacityRepo.update_capacity(db, openloop_capacity, capacity.Capacity)
        return {"status": "success", "data": updated_openloop_capacity}
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}
