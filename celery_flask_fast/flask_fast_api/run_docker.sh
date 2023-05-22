#!/bin/bash
mkdir -p /var/log/uwsgi
chown -R $user:$user /var/log/uwsgi
chown -R $user:$user /ext512
python /app/app/fastapp/asgi.py &
uwsgi --ini app.ini &
cd /app/app
celery -A celery_app.main worker --loglevel=INFO
cron -f

