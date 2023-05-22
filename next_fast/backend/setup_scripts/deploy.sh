#!/usr/bin/env bash

if ! git switch master;
then
  echo "cd to correct dir & run again"
  exit 1
fi

git switch master
git pull

# python3 -m pip install -r requirements.txt

sudo systemctl restart gunicorn.service
