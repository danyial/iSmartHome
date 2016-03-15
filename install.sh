#!/bin/bash

IPADDRESS=$(whiptail --title "IP-Adresse" --inputbox "Bitte geben Sie die IP-Adresse der Zentrale ein" 10 60 3>&1 1>&2 2>&3)

USERNAME=$(whiptail --title "Benutzername" --inputbox "Bitte geben Sie Ihren SmartHome Benutzernamen ein" 10 60 3>&1 1>&2 2>&3)

PASSWORD=$(whiptail --title "Passwort" --inputbox "Bitte geben Sie Ihr SmartHome Passwort ein" 10 60 3>&1 1>&2 2>&3)

VERSION=$(whiptail --title "Version" --inputbox "Bitte geben Sie die Softwareversion der Zentrale ein" 10 60 1.70 3>&1 1>&2 2>&3)

sudo apt-get install gcc python-dev

cd /tmp/iSmartHome

sed -i -e "s/\(DAEMON_OPTS=\).*/\1'-i $IPADDRESS -u $USERNAME -p $PASSWORD -v $VERSION'/" ismarthome.sh

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
sudo cp /tmp/iSmartHome/ismarthome.sh /etc/init.d/ismarthome.sh
sudo cp /tmp/iSmartHome/ismarthome.py /opt/iSmartHome/ismarthome.py
sudo chmod 755 /opt/iSmartHome/ismarthome.py
sudo chmod 755 /etc/init.d/ismarthome.sh
cd /etc/init.d
sudo update-rc.d ismarthome.sh defaults

cd /tmp
sudo crontab -e > ismarthomecron
echo "@daily sudo service ismarthome restart" >> ismarthomecron
sudo crontab ismarthomecron



