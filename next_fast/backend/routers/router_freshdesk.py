import logging

from api.freshdesk_api import fr_api
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, List
from db_client import DBClient

logger = logging.getLogger("fastapi")
router = APIRouter()


class UserTicket(BaseModel):
    name: str
    email: str
    phone: str
    subject: str
    description: str
    status: int
    priority: int
    # custom_fields: Optional[dict] 


class ViewFreshDeskTicket(BaseModel):
    ticket_id: str


class ReplyFreshDeskTicket(BaseModel):
    body: str
    ticket_id: str
    from_email: str
    cc_emails:  Optional[list]


class AddFreshdeskToVisits(BaseModel):
    mrn: str
    freshdesk_id: str


@router.post('/freshdesk-raise-ticket', tags=["freshdesk"])
async def raise_ticket_endpoint(ticket_obj: UserTicket):
    """Create ticket for freshdesk"""
    try:
        logger.info("API: freshdesk-raise-ticket")
        data = ticket_obj.dict()
        logger.debug(data)
        response = fr_api.create_ticket(body=data)
        logger.debug(response)
        return response

    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@router.post('/freshdesk-view-ticket', tags=["freshdesk"])
async def view_ticket_endpoint(ticket_obj: ViewFreshDeskTicket):
    """View ticket for freshdesk"""
    try:
        logger.info("API: freshdesk-view-ticket")
        data = ticket_obj.dict()
        logger.debug(data)
        response = fr_api.view_ticket(data["ticket_id"])
        logger.debug(response)
        return response

    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@router.post('/freshdesk-reply-ticket', tags=["freshdesk"])
async def reply_ticket_endpoint(ticket_obj: ReplyFreshDeskTicket):
    """Reply ticket for freshdesk"""
    try:
        logger.info("API: freshdesk-reply-ticket")
        data = ticket_obj.dict()
        logger.debug(data)
        response = fr_api.reply_ticket(body=data)
        logger.debug(response)
        return response

    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}


@router.post('/visits-add-freshdesk-ticket', tags=["freshdesk"])
async def add_freshdesk_to_visits_endpoint(ticket_obj: AddFreshdeskToVisits):
    """Add freshdesk ticket id to visits"""
    try:
        logger.info("API: visits-add-freshdesk-ticket")
        client = DBClient()
        data = ticket_obj.dict()
        logger.debug(data)
        visit_exists = client.get_visits_by_mrn(data["mrn"])
        if not visit_exists:
            raise Exception('visit not found for this mrn')
        response = client.update_patient_visits_add_freshdesk_ticket_id(
            data["mrn"], data["freshdesk_id"]
        )
        logger.info(f"add_freshdesk_to_visits_endpoint ==> {str(response)}")
        return response
    except Exception as e:
        logger.exception(f"add_freshdesk_to_visits_endpoint ==> {str(e)}")
        return {"status": "failed", "error": str(e)}


@router.post('/freshdesk-get-conversation', tags=["freshdesk"])
async def reply_ticket_endpoint(ticket_obj: ViewFreshDeskTicket):
    """Get ticket conversation for freshdesk"""
    try:
        logger.info("API: freshdesk-get-conversation")
        data = ticket_obj.dict()
        logger.debug(data)
        response = fr_api.view_conversation(data["ticket_id"])
        logger.debug(response)
        return response

    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}
