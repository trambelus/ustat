#!/bin/sh
# onStartUp.sh
# Created By: Chris Cox
# Date: 5/6/2016
# Runs camera.py on start up by changing directories and then back to original dirSectory

# Sends this device's local wlan0 IP address to the PiSSH server, and clears it on shutdown.
ipaddr=$(ifconfig eth0 | awk '/inet addr/{{print substr($2,6)}}')
echo "onStartUp.sh: Sending IP $ipaddr to server"

cd /
cd home/pi/ustat
sudo python3 camera.py &  # Starts camera.py and runs it in the background
sudo python3 ip_log.py &  # Starts ip_log.py and runs it in the background
cd /