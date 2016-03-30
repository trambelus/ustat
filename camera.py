#!/usr/bin/env python
from PIL import Image, ImageFilter, ImageChops
import picamera
import math, operator
import time

camera = picamera.PiCamera()

def main():
	try:
		print('Inside of main')
		#testing
		#put all in a while loop, always wait for a signal to take another photo and process again
		while (1):
			#recv_data = 5
			print('Infinite while')
			# recv_data = ord(conn.recv(1))
			# print (recv_data)
			time.sleep(10) #for demo -- protoype should be per minute
			print ("Ten Seconds")
			camera.capture('dump.jpg')
			time.sleep(3)
			camera.capture('orig.jpg') 
			time.sleep(3)
			camera.capture('update.jpg') #capture new image whenever there is a change

			img1 = Image.open('orig.jpg')
			img2 = Image.open('update.jpg')

			print ("Captured Images")

			# toSend = img2.resize((400, 400), Image.ANTIALIAS)
			# toSend.save('latest.png')

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
			rsp = requests.post('http://trambel.us/ustat/upload', data=myData, headers=headers)
	except KeyboardInterrupt:
		print ("keyboard interrupt")

if __name__ == '__main__':
	main()
