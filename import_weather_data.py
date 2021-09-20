import requests
from bs4 import BeautifulSoup
import datetime
import csv
from weather_models import PastWeatherData
#from postgres_access import PostgresAccess
#from mysql_access import MySqlAccess
from sqlite_access import SqliteAccess
import os
import re

regex = re.compile('[0-9]+\.*[0-9]*')

def str2float(str_data, default):
	try:
		return float(str_data)
	except:
		mo = regex.search(str_data)
		if mo == None:
			return default
		return float(mo.group())

db_access = SqliteAccess(os.path.join(os.path.dirname(__file__), 'data', 'weather.sqlite3'))
#db_access = PostgresAccess(os.environ.get('POSTGRES_USER'), os.environ.get('POSTGRES_PASSWORD'), 'localhost')
#db_access = MySqlAccess(os.environ.get('MYSQL_USER'), os.environ.get('MYSQL_PASSWORD'), 'localhost')

"""
  Convert a direction string to a code
"""
def direction(name:str):

	if(name == '北'):
		return 0
	elif(name == '北北東'):
		return 1
	elif(name == '北北東'):
		return 2
	elif(name == '北東'):
		return 3
	elif(name == '東北東'):
		return 4
	elif(name == '東'):
		return 5
	elif(name == '東南東'):
		return 6
	elif(name == '南東'):
		return 7
	elif(name == '南南東'):
		return 8
	elif(name == '南'):
		return 9
	elif(name == '南南西'):
		return 10
	elif(name == '南西'):
		return 11
	elif(name == '西南西'):
		return 12
	elif(name == '西'):
		return 13
	elif(name == '西北西'):
		return 14
	elif(name == '西北'):
		return 15
	elif(name == '北北西'):
		return 16
	else:
		return -1

def processRow(data):
	# 0: area_code, 1: station_code, 2: year, 3: month
    # 4: day, 4: pressure(land, hPa), 6: pressure(land, hPa), 
    # 7: total precipitaion (mm), 8: max precip. per hour, 9: max precip. per 10 min
    # 10: avg temperature(degree), 11: highest temp, 12: lowest temp
    # 13: avg humidity(%), 14: min humidity
    # 15: avg wind velocity(m/s), 16: max wind velo. 17: direction of max wind velo, 
    # 18: max peak wind velocity(m/s), 19: direction of max peak wind velocity
    # 20: hours of sunshine(h), 21: total snow (cm), 22: max snow depth,
    # 23: day summary (6:00-18:00), 24: night summary (6:00-18:00)

	wd = PastWeatherData()

	# area_code = int(data[0]) ... ignore
	wd.station_code = int(data[1])
	wd.year = int(data[2])
	wd.month = int(data[3])
	wd.day =int(data[4])
	wd.pressure_land = str2float(data[5], "-1")
	wd.pressure_sea = str2float(data[6], "-1")
	wd.rain_total = str2float(data[7], "-1")
	wd.rain_hour_max = str2float(data[8], "-1")
	wd.rain_10min_max = str2float(data[9], "-1")
	wd.temp_avg = str2float(data[10], "0")
	wd.temp_high = str2float(data[11], "0")
	wd.temp_low = str2float(data[12], "0")
	wd.humid_avg = str2float(data[13], "-1")
	wd.humid_min = str2float(data[14], "-1")
	wd.wind_avg = str2float(data[15], -1)
	wd.wind_max = str2float(data[16], -1)
	wd.wind_dir = direction(data[17])
	wd.wind_peak_speed = str2float(data[18], -1)
	wd.wind_peak_dir = direction(data[19])
	wd.sun_hours = str2float(data[20], -1)
	wd.snow_total = str2float(data[21], -1)
	wd.snow_depth = str2float(data[22], -1)
	wd.summary_day = data[23]
	wd.summary_night = data[24]

	return wd
    #self.db_access.write_weather(wd)


if __name__ == "__main__": 
	if os.path.exists('data') == False:
		os.mkdir('data')

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
  
	try:
		for year in years:
			with open(f'data/weather_{year}.csv', 'r', newline='') as f:
				reader = csv.reader(f)
				print(f"extracting data for {year} started.")
				wds = []
				counter = 1
				for row in reader:
					wds.append(processRow(row))
					print(f'\r{counter}', end='')
					counter += 1
				print(f"\rYear {year} completed. {len(wds)} rows")
				print('writing to DB', end='')
				db_access.write_weathers(wds, year)
				print('... done')
	finally:
		db_access.close()
