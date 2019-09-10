import sys
import base64
import json
import sys
import configparser
import os.path
sys.path.insert(0, '..\pyvesync\src')

from pyvesync import VeSync

config = configparser.ConfigParser()
config.read('config.ini')

DEFAULT_TZ = config['DEFAULT']['DEFAULT_TZ']
POWERTHRESHOLD = float(config['DEFAULT']['PowerThreshold'])
UserName = config['DEFAULT']['UserName']
Password = config['DEFAULT']['Password']


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
        print(ret['Device Name']+": Current = "+ str(currentValue) + ", Previous = "+str(previousValue))
        f.write(str(currentValue))
        f.close()
    
    #if(previousValue<POWERTHRESHOLD and currentValue>POWERTHRESHOLD):
        #print("Machine appears to have started")
    #elif(previousValue>POWERTHRESHOLD and currentValue<POWERTHRESHOLD):
        #print("Machine appears to have stopped")
    #elif(previousValue<POWERTHRESHOLD and currentValue<POWERTHRESHOLD):
        #print("Machine appears idle")
        