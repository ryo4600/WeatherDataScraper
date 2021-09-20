import requests
from bs4 import BeautifulSoup
import datetime
import csv
from weather_models import PastWeatherData
from sqlite_access import SqliteAccess
#from postgres_access import PostgresAccess
import os

db_access = SqliteAccess(os.path.join(os.path.dirname(__file__), 'data', 'weather.sqlite3'))
#db_access = PostgresAccess(os.environ.get('POSTGRES_USER'), os.environ.get('POSTGRES_PASSWORD'), 'localhost')

def get_all_stations():
	"""	Get stationc codes from database
		It expects that there are data tables created with scrape_stations.py
	"""
	return db_access.get_all_stations()

def extractPastData(year:int, station_code:int):
	""" Scrape data from JMA by year and station"""
	area_code = db_access.get_area_code(station_code)
	rowsprocessed = 0
	data = []
	# January - December
	for month in range(1,13):
		r = requests.get(f"http://www.data.jma.go.jp/obd/stats/etrn/view/daily_s1.php?prec_no={area_code}&block_no={station_code}&year={year}&month={month}&day=1&view=p1")
		r.encoding = r.apparent_encoding

		soup = BeautifulSoup(r.text, "html.parser")
		rows = soup.findAll('tr',class_='mtx')
		if len(rows) == 0:
			continue

		# first 4 rows are headers, so we ignore them
		rows = rows[4:]

		# days
		for row in rows:
			data.append([area_code, station_code, year, month] + [str(dt.string).replace('--', '').replace('///', '').replace(']', '').replace(')', '').strip(' ') for dt in row.findAll('td')])
	
	return data

if __name__ == "__main__": 
	if os.path.exists('data') == False:
		os.mkdir('data')

	# arg1: target year
	# ex. year:2020,2019,2018
	# arg2: target station. all stations if not specified.
	# ex. code:48321,48322
	for arg in os.sys.argv:
		vals = arg.split(':')
		if len(vals) != 2:
			continue

		key = vals[0]
		value = vals[1]
		if key == 'year':
			vals = value.split('-')
			if len(vals) == 2:
				start = int(vals[0])
				end = int(vals[1])
				step = 1 if start < end else -1
				years = list(range(int(vals[0]),int(vals[1]), step))
			else:
				vals = value.split(',')
				years = [int(val) for val in vals]
		elif key == "code":
			vals = value.split(',')

			station_codes = [int(val) for val in vals]
	try:
		station_codes
	except:
		station_codes = get_all_stations()

	nStations = len(station_codes)
	
	for year in years:
		with open(f'data/weather_{year}.csv', 'w', newline='') as f:
			writer = csv.writer(f, lineterminator='\n')
			print(f"Year {year} started.")
			counter = 1
			for station_code in station_codes:
				print (f"{counter}/{nStations}: {station_code}", end='')
				data = extractPastData(year,station_code)
				print (f" ... done. {len(data)} rows. ")
				writer.writerows(data)
				counter += 1

	db_access.close()
