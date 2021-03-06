#!/usr/bin/env python3
# ustat
# Last Edit: 5/11/2016; Chris Cox

from PIL import Image, ImageFilter, ImageChops
import picamera
import math, operator
import time
import requests
camera = picamera.PiCamera()

LOGFILE = 'camera_py.log'
DELAY_RUN = 10 # 10 second delay in between pictures
DELAY_CALIBRATION = 10 # 10 second delay in between pictures
HEADERS = {'Auth':'8spWsLd38ji08Tpc'}
AVERAGE_L = [] # Creating average list for dynamic threshold value
TOTAL_L = 0 # Initalizing total value of list
DYNAMIC_THRESHOLD_VAL = 0 # Initializing value for dynamic threshold average value

# Credits to log : John McDouall
def log(*msg):
	"""
	Prepends a timestamp and prints a message to the console and LOGFILE
	"""
	output = "%s:\t%s" % (time.strftime("%Y-%m-%d %X"), ' '.join(msg))
	print(output)
	with open(LOGFILE, 'a') as f:
		f.write(output + '\n')

# Grab last ten elements. Add all together then divide by 10 for average.  Now compare that to white 
# pixels for dynamic threshold
def thresholdCalc(white_edge):
	if len(AVERAGE_L) < 10:
		AVERAGE_L.append(white_edge)
		log("Appended value to initial list : ", str(white_edge))
		return white_edge
	else: # This section will end up occuring everytime once list is full
		#print("List size : ", len(AVERAGE_L))
		#print("List : ", *AVERAGE_L, sep=', ')
		AVERAGE_L.pop(0)
		#print("Popped value from list, new list : ", AVERAGE_L)
		AVERAGE_L.append(white_edge)
		#print("Appended to list : ", white_edge)
		TOTAL_L = sum(AVERAGE_L)
		#print("total_L = ", TOTAL_L)
		DYNAMIC_THRESHOLD_VAL = TOTAL_L / len(AVERAGE_L)
		log("dynamic_threshold_val : ", str(DYNAMIC_THRESHOLD_VAL))
		return DYNAMIC_THRESHOLD_VAL

# Calculate the room determiend value (RDV).
# This is done using the dynamic threshold value minus the current white pixel value
def roomDeterminedValue(thresholdValue, white_pixels):
	RDV = thresholdValue - white_pixels
	return RDV

# This handles the calibration image for the user which can be viewed @ trambel.us/ustat/calibrate
def calibrationMode():
	time.sleep(DELAY_CALIBRATION) # Delay to take new pictures
	log("Waited Ten Seconds For New Calibration")

	camera.capture('dump.jpg')
	time.sleep(3)
	camera.capture('orig.jpg') 
	time.sleep(3)
	camera.capture('update.jpg') # capture new image whenever there is a change
	img1 = Image.open('orig.jpg')
	img2 = Image.open('update.jpg')
	log("Captured New Calibration Image")

	img1 = img1.filter(ImageFilter.FIND_EDGES)
	img1.save('orig.jpg')
	img2 = img2.filter(ImageFilter.FIND_EDGES)
	img2.save('update.jpg')
	toSend = img2.resize((400, 400), Image.ANTIALIAS)
	toSend.save('latest.png')
	calPicture = {'calibration': open('latest.png','rb')}

	# The following try block makes sure the server is up and running to prevent program crashes
	try:
		rsp = requests.post('http://trambel.us/ustat/calibrate', files=calPicture, headers=HEADERS) # calibration mode
		log("Check New Calibration Photo")
	except:
		log("Connection Failed: Check Server Status")
		pass

# This handles the image detection for the graph which can be viewed @ trambel.us/ustat
def cameraRun():
	log("Will Now Wait Ten Seconds")
	time.sleep(DELAY_RUN) # Delay to take new pictures
	camera.capture('dump.jpg')
	time.sleep(3)
	camera.capture('orig.jpg') 
	time.sleep(3)
	camera.capture('update.jpg') # capture new image whenever there is a change
	img1 = Image.open('orig.jpg')
	img2 = Image.open('update.jpg')
	log("Captured Images")

	img1 = img1.filter(ImageFilter.FIND_EDGES)
	img1.save('orig.jpg')
	img2 = img2.filter(ImageFilter.FIND_EDGES)
	img2.save('update.jpg')
	diff = ImageChops.subtract(img2, img1)
	diff.save('diff.jpg')
	diff = Image.open("diff.jpg").convert('1')
	black, white = diff.getcolors()
	finalThresholdValue = thresholdCalc(white[0]) # Calling thresholdCalc()
	log("finalThresholdValue : ", str(finalThresholdValue))
	RDVtoPost = roomDeterminedValue(finalThresholdValue, white[0]) # Getting the value to post to the view
	log("RDVtoPost : ", str(RDVtoPost))
	log("Number of Black Pixels: ", str(black[0]))
	log("Number of White Pixels: ", str(white[0]))
	myData = {'pixels': RDVtoPost, 'roomid':0}

	# The following try block makes sure the server is up and running to prevent program crashes
	try:
		rsp = requests.post('http://trambel.us/ustat/upload', data=myData, headers=HEADERS) # graph data
		log("Posted New Pixel Count To Server")
	except:
		log("Connection Failed: Check Server Status")
		pass

def main():
	try:
		# put all in a while loop, always wait for a signal to take another photo and process again
		watchDog_t = 0 # This is for the watchdog timer; Calibration Mode
		log("Preparing Camera...")
		while (1):
			if watchDog_t < 8: # If FALSE; Stops posting the calibration picture after 2 minutes
				# ***Calibration Mode***
				calibrationMode()
				watchDog_t += 1 # Increasing the watchdog timer value
			else:
				# ***Camera Run Mode ***
				cameraRun()
				watchDog_t += 1 # Increasing the watchdog timer value
	except KeyboardInterrupt:
		print ("keyboard interrupt")

if __name__ == '__main__':
	main()
