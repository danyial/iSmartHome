#!/bin/bash

IPADDRESS=$(whiptail --title "IP-Adresse" --inputbox "Bitte geben Sie die IP-Adresse der Zentrale ein" 10 60 3>&1 1>&2 2>&3)

USERNAME=$(whiptail --title "Benutzername" --inputbox "Bitte geben Sie Ihren SmartHome Benutzernamen ein" 10 60 3>&1 1>&2 2>&3)

PASSWORD=$(whiptail --title "Passwort" --inputbox "Bitte geben Sie Ihr SmartHome Passwort ein" 10 60 3>&1 1>&2 2>&3)

VERSION=$(whiptail --title "Version" --inputbox "Bitte geben Sie die Softwareversion der Zentrale ein" 10 60 1.70 3>&1 1>&2 2>&3)

sudo apt-get --assume-yes install gcc python-dev python-requests lighttpd php5-common php5-cgi php5 php5-curl

cd /tmp/iSmartHome

sed -i -e "s/\(DAEMON_OPTS=\).*/\1'-i $IPADDRESS -u $USERNAME -p $PASSWORD -v $VERSION'/" ismarthome.sh
sed -i -e "s/\(DAEMON_USER=\).*/\1$USER/" ismarthome.sh

git clone https://github.com/giampaolo/psutil.git
git clone https://github.com/dlitz/pycrypto.git

cd psutil
sudo python setup.py install

cd /tmp/iSmartHome/pycrypto
sudo python setup.py install

cd /opt
sudo mkdir iSmartHome
cd iSmartHome
sudo mkdir Logs
cd /var/www/html
sudo mkdir iSmartHome

sudo cp /tmp/iSmartHome/ismarthome.sh /etc/init.d/ismarthome.sh
sudo cp /tmp/iSmartHome/ismarthome.py /opt/iSmartHome/ismarthome.py
sudo cp /tmp/iSmartHome/Actions.json /opt/iSmartHome/Actions.json
sudo cp /tmp/iSmartHome/index.php /var/www/html/iSmartHome/index.php

sudo chmod 755 /opt/iSmartHome/ismarthome.py
sudo chmod 755 /etc/init.d/ismarthome.sh
sudo chown -R $USER /opt/iSmartHome/

cd /etc/init.d
sudo update-rc.d ismarthome.sh defaults

crontab -l | { cat; echo "@daily sudo service ismarthome restart"; } | crontab -

sudo systemctl daemon-reload
sudo service ismarthome start

sudo lighttpd-enable-mod fastcgi fastcgi-php
sudo service lighttpd restart



