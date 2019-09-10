import sys
import base64
import json
import sys
import configparser
import os.path
import datetime
import boto3

config = configparser.ConfigParser()
config.read('config.ini')

DEFAULT_TZ = config['DEFAULT']['DEFAULT_TZ']
VESYNCAPIPATH = config['DEFAULT']['VESYNCAPIPATH']
POWERTHRESHOLD = float(config['DEFAULT']['PowerThreshold'])
UserName = config['DEFAULT']['UserName']
Password = config['DEFAULT']['Password']
client = boto3.client("sns",aws_access_key_id=config['DEFAULT']['aws_access_key_id'],aws_secret_access_key=config['DEFAULT']['aws_secret_access_key'],region_name=config['DEFAULT']['region_name'])

sys.path.insert(0, VESYNCAPIPATH)
from pyvesync import VeSync

manager = VeSync(UserName, Password, time_zone=DEFAULT_TZ)
manager.login()
manager.update()

# Get energy usage data
manager.update_energy()

# Display outlet device information
for device in manager.outlets:
    ret = device.displayJSON()
   
    currentValue = float(ret['Power'])
    
    if(os.path.exists(ret['Device Name']+".txt") == False):
        print("File does not exist - creating with initial value.")
        f = open(ret['Device Name']+".txt", "w")
        f.write(str(currentValue))
        f.close()
        previousValue = currentValue
    else:
        f = open(ret['Device Name']+".txt", "r")
        previousValue = f.readline()

        previousValue = float(previousValue)
        f.close()
        f = open(ret['Device Name']+".txt", "w")
        print(str(datetime.datetime.now())+" " + ret['Device Name']+": Current = "+ str(currentValue) + ", Previous = "+str(previousValue))
        f.write(str(currentValue))
        f.close()
    
    if(previousValue<POWERTHRESHOLD and currentValue>POWERTHRESHOLD):
        print("Machine appears to have started")
        client.publish(PhoneNumber=config['DEFAULT']['PhoneNumber1'],Message=(config['DEFAULT']['StartMessage']).replace("plug",ret['Device Name']))
        client.publish(PhoneNumber=config['DEFAULT']['PhoneNumber2'],Message=(config['DEFAULT']['StartMessage']).replace("plug",ret['Device Name']))
    elif(previousValue>POWERTHRESHOLD and currentValue<POWERTHRESHOLD):
        print("Machine appears to have stopped")
        client.publish(PhoneNumber=config['DEFAULT']['PhoneNumber1'],Message=(config['DEFAULT']['CompleteMessage']).replace("plug",ret['Device Name']))
        client.publish(PhoneNumber=config['DEFAULT']['PhoneNumber2'],Message=(config['DEFAULT']['CompleteMessage']).replace("plug",ret['Device Name']))
    elif(previousValue<POWERTHRESHOLD and currentValue<POWERTHRESHOLD):
        print("Machine appears idle")
        
