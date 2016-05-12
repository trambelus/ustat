#!/bin/env python3
# ip_log.py
# Created By: Chris Cox
# Date: 5/11/2016
# Logs the IP Address of the RPI and if it changes it stores the next IP Address. To Ensure DHCP is working correctly

import netifaces as ni
import time

IPLOGFILE = 'IP_Address_File.log' # Holds the logged IP Addresses
DELAY = 20 # 20 second delay to check IP Address; DHCP lease is 10800 second

# Defining global variables
IP_ADDRESS = '0.0.0.0' # Current IP Address
INITIAL_IP = '1.1.1.1' # Initial IP Adress

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
	global INITIAL_IP
	IPLog("Gathering IP Address...")
	IPLog("Initial IP Address Acquired")
	INITIAL_IP = getIPAddress()
	time.sleep(DELAY)

def checkIP():
	global IP_ADDRESS
	time.sleep(DELAY)
	IP_ADDRESS = getIPAddress()
	if str(IP_ADDRESS) != str(INITIAL_IP):
		IPLog("NEW IP : ", IP_ADDRESS)

def main():
	try:
		time.sleep(100) # Delaying Initial start of the program in order for RPI to get IP ADDRESS
		initIP()
		while True:
			checkIP()
	except KeyboardInterrupt:
		print ("keyboard interrupt")

if __name__ == '__main__':
	main()