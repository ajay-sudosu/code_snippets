import time
from celery import Celery

celery_app = Celery('tasks', backend="redis://localhost:6379/1", broker="amqp://admin:admin@localhost:5672")


@celery_app.task
def task_test():
    try:
        for i in range(3):
            time.sleep(i)
        return {"message": "Success."}
    except Exception as e:
        return {"message": "Failed."}
