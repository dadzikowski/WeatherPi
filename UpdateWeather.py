#!/usr/bin/env python

#Imports
import sqlite3
import board
from datetime import datetime, timedelta, date
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
from requests import Session, Request
import requests

#Database Schema
#BEGIN;
#CREATE TABLE weather (datetime TEXT, winddir NUMERIC, windspeedmph NUMERIC, windgustmph NUMERIC, windgustdir NUMERIC, windspdmph_avg2m NUMERIC, winddir_avg2m NUMERIC, windgustmph_10m NUMERIC,
#windgustdir_10m NUMERIC, humidity NUMERIC, dewptf NUMERIC, tempf NUMERIC, rainin NUMERIC, dailyrainin NUMERIC, baromin NUMERIC, UV NUMERIC, solarradiation NUMERIC, AqPM2_5 NUMERIC, AqPM10 NUMERIC, wuresponse TEXT);
#COMMIT;

#Altitude, Temp, Humidity, DewPt, Pressure from  BME280
from adafruit_bme280 import basic as adafruit_bme280
i2c = board.I2C()  # uses board.SCL and board.SDA
bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c, 0x76)

#Wind Ddirection
i2c = busio.I2C(board.SCL, board.SDA)

ads = ADS.ADS1115(i2c)
Wind_Direction_Sensor = AnalogIn(ads, ADS.P0)

#Read initial values and convert as needed
now = datetime.now()
tempf = (bme280.temperature * (9/5)) + 32 #C to F conversion formula: (0°C × 9/5) + 32
altitude = bme280.altitude
humidity = bme280.humidity
dewptf = (bme280.temperature - ((100 - bme280.humidity)/5)) * (9/5) + 32 #Dewpt = Temp_C - ((100 - Humidity)/5)
baromin = (bme280.pressure / 33.863886666667) * (293/(293 - (856 * 0.0065))) #Converted hectopascal to inchs of mercury with constant 33.863886666667. The calculation of sea level pressure involves correcting the observed pressure to the pressure that would exist at sea level. The formula for this correction is: PSL = P × 293⁄(293 - h × 0.0065) Where: PSL is the sea level pressure (in hPa or inHg). P is the observed pressure at the given altitude (in hPa or inHg). h is the altitude above sea level (in meters or feet).
winddir = Wind_Direction_Sensor.voltage * (360/4.096) #4.096 max value
windspeedmph = 0
windgustmph = 0
windgustdir = 0
windspdmph_avg2m = 0
winddir_avg2m = 0
windgustmph_10m = 0 
windgustdir_10m = 0
rainin = 0
dailyrainin = 0

#Query database for 60 min rain data
#Funnel diameter = 79.97509999 mm
#Funnel Area = (pi) 3.14 * (r^2) 1599.004155 
#XXmm caused X bucket tips
#XXmm/Funnel Area = 0.010117762

connection = sqlite3.connect("/media/WeatherPi/weatherdb")
cursor = connection.cursor()
datetime_10 = datetime.now() - timedelta(minutes=10)
sql = "SELECT sum(rain_count) from rain WHERE datetime > '" +  str(datetime_10) + "'"
cursor.execute(sql)
record = cursor.fetchone()
rain_count = record[0]

if rain_count is None:
      rainin = 0
else:
     #Record rain per hour. Note that multiply bucket by 2 to align with other weather stations in Westerville 
     rainin = (60 / 10) * (rain_count * 0.0147 * 2)

cursor.close()
connection.close()

#Query database for daily rain data
connection = sqlite3.connect("/media/WeatherPi/weatherdb")
cursor = connection.cursor()
current_date = date.today()
sql = "SELECT sum(rain_count) from rain WHERE DATE(datetime) = '" + str(current_date) + "'"
cursor.execute(sql)
record = cursor.fetchone()
rain_count = record[0] 

if rain_count is None:
      dailyrainin = 0
else:
     dailyrainin = rain_count * 0.0147 * 2

cursor.close()
connection.close()

#Query database for windspeedmph
connection = sqlite3.connect("/media/WeatherPi/weatherdb")
cursor = connection.cursor()

sql = "SELECT max(datetime), wind_count from wind"
cursor.execute(sql)
record = cursor.fetchone()
wind_count = record[1]

if wind_count is None:
      wind_count = 0
else:
#Calculate the circumference of your anemometer by multiplying the diameter (or distance between opposing scoops) in feet times pi (or 3.14).
#Multiply this number times the number of revolutions per minute to get the number of feet per minute (fpm) one scoop travels.
#By multiplying rpm by 60 (minutes per hour) and dividing this number by 5280 (feet per mile), you will get an approximate wind speed in miles per hour.
     windspeedmph = (float(wind_count) * 0.11)

cursor.close()
connection.close()

#Query database for windgustmph/windgustdir -- today
connection = sqlite3.connect("/media/WeatherPi/weatherdb")
cursor = connection.cursor()

sql = "SELECT max(wind_count), winddir_avg from wind WHERE DATE(`datetime`) = date('now')"
cursor.execute(sql)
record = cursor.fetchone()
wind_count = record[0]
winddir_avg = record[1]

if wind_count is None:
      wind_count = 0
      windgustdir = 0
else:
     windgustmph = (float(wind_count) * 0.11)
     windgustdir = winddir_avg
cursor.close()
connection.close()

#Query database for windspdmph_avg2m/winddir_avg2m
connection = sqlite3.connect("/media/WeatherPi/weatherdb")
cursor = connection.cursor()

datetime_2 = datetime.now() - timedelta(minutes=2)

sql = "SELECT avg(wind_count), avg(winddir_avg) from wind WHERE datetime > '" +  str(datetime_2) + "'"
cursor.execute(sql)
record = cursor.fetchone()
wind_count = record[0]
winddir_avg = record[1]

if wind_count is None:
      wind_count = 0
      winddir_avg2m = 0
else:
     windspdmph_avg2m = (float(wind_count) * 0.11)
     winddir_avg2m = winddir_avg

cursor.close()
connection.close()

#Query database for windgustmph_10m/windgustdir_10m 
connection = sqlite3.connect("/media/WeatherPi/weatherdb")
cursor = connection.cursor()

datetime_10 = datetime.now() - timedelta(minutes=10)

sql = "SELECT avg(wind_count), avg(winddir_avg) from wind WHERE datetime > '" +  str(datetime_10) + "'"
cursor.execute(sql)
record = cursor.fetchone()
wind_count = record[0]
winddir_avg = record[1]

if wind_count is None:
      wind_count = 0
      windgustdir_10m = 0
else:
     windgustmph_10m = (float(wind_count) * 0.11)
     windgustdir_10m = winddir_avg

cursor.close()
connection.close()

#Query database for air data 
connection = sqlite3.connect("/media/WeatherPi/weatherdb")
cursor = connection.cursor()

sql = "SELECT UV, solarradiation, AqPM2_5, AqPM10 from air ORDER BY datetime DESC LIMIT 1"
cursor.execute(sql)
record = cursor.fetchone()
UV = record[0]
solarradiation = record[1]
AqPM2_5 = record[2]
AqPM10 = record[3]

cursor.close()
connection.close()

#Post to Weather Underground
url = "https://weatherstation.wunderground.com/weatherstation/updateweatherstation.php?"

#Adding a payload
payload = {
    'ID': 'ID', 
    'PASSWORD': 'PASSWORD',
    'action': 'updateraw',
    'dateutc': 'now',
    'winddir': str(winddir),
    'windspeedmph': str(windspeedmph),
    'windgustmph': str(windgustmph),
    'windgustdir': str(windgustdir),
    'windspdmph_avg2m': str(windspdmph_avg2m),
    'winddir_avg2m': str(winddir_avg2m),
    'windgustmph_10m': str(windgustmph_10m),
    'windgustdir_10m': str(windgustdir_10m),
    'rainin': str(rainin),
    'dailyrainin': str(dailyrainin),
    'humidity': str(humidity),
    'dewptf': str(dewptf),
    'tempf': str(tempf),
    'baromin': str(baromin),
    'UV': str(UV),
    'solarradiation': str(solarradiation),
    'AqPM2_5': str(AqPM2_5),
    'AqPM10': str(AqPM10)
}

#Post to Weather Underground
wuresponse = requests.get(url, payload)

#Save to weatherdb database
connection = sqlite3.connect("/media/WeatherPi/weatherdb")
cursor = connection.cursor()

#Build INSERT query
sql = "INSERT INTO weather VALUES(" + "'" +  str(now.strftime("%Y-%m-%d %H:%M:%S")) + "', " + str(winddir) + ", " + str(windspeedmph) + ", " + str(windgustmph) + ", " + str(windgustdir) + ", " + str(windspdmph_avg2m) + ", " + str(winddir_avg2m) + ", " + str(windgustmph_10m) + ", " + str(windgustdir_10m) + ", " + str(humidity) + ", " + str(dewptf) + ", " + str(tempf) + ", " + str(rainin) + ", " + str(dailyrainin) + ", " + str(baromin) + ", " + str(UV) + ", " + str(solarradiation) + ", " + str(AqPM2_5) + ", " + str(AqPM10) + ", '" + wuresponse.text + "')"
cursor.execute(sql)
connection.commit()
cursor.close()
connection.close()
