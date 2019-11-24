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
from datetime import datetime

config = configparser.ConfigParser()
config.read('config.ini')

DEFAULT_TZ = config['DEFAULT']['DEFAULT_TZ']
VESYNCAPIPATH = config['DEFAULT']['VESYNCAPIPATH']
POWERTHRESHOLD = float(config['DEFAULT']['PowerThreshold'])
InfluxDBIP = str(config['DEFAULT']['InfluxDBIP'])
UserName = config['DEFAULT']['UserName']
Password = config['DEFAULT']['Password']
botoclient = boto3.client("sns",aws_access_key_id=config['DEFAULT']['aws_access_key_id'],aws_secret_access_key=config['DEFAULT']['aws_secret_access_key'],region_name=config['DEFAULT']['region_name'])
OutletsToProcess = config['DEFAULT']['OutletsToProcess'].split(",")

sys.path.insert(0, VESYNCAPIPATH)
from pyvesync import VeSync

manager = VeSync(UserName, Password, time_zone=DEFAULT_TZ)
manager.login()
manager.update()

# Get energy usage data
manager.update_energy()

client = InfluxDBClient(InfluxDBIP, 8086, '', '', 'EnergyMonitor')

# Display outlet device information
for device in manager.outlets:
    ret = device.displayJSON()
    print("Checking if array contians " + ret['Device Name'])
    if(ret['Device Name'] in OutletsToProcess):
        currentValue = float(ret['Power'])
        
        json_body = [
            {
                "measurement": "Wattage",
                "tags": {
                    "device": ret['Device Name']
                },
                "time": datetime.utcnow(),
                "fields": {
                    "value": currentValue
                }
            }
        ]
        client.write_points(json_body)
        print(str(datetime.utcnow())+" " + ret['Device Name']+": Current = "+ str(currentValue))

        #Get the older values from the DB (if they even exist)
        PreviousQueryDates = (datetime.utcnow() - timedelta(minutes=6))
        q1 = 'SELECT "value" FROM "EnergyMonitor"."autogen"."Wattage" WHERE time > ' + "'"+ str(PreviousQueryDates)+"' and device='"+ret['Device Name']+"'"
        #Test Values
        #PreviousQueryDates = (datetime(2019,9,23,15,8,6) - timedelta(minutes=6))
        #q1 = 'SELECT "value" FROM "EnergyMonitor"."autogen"."Wattage" WHERE time > ' + "'"+ str(PreviousQueryDates)+"' and time <= '"+ str(datetime(2019,9,23,15,8,10)) +"'and device='"+ret['Device Name']+"'"
        
        res = client.query(q1)
        
        Counter=0
        PreviousValuesAboveThreshold=False
        CountOfPointsAboveThreshold=0
        CountOfPointsBelowThreshold=0
        print(ret['Device Name']+":")
        col = []
        
        for point in res.get_points():
            col.append(point['value'])
            print("\t" + str(point['time'])+": Value = "+ str(point["value"]))

            if(point["value"] >  POWERTHRESHOLD):
                PreviousValuesAboveThreshold = True
                CountOfPointsAboveThreshold = CountOfPointsAboveThreshold + 1
            else:
                PreviousValuesAboveThreshold = False
                CountOfPointsBelowThreshold = CountOfPointsBelowThreshold + 1
            Counter = Counter+1
        
        print("\t"+str(col))
        size = len(col)
        if(size > 5):
            if((col[size-1] < POWERTHRESHOLD and col[size-2] < POWERTHRESHOLD and col[size-3] < POWERTHRESHOLD and col[size-4] < POWERTHRESHOLD and col[size-5] < POWERTHRESHOLD) and (col[0] > POWERTHRESHOLD or col[1] > POWERTHRESHOLD or col[2] > POWERTHRESHOLD or col[3] > POWERTHRESHOLD)):
                print("Current values are below, and former values were above. Safe to say it stopped")
                for number in config['DEFAULT']['PhoneNumber'].split(","):
                    botoclient.publish(PhoneNumber=number,Message=(config['DEFAULT']['CompleteMessage']).replace("plug",ret['Device Name']))
        
        
        
        print("\n\t**Count Above Thresold: "+str(CountOfPointsAboveThreshold))
        print("\t**Count Below Thresold: "+str(CountOfPointsBelowThreshold))
        print(str(Counter) + " previous values found in the past 5 minutes")

        if(PreviousValuesAboveThreshold == True and currentValue < POWERTHRESHOLD and CountOfPointsBelowThreshold > 3):
            print("Machine is confirmed off for the past 5 minutes worth of checks")
        