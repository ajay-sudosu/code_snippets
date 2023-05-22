service rabbitmq-server start
(rabbitmqctl add_user admin admin; \
rabbitmqctl set_user_tags admin administrator ; \
rabbitmqctl set_permissions -p / admin  ".*" ".*" ".*" ; \
echo "*** User 'admin' with password 'admin' completed. ***" ; \
echo "*** Log in the WebUI at port 15672 (example: http://{gg/ip}:15672) ***")
rabbitmq-plugins enable rabbitmq_management;
sed -i -e 's/bind 127.0.0.1 ::1/#bind 127.0.0.1 ::1/g' /etc/redis/redis.conf
sed -i -e 's/protected-mode yes/protected-mode no/g' /etc/redis/redis.conf
service redis-server start
service rabbitmq-server restart
cron -f