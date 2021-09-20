import urllib.request, urllib.parse
import requests
import csv
from bs4 import BeautifulSoup
import os
import re
from weather_models import AreaInfo, StationInfo
from sqlite_access import SqliteAccess

###########################################################
## Scrape station codes and write into DB
###########################################################
class WeatherStationsScraper:
	def __init__(self):
		pass
	
	# get prefectures / regions
	def getPrefectures(self):
		url = 'https://www.data.jma.go.jp/obd/stats/etrn/select/prefecture00.php?prec_no=&block_no=&year=&month=&day=&view='
		html = urllib.request.urlopen(url)
		soup = BeautifulSoup(html, 'html.parser')
		elements = soup.find_all('area')
		return [AreaInfo(element['alt'], self.extractAreaNo(element['href'])) for element in elements]
		
	def extractAreaNo(self, href):
		qs = urllib.parse.urlparse(href).query
		qs_d = urllib.parse.parse_qs(qs)
		return int(qs_d['prec_no'][0])

	# retrieve station info from area info
	def getStations(self, area_code):
		url = '{}{}'.format('https://www.data.jma.go.jp/obd/stats/etrn/select/prefecture.php?prec_no=', area_code)
		html = urllib.request.urlopen(url)
		soup = BeautifulSoup(html, 'html.parser')
		elements = soup.find_all('area')

		out = list()
		for element in elements[0::2]:
			# parse station code
			qs = urllib.parse.urlparse(element['href']).query
			qs_d = urllib.parse.parse_qs(qs)
			station_code = -1
			if qs_d.__contains__('block_no') == False or element.has_attr('onmouseover') == False:
				continue
			station_code = int(qs_d['block_no'][0])

			# get other information
			station_type, _, kanji_name, hiragana_name, lat_int, lat_dec, lon_int, lon_dec, elev, *rest = self.extractStationInfo(element['onmouseover'])

			station = StationInfo(station_type, \
								area_code, \
								station_code, \
								kanji_name, \
								hiragana_name, \
								float(lat_int) + float(lat_dec) / 60, \
								float(lon_int) + float(lon_dec) / 60, \
								float(elev))

			out.append(station)
		return out
	
	def extractStationInfo(self, onmouseover):
		reg_ex = re.compile('javascript:viewPoint\((.*)\)')
		matched = reg_ex.search(onmouseover)
		test = list(matched[1].split(','))
		vals = list(map(lambda val: val.strip('\''), matched[1].split(',')))
		return vals


if __name__ == '__main__':
	if os.path.exists('data') == False:
		os.mkdir('data')

	db_name = os.path.join(os.path.dirname(__file__), 'data', 'weather.sqlite3')

	scraper = WeatherStationsScraper()
	db_access = SqliteAccess(db_name)
	try:
		db_access.init_db()
		
		areas = scraper.getPrefectures()
		db_access.write_areas(areas)

		for area in areas:
			print("extracting area {}".format(area.name))
			stations = scraper.getStations(area.code)
			db_access.write_stations(stations)
	finally:
		db_access.close()
