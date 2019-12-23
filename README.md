# EnergyMon

sudo apt-get update;sudo apt-get upgrade
git clone https://github.com/sth2258/EnergyMon.git
git clone https://github.com/markperdue/pyvesync.git
sudo apt-get install python3-pip
pip3 install boto3
pip3 install influxdb
cp EnergyMon/config.template.ini EnergyMon/config.ini
echo ""|
(crontab -l 2>/dev/null; echo "* * * * * cd ~pi/EnergyMon;python3 energyMonitor.py > /dev/null 2>&1") | crontab -
# edit config.ini; set VESYNCAPIPATH to Linux path, aws_access_key_id, aws_secret_access_key, PhoneNumber, UserName, Password


curl -sL https://repos.influxdata.com/influxdb.key | sudo apt-key add -
echo "deb https://repos.influxdata.com/debian $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/influxdb.list
sudo apt-get update
sudo apt-get update
sudo apt-get install telegraf influxdb chronograf kapacitor