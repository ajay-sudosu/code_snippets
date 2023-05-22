#!/usr/bin/env bash

if test "$AWS_ACCESS_KEY_ID" == ""
then
  echo "AWS_ACCESS_KEY_ID not set in env!"
  echo "set the value then run again."
  exit 1
fi

if test "$AWS_SECRET_ACCESS_KEY" == ""
then  echo "AWS_SECRET_ACCESS_KEY not set in env!"
      echo "set the value then run again."
      exit 1
fi

if test "$ENV" == "PROD"
then
        worker=9
echo "[Unit]
Description=Next-Med backend gunicorn service
After=network.target

[Service]
Environment=FASTAPI_LOG_LEVEL=debug
Environment=IS_PROD=true
Environment=ENV=PROD
Environment=DD_SERVICE=\"backend-api\"
Environment=DD_ENV=\"prod\"
Environment=DD_LOGS_INJECTION=true
Environment=DD_TRACE_SAMPLE_RATE=\"1\"
Environment=DD_PROFILING_ENABLED=true
Environment=AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID
Environment=AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY
ExecStart=/home/ubuntu/.local/bin/ddtrace-run /home/ubuntu/.local/bin/gunicorn -w 9 -k uvicorn.workers.UvicornWorker --timeout 60 --graceful-timeout 60  -b 0.0.0.0:8080 main:app
WorkingDirectory=/home/ubuntu/Next-Medical/backend
StandardOutput=append:/var/log/next-med.log
StandardError=append:/var/log/next-med.log
Restart=always
User=ubuntu

[Install]
">>service.tmp

else
        worker=2
echo "[Unit]
Description=Next-Med backend gunicorn service
After=network.target

[Service]
Environment=FASTAPI_LOG_LEVEL=$FASTAPI_LOG_LEVEL
Environment=AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID
Environment=AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY
Environment=ENV=$ENV
Environment=IS_PROD=$IS_PROD
ExecStart=/home/ubuntu/pyenv/bin/gunicorn -w $worker -k uvicorn.workers.UvicornWorker --timeout 60 --graceful-timeout 60 -b 0.0.0.0:8080 main:app
WorkingDirectory=/home/ubuntu/Next-Medical/backend
StandardOutput=append:/var/log/next-med.log
StandardError=append:/var/log/next-med.log
Restart=always
User=ubuntu

[Install]
">>service.tmp
fi

sudo cp service.tmp /lib/systemd/system/

rm service.tmp

sudo ls /lib/systemd/system/gunicorn.service

sudo chmod 644 /lib/systemd/system/gunicorn.service

sudo systemctl daemon-reload

sudo systemctl enable gunicorn.service

sudo systemctl stop gunicorn.service

sudo systemctl start gunicorn.service
