import logging
from datetime import date

from db_client import DBClient
from healthie import healthie

logger = logging.getLogger("fastapi")


def create_tasks():
    """
    Get patients data from visits table when is_healthie is 1 and
    create tasks for them
    """
    try:
        client = DBClient()
        visits_data = client.get_visits_data_by_is_healthie()
        count = 0;
        for item in visits_data.get('data', []):
            if item.get('drchrono_res', None) or item.get('address', "") == 'Lab uploaded':
                count = count + 1
                healthie_id = item.get('healthie_id', None)
                if healthie_id:
                    healthie_dict = {
                        "user_id": "1627246",
                        "content": "EB_CHECK",
                        "client_id": healthie_id,
                        "due_date": date.today().strftime('%Y-%m-%d'),
                        "remainder": {
                            "is_enabled": True,
                            "interval_type": "daily",
                            "interval_value": "friday",
                            "remove_reminder": True
                        }
                    }
                    res = healthie.create_task(healthie_dict)
                    print(res)
        print(count)
    except Exception as e:
        logger.exception(
            "healthie create task => task not created: " + str(e)
        )


if __name__ == '__main__':
    create_tasks()
