#!/usr/bin/env python3

from flask import Flask, request, flash, redirect,  render_template, url_for, abort
from pprint import pprint
import hashlib
import sqlite3
import time
import shelve

import testgen

DB_NAME = 'ustat.db3'

app = Flask(__name__)
app.secret_key = 'vOaZrSbR8ZIpCAeU'

with open('data.csv','r') as f:
	csvdata = f.read()
csvdata = csvdata.replace('\n','\\n')

# Connects to the database. Creates it if it needs to.
def init_db():
	db = sqlite3.connect(DB_NAME)
	db.execute("""CREATE TABLE IF NOT EXISTS stats (
		timestamp DATE,
		pixels INT,
		roomid INT
	)""")
	return db

def get_csv(period='total'):
	db = init_db()
	
	if period == 'total':
		res = db.execute("""SELECT timestamp, pixels FROM stats""").fetchall()
	elif period == 'day':
		res = db.execute("""
			SELECT z.hour,
			100*CAST(a.N AS FLOAT)/T sun,
			100*CAST(b.N AS FLOAT)/T mon,
			100*CAST(c.N AS FLOAT)/T tue,
			100*CAST(d.N AS FLOAT)/T wed,
			100*CAST(e.N AS FLOAT)/T thu,
			100*CAST(f.N AS FLOAT)/T fri,
			100*CAST(g.N AS FLOAT)/T sat
			FROM (
				  (SELECT STRFTIME('%H',timestamp) hour, SUM(pixels) N FROM stats
				    GROUP BY hour) z
			  	LEFT JOIN
				  (SELECT STRFTIME('%H',timestamp) hour, SUM(pixels) N FROM stats
				    AND STRFTIME('%w',timestamp) = '1' GROUP BY hour) a
				ON (z.hour = a.hour)
			  	LEFT JOIN
				  (SELECT STRFTIME('%H',timestamp) hour, SUM(pixels) N FROM stats
				    AND STRFTIME('%w',timestamp) = '2' GROUP BY hour) b
				ON (z.hour = b.hour)
			  	LEFT JOIN
				  (SELECT STRFTIME('%H',timestamp) hour, SUM(pixels) N FROM stats
				    AND STRFTIME('%w',timestamp) = '3' GROUP BY hour) c
				ON (z.hour = c.hour)
			  	LEFT JOIN
				  (SELECT STRFTIME('%H',timestamp) hour, SUM(pixels) N FROM stats
				    AND STRFTIME('%w',timestamp) = '4' GROUP BY hour) d
				ON (z.hour = d.hour)
			  	LEFT JOIN
				  (SELECT STRFTIME('%H',timestamp) hour, SUM(pixels) N FROM stats
				    AND STRFTIME('%w',timestamp) = '5' GROUP BY hour) e
				ON (z.hour = e.hour)
			  	LEFT JOIN
				  (SELECT STRFTIME('%H',timestamp) hour, SUM(pixels) N FROM stats
				    AND STRFTIME('%w',timestamp) = '6' GROUP BY hour) f
				ON (z.hour = f.hour)
			  	LEFT JOIN
				  (SELECT STRFTIME('%H',timestamp) hour, SUM(pixels) N FROM stats
				    AND STRFTIME('%w',timestamp) = '0' GROUP BY hour) g
				ON (z.hour = g.hour)
			  	LEFT JOIN
				  (SELECT COUNT(*) T FROM stats)
			)
			""").fetchall()
	elif period == 'week':
		pass

	csv = '\n'.join([','.join(map(str,c)) for c in res])
	csv = 'date,pixels\n' + csv
	csv = csv.replace('\n','\\n')
	return csv

@app.route('/')
def main():
	return 'Hi!'

@app.route('/ustat/upload', methods=['GET','POST'])
def upload():
	if request.method == 'POST':

		db = init_db()
		timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
		pixels = request.form['pixels']
		roomid = request.form['roomid']
		db.execute("""INSERT INTO stats (timestamp, pixels, roomid)
			VALUES (?, ?, ?)""", (timestamp, pixels, roomid))
		db.commit()
		db.close()
		return 'Success'

	elif request.method == 'GET':
		abort(403)

@app.route('/ustat/calibrate', methods=['GET','POST'])
def calibration():
	if request.method == 'POST':
		# Uploading calibration image
		print("calibrate: "  + str(request.files))
		if 'calibration' in request.files:
			recv_file = request.files['file']
			filename = 'calibration.png'
			recv_file.save('static/%s' % filename)
			return "Upload successful"
		abort(400)

	elif request.method == 'GET':
		return render_template('calibration.html', filename='calibration.png')

@app.route('/favicon.ico')
def favicon():
	return url_for('static',filename='favicon.ico')

@app.route('/ustat', methods=['GET','POST'])
def rooms():
	# if request.method == 'POST':
	# 	with open('hash.txt','r') as f:
	# 		hash_s = f.readlines()[0]

	# 	hash_f = hashlib.new('sha256')
	# 	hash_f.update(bytes(request.form['password'],'UTF-8'))

	# 	if hash_f.hexdigest() != hash_s:
	# 		return render_template('index.html',error='Invalid password')

	# 	flash('Authentication successful')

	#csv_total = get_csv()
	# with open('data.csv','r') as f:
	# 	csvdata = f.read()
	# csvdata = csvdata.replace('\n','\\n')
	#return render_template('index.html', csv_total=csv_total)
	return testgen.render()

def main():
	try:
		app.run(host='0.0.0.0', port=80, debug=False)
	except OSError:
		app.run(host='0.0.0.0', port=9861, debug=False)

if __name__ == '__main__':
	main()

# Pareto distribution for test data generation:
# [[i,j,sum([par((abs(i-13+random.randint(-1,3))+0.5)/2)-((j==0 or j==6)*5)>1.5
#  for _ in range(120)])] for i in range(24) for j in range(7)]