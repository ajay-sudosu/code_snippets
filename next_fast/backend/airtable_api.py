import logging

from pyairtable import Table

AIRTABLE_TOKEN = 'keyalgn06WaIgrxbK'
AIRTABLE_BASE_ID = 'appWCzNS6feFG1fGE'
AIRTABLE_TABLE_NAME = "PA Process ->"

table = Table(AIRTABLE_TOKEN, AIRTABLE_BASE_ID, AIRTABLE_TABLE_NAME)
logger = logging.getLogger("fastapi")


def create_new_record(data):
    """Add data to the Airtable."""
    try:
        response = table.create(data)
        return response
    except Exception as e:
        logger.exception("create_new_record => record not created: " + str(e))
        return None
