#!/usr/bin/env bash

# Refresh drchrono token & restart the gunicorn service

cd /home/ubuntu/Next-Medical/backend
python3 -c "from drchrono import drchrono;drchrono.refresh_token()"

sudo systemctl stop gunicorn.service

sudo systemctl start gunicorn.service
