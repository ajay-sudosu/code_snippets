from celery import Celery
# from celery.schedules import crontab
from datetime import timedelta
app = Celery('tasks', broker='redis://localhost:6379/0', backend='redis://localhost:6379/0')


@app.task
def send_pdf_mail(subscribtion_date):
    return "This is celery saying \n HELLO"


if __name__ == '__main__':
    app.start()
