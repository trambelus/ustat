#!/usr/bin/env python3

# Pareto distribution for test data generation:
# [[i,j,sum([par((abs(i-13+ri(-1,3))+0.5)/2)-((j==0 or j==6)*5)>1.5
#  for _ in range(120)])] for i in range(24) for j in range(7)]

import sqlite3
from random import randint as ri, paretovariate as par
import time
import webbrowser
from datetime import timedelta, datetime



hours = [
	( -4, 1), # 5
	( -6, 2), # 6
	( -6, 3), # 7
	( -8,10), # 8
	(-10,14), # 9
	(-10,18), # 10
	(-20,28), # 11
	(-18,16), # 12
	( -9,22), # 13
	(-20,24), # 14
	(-20,30), # 15
	(-20,26), # 16
	(-20,20), # 17
	(-20,18), # 18
	(-20,19), # 19
	(-20,12), # 20
	(-16, 6), # 21
	(-16, 4), # 22
	(-16, 2), # 23
	(-12, 4), # 0
	(-16, 1), # 1
	(-16, 1), # 2
	(-16, 1), # 3
	(-12, 1), # 4
]

def render():

	events = [(ri(9,17),ri(0,4)) for _ in range(4)]
	print(events)

	def daterange(start_date, end_date):
	    for n in range(int((end_date - start_date).days)):
	        yield start_date + timedelta(minutes=5)

	db = sqlite3.connect('test_db.db3')
	db.execute("DROP TABLE IF EXISTS stats;")
	db.execute("""CREATE TABLE stats (
		timestamp DATE,
		pixels INTEGER,
		roomid INTEGER );
	""")

	c_date = datetime(2016, 1, 1)
	end_date = datetime(2016, 1, 15)
	pixels = ri(1,1500)
	pixels = 0

	while c_date < end_date:
		timestamp = c_date.strftime("%Y-%m-%d %H:%M:%S")
		c_date = c_date + timedelta(minutes=5)
		minmax = [h if c_date.weekday() < 5 else int(h*0.4) for h in hours[c_date.hour]]
		if (c_date.hour, c_date.weekday()) in events:
			minmax[1] *= 2

		if pixels > 400:
			pixels -= 15

		pixels += ri(*minmax)
		if pixels < 0:
			pixels *= -1
		db.execute("""INSERT INTO stats (timestamp, pixels, roomid)
			VALUES (?,?,?);""",(timestamp,pixels+ri(-10,10),0))

	db.commit()

	res = db.execute("""SELECT timestamp, pixels FROM stats""").fetchall()
	csv_linear = str([["Date.parse(\"{}\")".format(tup[i]) if i == 0 else tup[i]
		for i in range(len(tup))] for tup in res]).replace("'","")
	#print(csv_linear)


	res = db.execute("""
		SELECT CAST(z.hour AS INTEGER),
		a.N sun,
		b.N mon,
		c.N tue,
		d.N wed,
		e.N thu,
		f.N fri,
		g.N sat
		FROM (
			  (SELECT STRFTIME('%H',timestamp) hour, SUM(pixels) N FROM stats
			    GROUP BY hour) z
		  	LEFT JOIN
			  (SELECT STRFTIME('%H',timestamp) hour, SUM(pixels) N FROM stats
			    WHERE STRFTIME('%w',timestamp) = '1' GROUP BY hour) a
			ON (z.hour = a.hour)
		  	LEFT JOIN
			  (SELECT STRFTIME('%H',timestamp) hour, SUM(pixels) N FROM stats
			    WHERE STRFTIME('%w',timestamp) = '2' GROUP BY hour) b
			ON (z.hour = b.hour)
		  	LEFT JOIN
			  (SELECT STRFTIME('%H',timestamp) hour, SUM(pixels) N FROM stats
			    WHERE STRFTIME('%w',timestamp) = '3' GROUP BY hour) c
			ON (z.hour = c.hour)
		  	LEFT JOIN
			  (SELECT STRFTIME('%H',timestamp) hour, SUM(pixels) N FROM stats
			    WHERE STRFTIME('%w',timestamp) = '4' GROUP BY hour) d
			ON (z.hour = d.hour)
		  	LEFT JOIN
			  (SELECT STRFTIME('%H',timestamp) hour, SUM(pixels) N FROM stats
			    WHERE STRFTIME('%w',timestamp) = '5' GROUP BY hour) e
			ON (z.hour = e.hour)
		  	LEFT JOIN
			  (SELECT STRFTIME('%H',timestamp) hour, SUM(pixels) N FROM stats
			    WHERE STRFTIME('%w',timestamp) = '6' GROUP BY hour) f
			ON (z.hour = f.hour)
		  	LEFT JOIN
			  (SELECT STRFTIME('%H',timestamp) hour, SUM(pixels) N FROM stats
			    WHERE STRFTIME('%w',timestamp) = '0' GROUP BY hour) g
			ON (z.hour = g.hour)
		)
	""").fetchall()

	#print(res)
	mm = max([max(r) for r in res])/100
	csv_heatmap = [[i[0], j, i[j+1]/mm] for i in res for j in range(len(i)-1)]
	#print(csv_heatmap)

	with open("templates/index.html",'r') as f:
		html = f.read()
		html = html.replace("{{ csv_linear }}", str(csv_linear))
		html = html.replace("{{ csv_heatmap }}", str(csv_heatmap))
		#csv_heatmap = [[i,j,sum([par((abs(i-13+ri(-1,3))+0.5)/2)-((j>=5)*5)>1.5 for _ in range(120)])] for i in range(24) for j in range(7)]
		
	db.close()
	return html
	
if __name__ == "__main__":
	html = render()
	with open("temp.html",'w') as g:
		g.write(html)
	webbrowser.open_new_tab("temp.html")