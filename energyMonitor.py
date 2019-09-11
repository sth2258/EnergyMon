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
    previousValue1 = float(ret['Power'])
    previousValue2 = float(ret['Power'])
    
    
    if(os.path.exists(ret['Device Name']+".txt") == False):
        print("File does not exist - creating with initial value.")
        f = open(ret['Device Name']+".txt", "w")
        f.write(str(currentValue)+"-"+str(currentValue))
        f.close()
        previousValue1 = currentValue
        previousValue2 = currentValue
    else:
        #First, read operation to get the previous two values
        f = open(ret['Device Name']+".txt", "r")
        fileContents = f.readline()
        splitLine = fileContents.split("-")
        previousValue1 = float(splitLine[0])
        previousValue2 = float(splitLine[1])
        f.close()
        
        #Second, write operation to write current plus the newer of the previous values (previousValue1)
        f = open(ret['Device Name']+".txt", "w")
        print(str(datetime.datetime.now())+" " + ret['Device Name']+": Current = "+ str(currentValue) + ", Previous1 = "+str(previousValue1)+ ", Previous2 = "+str(previousValue2))
        f.write(str(currentValue)+"-"+str(previousValue1))
        f.close()
    
    if(previousValue1<POWERTHRESHOLD and previousValue2<POWERTHRESHOLD and currentValue>POWERTHRESHOLD):
        print(str(datetime.datetime.now())+" " +ret['Device Name']+" appears to have started")
        for number in config['DEFAULT']['PhoneNumber'].split(","):
            client.publish(PhoneNumber=number,Message=(config['DEFAULT']['StartMessage']).replace("plug",ret['Device Name']))
    elif(previousValue2>POWERTHRESHOLD and previousValue1<POWERTHRESHOLD and currentValue<POWERTHRESHOLD):
        print(str(datetime.datetime.now())+" " +ret['Device Name']+" appears to have stopped")
        for number in config['DEFAULT']['PhoneNumber'].split(","):
            client.publish(PhoneNumber=number,Message=(config['DEFAULT']['StartMessage']).replace("plug",ret['Device Name']))
    else:
        print(str(datetime.datetime.now())+" " +ret['Device Name']+" appears idle")
        
