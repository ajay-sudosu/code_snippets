FROM rabbitmq:3-management
WORKDIR /rabbitmq
RUN apt-get update && apt-get -y install redis-server cron rabbitmq-server
COPY rabbitmq_cron /etc/cron.d/rabbitmq_cron
RUN chmod 0644 /etc/cron.d/rabbitmq_cron
RUN crontab /etc/cron.d/rabbitmq_cron
ADD . /rabbitmq
CMD ["sh", "run_docker.sh"]