#!/bin/env python3
# ip_log.py
# Created By: Chris Cox
# Date: 5/11/2016
# Logs the IP Address of the RPI and if it changes it stores the next IP Address. To Ensure DHCP is working correctly

import netifaces as ni
import time

IPLOGFILE = 'IP_Address_File.log' # Holds the logged IP Addresses
IP_ADDRESS = '0.0.0.0' # Current IP Address
INITIAL_IP = '1.1.1.1' # Initial IP Adress
DELAY = 20 # 20 second delay to check IP Address

# Returns current IP Address
def getIPAddress():
	ni.ifaddresses('eth0')
	IP = ni.ifaddresses('eth0')[2][0]['addr']
	IPLog('Current IP Address : ', str(IP))
	return IP

# Logs the current IP Address and prints it to the screen
def IPLog(*msg):
	output = "%s:\t%s" % (time.strftime("%Y-%m-%d %X"), ' '.join(msg))
	print(output)
	with open(IPLOGFILE, 'a') as f:
		f.write(output + '\n')

def initIP():
	IPLog("Gathering IP Address...")
	IPLog("Initial IP Address Acquired")
	INITIAL_IP = getIPAddress()
	IP_ADDRESS = INITIAL_IP
	time.sleep(DELAY)

def checkIP():
	time.sleep(DELAY)
	if IP_ADDRESS is not INITIAL_IP:
		IP_ADDRESS = getIPAddress()
		IPLog("NEW IP : ", IP_ADDRESS)

def main():
	try:
		initIP()
		while True:
			checkIP()
	except KeyboardInterrupt:
		print ("keyboard interrupt")

if __name__ == '__main__':
	main()