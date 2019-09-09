import sys
import base64
import sys
import configparser
sys.path.insert(0, '..\pyvesync\src')
print(sys.path)
from pyvesync import VeSync

config = configparser.ConfigParser()
config.read('config.ini')

DEFAULT_TZ = config['DEFAULT']['DEFAULT_TZ']
UserName = config['DEFAULT']['UserName']
Password = config['DEFAULT']['Password']
print(DEFAULT_TZ)
print(UserName)
print(Password)

manager = VeSync(UserName, Password, time_zone=DEFAULT_TZ)
manager.login()
manager.update()

# Get energy usage data
manager.update_energy()

# Display outlet device information
for device in manager.outlets:
    ret = device.displayJSON()
    print(ret)