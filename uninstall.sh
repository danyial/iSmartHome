#!/bin/bash

sudo service ismarthome stop
sudo rm -R /opt/iSmartHome
sudo rm /etc/init.d/ismarthome.sh
sudo systemctl daemon-reload
crontab -l | sed 's/@daily sudo service ismarthome restart//' | crontab -