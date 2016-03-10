#!/bin/bash

IPADDRESS=$(whiptail --title "IP-Adresse" --inputbox "Bitte geben Sie die IP-Adresse der Zentrale ein" 10 60 3>&1 1>&2 2>&3)
 
exitstatus=$?
if [ $exitstatus = 0 ]; then
    echo "IP-Adresse:" $IPADDRESS
else
    echo "Abbruch"
fi

USERNAME=$(whiptail --title "Benutzername" --inputbox "Bitte geben Sie Ihren SmartHome Benutzernamen ein" 10 60 3>&1 1>&2 2>&3)
 
exitstatus=$?
if [ $exitstatus = 0 ]; then
    echo "Benutzername:" $USERNAME
else
    echo "Abbruch"
fi

PASSWORD=$(whiptail --title "Passwort" --inputbox "Bitte geben Sie Ihr SmartHome Passwort ein" 10 60 3>&1 1>&2 2>&3)
 
exitstatus=$?
if [ $exitstatus = 0 ]; then
    echo "Passwort:" $PASSWORD
else
    echo "Abbruch"
fi

VERSION=$(whiptail --title "Version" --inputbox "Bitte geben Sie die Softwareversion der Zentrale ein" 10 60 1.70 3>&1 1>&2 2>&3)
 
exitstatus=$?
if [ $exitstatus = 0 ]; then
    echo "Version:" $VERSION
else
    echo "Abbruch"
fi

sudo apt-get update
sudo apt-get upgrade
sudo apt-get install gcc python-dev

cd ~/iSmartHome

sed -i -e "s/\(DAEMON_OPTS=\).*/\1'-i $IPADDRESS -u $USERNAME -p $PASSWORD -v $VERSION'/" ismarthome.sh

git clone https://github.com/giampaolo/psutil.git
git clone https://github.com/dlitz/pycrypto.git

cd psutil
sudo python setup.py install

cd ~/iSmartHome/pycrypto
sudo python setup.py install

cd ~/iSmartHome
sudo cp ismarthome.sh /etc/init.d/ismarthome.sh
sudo chmod 755 ismarthome.py
sudo chmod 755 /etc/init.d/ismarthome.sh
cd /etc/init.d
sudo update-rc.d ismarthome.sh defaults

crontab -e > ismarthomecron
echo "@daily sudo service ismarthome restart" >> ismarthomecron
sudo crontab ismarthomecron
rm ismarthomecron

sudo reboot



