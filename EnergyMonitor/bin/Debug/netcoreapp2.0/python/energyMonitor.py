import sys
import base64
import sys
sys.path.insert(0, 'pyvesync')
from pyvesync import VeSync

DEFAULT_TZ = 'America/New_York'
UserName = sys.argv[1]
UserName1 = 'steve.t.haber+vesync@gmail.com'
Password = base64.b64decode(sys.argv[2])
Password1 = 'cSG__("Fp5rb-895'

manager = VeSync(UserName1, Password1, time_zone=DEFAULT_TZ)
manager.login()
manager.update()

# Get energy usage data
manager.update_energy()

# Display outlet device information
for device in manager.outlets:
    device.display2()