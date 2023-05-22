FROM python:3.7.10
WORKDIR /app
ADD . /app
RUN apt-get update && apt-get install -y python3-opencv cron
RUN apt-get install -y ffmpeg
RUN apt-get install libpcre3 libpcre3-dev
RUN pip install -r requirements.txt
COPY flask_cron /etc/cron.d/flask_cron
RUN chmod 0644 /etc/cron.d/flask_cron
RUN crontab /etc/cron.d/flask_cron
CMD ["sh", "run_docker.sh"]