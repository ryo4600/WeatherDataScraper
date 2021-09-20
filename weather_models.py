import datetime

# Prefectures/Areas
class AreaInfo():
	def __init__(self, area_name, prec_no):
		self.name = area_name
		self.code = int(prec_no)

	def __str__(self):
		return f'{self.area_name}, {self.prec_no}'

# weather stations
class StationInfo():
	def __init__(self, station_type, area, code, name, yomi, latitude, longitude, elevation):
		self.station_type = station_type # 'a' = amedas only, 's' = normal
		self.area = int(area)
		self.code = int(code)
		self.name = name
		self.yomi = yomi
		self.latitude = latitude
		self.longitude = longitude
		self.elevation = elevation

class PastWeatherData():
	def __init__(self):
		self.station_code: int = 0
		self.year: int = 0
		self.month: int = 0
		self.day: int = 0
		self.days_in_week: int = 0
		self.pressure_land: float = 0.0
		self.pressure_sea: float = 0.0
		self.rain_total: float = 0.0
		self.rain_hour_max: float = 0.0
		self.rain_10min_max: float = 0.0
		self.temp_avg: float = 0.0
		self.temp_high: float = 0.0
		self.temp_low: float = 0.0
		self.humid_avg: float = 0.0
		self.humid_min: float = 0.0
		self.wind_avg: float = 0.0
		self.wind_max: float = 0.0
		self.wind_dir: int = 0
		self.wind_peak_speed: float = 0.0
		self.wind_peak_dir: int = 0
		self.sun_hours: float = 0.0
		self.snow_total: float = 0.0
		self.snow_depth: float = 0.0
		self.summary_day: str = ""
		self.summary_night: str = ""

	@property
	def id(self):
	    return  int(f"{self.year:}{self.month:02}{self.day:02}{self.station_code}")

	def days_in_week(self):
		return datetime.datetime(self.year, self.month, self.day).weekday()



