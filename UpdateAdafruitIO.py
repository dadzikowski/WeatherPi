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
from Adafruit_IO import RequestError, Client, Feed

#Query database for data 
connection = sqlite3.connect("/media/WeatherPi/weatherdb")
cursor = connection.cursor()

sql = "SELECT AqPM10, AqPM2_5 FROM weather ORDER BY datetime DESC LIMIT 1"
cursor.execute(sql)
record = cursor.fetchone()
AqPM10 = record[0]
AqPM2_5 = record[1]
LastUpdate = datetime.now()
LastUpdate = LastUpdate.strftime("%m/%d/%Y, %H:%M:%S")
#UV = record[2]
#baromin = record[3]
#dailyrainin = record[4]
#dewptf = record[5]
#humidity = record[6]
#solarradiation = record[7]
#tempf = record[8]
#windspeedmph = record[9]

cursor.close()
connection.close()

#Post to io.adafruit.com
ADAFRUIT_IO_USERNAME = "USERNAME"
ADAFRUIT_IO_KEY = "PASSWORD"

aio = Client(ADAFRUIT_IO_USERNAME, ADAFRUIT_IO_KEY)

aiofeed = aio.feeds('aqpm10')
aio.send_data(aiofeed.key, str(AqPM10))
aiofeed = aio.feeds('aqpm2-5')
aio.send_data(aiofeed.key, str(AqPM2_5))
aiofeed = aio.feeds('lastupdate')
aio.send_data(aiofeed.key, str(LastUpdate))
#aiofeed = aio.feeds('uv')
#aio.send_data(aiofeed.key, str(UV))
#aiofeed = aio.feeds('baromin')
#aio.send_data(aiofeed.key, str(baromin))
#aiofeed = aio.feeds('dailyrainin')
#aio.send_data(aiofeed.key, str(dailyrainin))
#aiofeed = aio.feeds('dewptf')
#aio.send_data(aiofeed.key, str(dewptf))
#aiofeed = aio.feeds('humidity')
#aio.send_data(aiofeed.key, str(humidity))
#aiofeed = aio.feeds('solarradiation')
#aio.send_data(aiofeed.key, str(solarradiation))
#aiofeed = aio.feeds('tempf')
#aio.send_data(aiofeed.key, str(tempf))
#aiofeed = aio.feeds('windspeedmph')
#aio.send_data(aiofeed.key, str(windspeedmph))
