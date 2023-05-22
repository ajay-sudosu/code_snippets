from datetime import datetime, timedelta
from celery.schedules import crontab
from task_scheduler import app

broker_url = 'redis://localhost:6379/0'


app.conf.beat_schedule = {
    'send_hello_function': {
        'task': 'task_scheduler.send_hello',
        'schedule': timedelta(seconds=3),
    },
}

# Start the Celery beat scheduler
app.conf.timezone = 'UTC'


if __name__ == '__main__':
    app.start()
