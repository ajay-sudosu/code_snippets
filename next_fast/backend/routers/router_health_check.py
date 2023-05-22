from fastapi import APIRouter
import logging
from db_client import DBClient


logger = logging.getLogger("fastapi")
router = APIRouter()


def get_session():
    client = DBClient()
    status = client.health_check_db()
    return status


def is_database_online():
    db_session = get_session()
    return db_session


@router.get("/health")
def check_health():
    try:
        logger.info("API: /health")
        server_health = is_database_online()
        return "I am Alive." if server_health else "I am dead."
    except Exception as e:
        logger.error("Database Offline")

