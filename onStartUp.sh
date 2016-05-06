#!/bin/sh
# onStartUp.sh
# Created By: Chris Cox
# Date: 5/6/2016
# Runs camera.py on start up by changing directories and then back to original dirSectory

cd /
cd home/pi/ustat
sudo python3 camera.py
cd /