#!/usr/bin/env python

import argparse
import base64
import json
import logging
import logging.handlers
import psutil
import requests
import signal
import ssl
import sys
import time
import urllib2
import uuid
import xml.etree.ElementTree as ET

from Crypto.Hash import SHA256
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.poolmanager import PoolManager

# Deafults
LOG_FILENAME = "/tmp/ismarthome.log"
LOG_LEVEL = logging.INFO

# Define and parse command line arguments
parser = argparse.ArgumentParser(description="iSmartHome HD Python Service")
parser.add_argument("-l", "--l", help="Log-File Pfad (Standard: '" + LOG_FILENAME + "')")
parser.add_argument("-i", "--i", help="IP Adresse der RWE Smarthome Zentrale", required=True)
parser.add_argument("-u", "--u", help="Benutzername", required=True)
parser.add_argument("-p", "--p", help="Passwort", required=True)
parser.add_argument("-v", "--v", help="BaseVersion (aktuell: 1.70)", required=True)

# If the log file is specified on the command line then override the default
args = parser.parse_args()
if args.l:
    LOG_FILENAME = args.l

# Configure logging to log to a file
logger = logging.getLogger(__name__)
logger.setLevel(LOG_LEVEL)
handler = logging.handlers.TimedRotatingFileHandler(LOG_FILENAME, when="midnight", backupCount=14)
formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# Make a class we can use to capture stdout and sterr in the log
class SmartHomeLogger(object):
    def __init__(self, logger, level):
        self.logger = logger
        self.level = level
        
    def write(self, message):
        # Only log if there is a message (not just a new line)
        if message.rstrip() != "":
            self.logger.log(self.level, message.rstrip())

# Replace stdout with logging to file at INFO level
sys.stdout = SmartHomeLogger(logger, logging.INFO)
# Replace stderr with logging to file at ERROR level
sys.stderr = SmartHomeLogger(logger, logging.ERROR)


# Main
def main():
    username = args.u
    password = args.p
    shcIP = args.i
    baseVersion = args.v
    
    passwordHash = base64.b64encode(SHA256.new(password).digest())
    
    while IsNetworkReachable() == False:
        time.sleep(10)
        logger.error('Netzwerk nicht verfuegbar. Warte 10 Sekunden.')
    
    start(username, passwordHash, baseVersion, shcIP, '')


def start(username, passwordHash, baseVersion, shcIP, clientId):
    clientId = RequestID()
        
    loginResponse = LoginRequest(username, passwordHash, baseVersion, shcIP, clientId)
    
    if loginResponse == 'Error':
        logger.error('LoginRequest fehlgeschlagen. Naechster Login Versuch in 1 Minute.')
                
        time.sleep(60)
        start(username, passwordHash, baseVersion, shcIP, clientId)
        return
    
    xmlLoginResponse = ET.fromstring(loginResponse)
        
    if 'Error' in xmlLoginResponse.attrib:
        if xmlLoginResponse.attrib['Error'] == 'InvalidCredentials':
            logger.error('Benutzerdaten sind falsch! Login nicht moeglich!')
                    
            return
        elif 'ExpectedVersion' in xmlLoginResponse.attrib:
            logger.error('Die BaseVerion \"' + baseVersion + '\" ist falsch. Benutze aktuelle BaseVersion \"' + xmlLoginResponse.attrib['ExpectedVersion'] + '\".')
                
            baseVersion = xmlLoginResponse.attrib['ExpectedVersion']
            start(username, passwordHash, baseVersion, shcIP, clientId)
            return

    if 'SessionId' in xmlLoginResponse.attrib:
        sessionId = xmlLoginResponse.attrib['SessionId']
        
        logger.info('Login erfolgreich')
        logger.info('SessionId: ' + sessionId)
        
        acknowledgeResponse = NotificationRequest(sessionId, baseVersion, shcIP, clientId)

        if acknowledgeResponse == 'Error':
            logger.error('NotificationRequest fehlgeschlagen... Naechster Login Versuch in 1 Minute')
                            
            time.sleep(60)
            start(username, passwordHash, baseVersion, shcIP, clientId)
            return
                
        xmlAcknowledgeResponse = ET.fromstring(acknowledgeResponse)
                    
        if 'Error' in xmlAcknowledgeResponse.attrib:
            if xmlLoginResponse.attrib['Error'] == 'IllegalSessionId':
                logger.error('Session abgelaufen... Starte Login.')
                                
                start(username, passwordHash, baseVersion, shcIP, clientId)
                return
                    
        updCounter = 0
        updateLoops = 300
        
        while updCounter < updateLoops:
            updCounter += 1
            
            stateUpdates = GetUpdates(shcIP, clientId)
                            
            if stateUpdates == 'Error':
                logger.error('Aktualisierung der States fehlgeschlagen... Naechster Login Versuch in 1 Minute')
                                    
                time.sleep(60)
                start(username, passwordHash, baseVersion, shcIP, clientId)
                return
                    
            Notifications = ET.fromstring(stateUpdates)
            Notifications = Notifications.find('Notifications')
                
            if Notifications.find('LogicalDeviceStatesChangedNotification') is not None:
                logger.info('Uebertrage States zum Push-Server...')
                    
                pushResult = SendStatesToPushServer(stateUpdates)
                                    
                if pushResult == 'Error':
                    logger.error('Uebertragung zum Push-Server fehlgeschlagen.')
                else:
                    logger.info('Uebertragung zum Push-Server erfolgreich.')
                    
            time.sleep(3)
        else:
            logoutResponse = LogoutRequest(sessionId, baseVersion, shcIP, clientId)
                    
            if logoutResponse == 'Error':
                logger.error('Logout fehlgeschlagen...')
            else:
                logger.info('Logout erfolgreich')
                    
                start(username, passwordHash, baseVersion, shcIP, clientId)


# Login Request
def LoginRequest(username, passwordHash, baseVersion, shcIP, clientId):
    loginRequest = LoginRequestString(username, passwordHash, baseVersion)
        
    headers = {
        'User-Agent': 'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0)',
        'Content-Type': 'application/json'
    }
    
    loginResponse = SendRequest('https://' + shcIP + '/cmd', str.encode(loginRequest), headers)
        
    return loginResponse


# Notification Request
def NotificationRequest(sessionId, baseVersion, shcIP, clientId):
    notificationRequest = NotificationRequestString(sessionId, baseVersion)
        
    headers = {
        'User-Agent': 'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0)',
        'Content-Type': 'application/json',
        'ClientId': clientId
    }
    
    result = SendRequest('https://' + shcIP + '/cmd', str.encode(notificationRequest), headers)
        
    return result


# Logout Request
def LogoutRequest(sessionId, baseVersion, shcIP, clientId):
    logoutRequest = LogoutRequestString(sessionId, baseVersion)
        
    headers = {
        'User-Agent': 'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0)',
        'Content-Type': 'application/json',
        'ClientId': clientId
    }
    
    result = SendRequest('https://' + shcIP + '/cmd', str.encode(logoutRequest), headers)
        
    return result


# Update States Request
def GetUpdates(shcIP, clientId):
    headers = {
        'User-Agent': 'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0)',
        'Content-Type': 'application/json',
        'ClientId': clientId
    }
    
    result = SendRequest('https://' + shcIP + '/upd', "", headers)

    return result


# Send states
def SendStatesToPushServer(states):
    headers = {
        'User-Agent': 'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0)',
        'Content-Type': 'application/json'
    }
        
    data = {
        'shcResponse': states
    }
        
    result = SendRequest('http://ismarthomehd.parseapp.com/checkShcResponse', json.dumps(data), headers)
        
    return result


# Login String
def LoginRequestString(username, password, baseVersion):
    return '<BaseRequest xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xsi:type="LoginRequest" RequestId="' + RequestID() + '" Version="' + baseVersion + '" UserName="' + username + '" Password="' + password + '" />'


# Logout String
def LogoutRequestString(sessionId, baseVersion):	
    return '<BaseRequest xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xsi:type="LogoutRequest" RequestId="' + RequestID() + '" Version="' + baseVersion + '" SessionId="' + sessionId + '" />'


# Notification String
def NotificationRequestString(sessionId, baseVersion):
    return '<BaseRequest xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" SessionId="' + sessionId + '" Version="' + baseVersion + '" xsi:type="NotificationRequest" RequestId="' + RequestID() + '"><Action>Subscribe</Action><NotificationType>DeviceStateChanges</NotificationType></BaseRequest>'


# UUID
def RequestID():
    return str(uuid.uuid4())


# Request
def SendRequest(url, d, h):
    s = requests.Session()
    s.mount('https://', MyAdapter())
    
    response = s.post(url, verify=False, headers=h, data=d)

    try:
        return response.text
    except Exception:
        logger.error("Fehler-Code: " + str(response.status_code))
        logger.error("Response: " + response.text)
        return 'Error'

# Check network connection
def IsNetworkReachable():
    try:
        response=urllib2.urlopen('http://google.de', timeout=2)
        return True
    except urllib2.URLError as err: pass
    return False

class MyAdapter(HTTPAdapter):
    def init_poolmanager(self, connections, maxsize, block=False):
        self.poolmanager = PoolManager(num_pools=connections,
                                       maxsize=maxsize,
                                       block=block,
                                       ssl_version=ssl.PROTOCOL_TLSv1)


if __name__=="__main__":
    main()




