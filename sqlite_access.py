import sqlite3
import traceback
from weather_models import *

class SqliteAccess:

	def __init__(self, dbfile:str):
		self.conn = sqlite3.connect(dbfile)
	
	def close(self):
		self.conn.close()

	### Initialize DB (creating tables) ###
	def init_db(self):
		try:
			cur = self.conn.cursor()
			cur.execute('CREATE TABLE IF NOT EXISTS areas (code integer NOT NULL PRIMARY KEY, name varchar(50) NOT NULL)')
			cur.execute('CREATE TABLE IF NOT EXISTS stations (station_type integer NOT NULL, name varchar(50) NOT NULL, code integer NOT NULL PRIMARY KEY, yomi varchar(50) NOT NULL, latitude real NOT NULL, longitude real NOT NULL, elevation real NOT NULL, area_id integer NOT NULL REFERENCES areas (code) DEFERRABLE INITIALLY DEFERRED)')
			cur.execute('CREATE TABLE IF NOT EXISTS weatherdata("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "station_code" integer NOT NULL, "year" integer NOT NULL, "month" integer NOT NULL, "day" integer NOT NULL, "days_in_week" integer NOT NULL, "pressure_land" real NOT NULL, "pressure_sea" real NOT NULL, "rain_total" real NOT NULL, "rain_hour_max" real NOT NULL, "rain_10min_max" real NOT NULL, "temp_avg" real NOT NULL, "temp_high" real NOT NULL, "temp_low" real NOT NULL, "humid_avg" real NOT NULL, "humid_min" real NOT NULL, "wind_avg" real NOT NULL, "wind_max" real NOT NULL, "wind_dir" integer NOT NULL, "wind_peak_speed" real NOT NULL, "wind_peak_dir" integer NOT NULL, "sun_hours" real NOT NULL, "snow_total" real NOT NULL, "snow_depth" real NOT NULL, "summary_day" varchar(50) NOT NULL, "summary_night" varchar(50) NOT NULL);')
			self.conn.commit()
		except Exception as e:
			self.conn.rollback()
			print(f"creating database failed. {e}")
			raise e

	def write_areas(self, areas: [AreaInfo]):
		try:
			cur = self.conn.cursor()
			for area in areas:
				sql = f"INSERT INTO areas (code, name) VALUES ({area.code}, '{area.name}') ON CONFLICT (code) DO UPDATE SET name = '{area.name}'"
				cur.execute(sql)
			
			self.conn.commit()
		except Exception as e:
			self.conn.rollback()
			print(f"writing areas failed. {e}")
			raise e

	def write_stations(self, stations: [StationInfo]):
		try:
			cur = self.conn.cursor()
			for station in stations:
				stype = 0 if station.station_type == 's' else 1
				sql = f"INSERT INTO stations (station_type, area_id, code, name, yomi, latitude, longitude, elevation)"  \
					+ f" VALUES ({stype}, {station.area}, {station.code}, '{station.name}', '{station.yomi}', {station.latitude}, {station.longitude}, {station.elevation})" \
					+ f" ON CONFLICT (code) DO UPDATE SET station_type ={stype}, area_id={station.area}, name ='{station.name}', yomi='{station.yomi}', latitude={station.latitude}, longitude={station.longitude}, elevation={station.elevation}"
				cur.execute(sql)
			
			self.conn.commit()
		except Exception as e:
			self.conn.rollback()
			print(f"writing stations failed. {e}")
			raise e
	
	def get_all_stations(self):
		cur = self.conn.cursor()
		sql = f"SELECT code FROM stations WHERE station_type=0"
		cur.execute(sql)
		rows = cur.fetchall()
		stations = []
		for row in rows:
			stations.append(int(row[0]))
		return stations

	def get_all_amedas_stations(self):
		cur = self.conn.cursor()
		sql = f"SELECT code FROM stations WHERE station_type=1"
		cur.execute(sql)
		rows = cur.fetchall()
		stations = []
		for row in rows:
			stations.append(int(row[0]))
		return stations

	def get_area_code(self, station_code:int):
		cur = self.conn.cursor()
		sql = f"SELECT area_id FROM stations WHERE code={station_code}"
		cur.execute(sql)
		return cur.fetchone()[0]

	def write_weathers(self, wds: [PastWeatherData], year):
		cur = self.conn.cursor()
		try:
			counter = 0
			sql = f"DELETE FROM weatherdata WHERE year={year}"
			cur.execute(sql)
			vals = [(wd.year, wd.month , wd.day, wd.station_code, wd.days_in_week, 
					wd.pressure_land, wd.pressure_sea, wd.rain_total, wd.rain_hour_max, wd.rain_10min_max, \
					wd.temp_avg, wd.temp_high, wd.temp_low, wd.humid_avg, wd.humid_min, \
					wd.wind_avg, wd.wind_max, wd.wind_dir, wd.wind_peak_speed, wd.wind_peak_dir, \
					wd.sun_hours, wd.snow_total, wd.snow_depth, wd.summary_day, wd. summary_night) for wd in wds]
			sql = f"INSERT INTO weatherdata (year, month, day, station_code, days_in_week, " \
				+ f"pressure_land, pressure_sea, rain_total, rain_hour_max, rain_10min_max," \
				+ f"temp_avg, temp_high, temp_low, humid_avg, humid_min," \
				+ f"wind_avg, wind_max, wind_dir, wind_peak_speed, wind_peak_dir," \
				+ f"sun_hours, snow_total, snow_depth, summary_day, summary_night" \
				+ ")" \
				+ f"VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
			cur.executemany(sql, vals)

			self.conn.commit()
		except:
			self.conn.rollback()
			traceback.print_exc()
			raise
			
