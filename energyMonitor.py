import sys
import base64
import json
import sys
import configparser
import os.path
import datetime
import time
import boto3
from influxdb import InfluxDBClient
from datetime import timedelta

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

client = InfluxDBClient('192.168.1.235', 8086, '', '', 'EnergyMonitor')

# Display outlet device information
for device in manager.outlets:
    ret = device.displayJSON()

    currentValue = float(ret['Power'])
    currentTime = datetime.datetime.now().timestamp()
    json_body = [
        {
            "measurement": "Wattage",
            "tags": {
                "device": ret['Device Name']
            },
            "time": datetime.datetime.now(),
            "fields": {
                "value": currentValue
            }
        }
    ]
    client.write_points(json_body)
    print(str(datetime.datetime.now())+" " + ret['Device Name']+": Current = "+ str(currentValue))

    #Get the older values from the DB (if they even exist)
    PreviousQueryDates = (datetime.datetime.now() - timedelta(minutes=5))
    q1 = 'SELECT "value" FROM "EnergyMonitor"."autogen"."Wattage" WHERE time > ' + "'"+ str(PreviousQueryDates)+"' and device='"+ret['Device Name']+"'"
    res = client.query(q1)
	
    Counter=0
    PreviousValuesAboveThreshold=False
    CountOfPointsAboveThreshold=0
    CountOfPointsBelowThreshold=0
    print(ret['Device Name']+":")
    for point in res.get_points():
        print("\t" + str(point['time'])+": Value = "+ str(point["value"]))

        if(point["value"] >  POWERTHRESHOLD):
            PreviousValuesAboveThreshold = True
            CountOfPointsAboveThreshold = CountOfPointsAboveThreshold + 1
        else:
            PreviousValuesAboveThreshold = False
            CountOfPointsBelowThreshold = CountOfPointsBelowThreshold + 1
        Counter = Counter+1
    
    
    print(str(Counter) + " previous values found in the past 5 minutes")

    if(PreviousValuesAboveThreshold == True and currentValue < POWERTHRESHOLD and CountOfPointsBelowThreshold > 3):
        print("Machine is confirmed off for the past 5 minutes worth of checks")
	