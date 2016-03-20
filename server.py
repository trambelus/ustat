#!/usr/bin/env python3

from flask import Flask, request, flash, redirect,  render_template, url_for, abort
from pprint import pprint
import hashlib
import sqlite3
import time
import shelve

app = Flask(__name__)
app.secret_key = 'vOaZrSbR8ZIpCAeU'

with open('data.csv','r') as f:
	csvdata = f.read()
csvdata = csvdata.replace('\n','\\n')

@app.route('/')
def main():
	return None

@app.route('/ustat/upload', methods=['GET','POST'])
def upload():
	return None

@app.route('/favicon.ico')
def favicon():
	return url_for('static',filename='favicon.ico')

@app.route('/ustat', methods=['GET','POST'])
def rooms():
	if request.method == 'POST':
		with open('hash.txt','r') as f:
			hash_s = f.readlines()[0]

		hash_f = hashlib.new('sha256')
		hash_f.update(bytes(request.form['password'],'UTF-8'))

		if hash_f.hexdigest() != hash_s:
			return render_template('index.html',error='Invalid password')

		flash('Authentication successful')

	return render_template('index.html', csvdata=csvdata)

def main():
	app.run(host='0.0.0.0', port=80, debug=True)

if __name__ == '__main__':
	main()
