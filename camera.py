#!/usr/bin/env python3
# ustat
# Last Edit: 5/6/2016; Chris Cox
# Edit Comments: 
#	1) Added global variable to change the time in between pictures
#	2) Added watch dog timer
#	3) Added correct bash command for python3
#	4) Added Debugging messages for monitor
#	5) Changed timer values
#	6) Added in dynamic threshold
#	7) prints for threshold included

from PIL import Image, ImageFilter, ImageChops
import picamera
import math, operator
import time
import requests
camera = picamera.PiCamera()

DELAY_RUN = 10 # 10 second delay in between pictures
DELAY_CALIBRATION = 10 # 10 second delay in between pictures
HEADERS = {'Auth':'8spWsLd38ji08Tpc'}

def main():
	try:
		# put all in a while loop, always wait for a signal to take another photo and process again
		watchDog_t = 0 # This is for the watchdog timer; Calibration Mode
		average_L = [] # Creating average list for dynamic threshold value
		total_L = 0 # Initalizing total value of list
		dynamic_threshold_val = 0 # Initializing value for dynamic threshold average value
		while (1):
			if watchDog_t < 8: # If FALSE; Stops posting the calibration picture after 2 minutes
				# ***Calibration Mode***
				time.sleep(DELAY_CALIBRATION) # Delay to take new pictures
				print ("Waited Ten Seconds For New Calibration")
				camera.capture('dump.jpg')
				time.sleep(3)
				camera.capture('orig.jpg') 
				time.sleep(3)
				camera.capture('update.jpg') # capture new image whenever there is a change

				img1 = Image.open('orig.jpg')
				img2 = Image.open('update.jpg')
				print ("Captured New Calibration Image")

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
					print("Check New Calibration Photo")
				except:
					print("Connection Failed: Check Server Status")
					continue
				watchDog_t += 1 # Increasing the watchdog timer value
			else:
				print ("Will Now Wait Ten Seconds")
				time.sleep(DELAY_RUN) # Delay to take new pictures
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

				# Grab last ten elements. Add all together then divide by 10 for average.  Now compare that to white 
				# pixels for dynamic threshold
				if len(average_L) < 10:
					average_L.append(white[0])
					print("Appended value to initial list : ", white[0])
				else: # This section will end up occuring everytime once list is full
					print("List size : ", len(average_L))
					average_L.popLeft()
					print("Popped value from list, new list : ", average_L)
					average_L.append(white[0])
					print("Appended to list : ", white[0])
					total_L = sum(average_L)
					print("total_L = ", total_L)
					dynamic_threshold_val = total_L / len(average_L)
					print("dynamic_threshold_val : ", dynamic_threshold_val)

				print ("Number of Black Pixels: ", black[0]) #number of black pixels
				print ("Number of White Pixels: ", white[0]) #number of white pixels
				myData = {'pixels': white[0], 'roomid':0}

				# The following try block makes sure the server is up and running to prevent program crashes
				try:
					rsp = requests.post('http://trambel.us/ustat/upload', data=myData, headers=HEADERS) # graph data
					print("Posted New Pixel Count To Server")
				except:
					print("Connection Failed: Check Server Status")
					continue

			watchDog_t += 1 # Increasing the watchdog timer value
	except KeyboardInterrupt:
		print ("keyboard interrupt")

if __name__ == '__main__':
	main()
