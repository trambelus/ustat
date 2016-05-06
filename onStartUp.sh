!/bin/sh
# onStartUp.sh
# Runs camera.py on start up by changing directories and then back to original dirSectory

cd /
cd home/pi/ustat
sudo python 3 camera.py
cd /