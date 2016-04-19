#!/usr/bin/env python
# ustat
# Last Edit: 4/13/2016; Chris Cox
# Edit Comments: 
#	1) Added global variable to change the time in between pictures
#	2) 

from PIL import Image, ImageFilter, ImageChops
import picamera
import math, operator
import time
import requests
camera = picamera.PiCamera()

DELAY_RUN = 60 # 60 second delay in between pictures
DELAY_CALIBRATION = 10 # 10 second delay in between pictures

def main():
	try:
		# put all in a while loop, always wait for a signal to take another photo and process again
		watchDog_t = 0 # This is for the watchdog timer; Calibration Mode
		while (1):
			if watchDog_t < 61: # If FALSE; Stops posting the calibration picture after 10 minutes
				# ***Calibration Mode***
				time.sleep(DELAY_CALIBRATION) # Delay to take new pictures
				print ("Ten Seconds")
				camera.capture('dump.jpg')
				time.sleep(3)
				camera.capture('orig.jpg') 
				time.sleep(3)
				camera.capture('update.jpg') # capture new image whenever there is a change

				img1 = Image.open('orig.jpg')
				img2 = Image.open('update.jpg')
				print ("Captured Images")

				img1 = img1.filter(ImageFilter.FIND_EDGES)
				img1.save('orig.jpg')
				img2 = img2.filter(ImageFilter.FIND_EDGES)
				img2.save('update.jpg')

				headers = {'Auth':'8spWsLd38ji08Tpc'}

				toSend = img2.resize((400, 400), Image.ANTIALIAS)
				toSend.save('latest.png')
				calPicture = {'calibration': open('latest.png','rb')}
				rsp = requests.post('http://trambel.us/ustat/calibrate', files=calPicture, headers=headers) # calibration mode
			else:
				time.sleep(DELAY_RUN) # Delay to take new pictures
				print ("Sixty Seconds")
				camera.capture('dump.jpg')
				time.sleep(3)
				camera.capture('orig.jpg') 
				time.sleep(3)
				camera.capture('update.jpg') # capture new image whenever there is a change

				img1 = Image.open('orig.jpg')
				img2 = Image.open('update.jpg')
				print ("Captured Images")

				img1 = img1.filter(ImageFilter.FIND_EDGES)
				img1.save('orig.jpg')
				img2 = img2.filter(ImageFilter.FIND_EDGES)
				img2.save('update.jpg')

				diff = ImageChops.subtract(img2, img1)
				diff.save('diff.jpg')

				diff = Image.open("diff.jpg").convert('1')
				black, white = diff.getcolors()

				print (black[0]) #number of black pixels
				print (white[0]) #number of white pixels

				headers = {'Auth':'8spWsLd38ji08Tpc'}
				myData = {'pixels': white[0], 'roomid':0}

				rsp = requests.post('http://trambel.us/ustat/upload', data=myData, headers=headers) # graph data

			watchDog_t += 1 # Increasing the watchdog timer value
	except KeyboardInterrupt:
		print ("keyboard interrupt")

if __name__ == '__main__':
	main()
