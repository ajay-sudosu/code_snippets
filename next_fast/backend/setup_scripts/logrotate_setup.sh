#!/usr/bin/env bash

if ! sudo apt show logrotate;
then
  sudo apt install logrotate
fi

echo "
/var/log/next-med.log {
size 1G
missingok
rotate 30
compress
notifempty
copytruncate
}
">nextmed
sudo cp nextmed /etc/logrotate.d/nextmed
rm nextmed
sudo logrotate /etc/logrotate.conf --debug
