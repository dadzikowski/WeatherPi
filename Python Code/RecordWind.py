#!/usr/bin/env python

#Import required libraries
import time
import RPi.GPIO as GPIO
import sqlite3
import datetime as datetime
import busio
import board
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

#Database Schema
#BEGIN;
#CREATE TABLE wind (datetime TEXT, wind_count NUMERIC, winddir_avg NUMERIC);
#COMMIT;

#Initialize wind_count and winddir_sum
wind_count = 0
winddir_sum = 0

def sensorCallback(channel):
  #Called if sensor output changes
      global wind_count
      global winddir_sum
      if GPIO.input(channel):
         ignore = 0
      else:
         wind_count = wind_count + 1
         winddir_sum = winddir_sum + (Wind_Direction_Sensor.voltage * (360/4.096)) #4.096 max value

def main():
  #Wrap main content in a try block so we can
  #catch the user pressing CTRL-C and run the
  #GPIO cleanup function. This will also prevent
  #the user seeing lots of unnecessary error
  #messages.

  #Get initial reading
  sensorCallback(17)

  #Set current_time
  current_time = time.time()

  #Initialize wind_count  
  global wind_count
  global winddir_sum

  try:
    #Loop until users quits with CTRL-C
    while True :
      time.sleep(0.1)
      if time.time() - current_time < 60:
         ignore = 0
      else:
         #Save to weatherdb database
         connection = sqlite3.connect("/media/WeatherPi/weatherdb")
         cursor = connection.cursor()

         #Build INSERT query
         if wind_count == 0:
             winddir_avg = Wind_Direction_Sensor.voltage * (360/4.096) #4.096 max value
         else:
             winddir_avg  =  winddir_sum / wind_count
         now = datetime.datetime.now()
         sql = "INSERT INTO wind VALUES(" + "'"  + str(now.strftime("%Y-%m-%d %H:%M:%S")) + "', " + str(wind_count) + ", " + str(winddir_avg) + ")"
         cursor.execute(sql)
         connection.commit()
         cursor.close()
         connection.close()
         wind_count = 0
         winddir_sum = 0
         current_time = time.time()

  except KeyboardInterrupt:
    # Reset GPIO settings
    GPIO.cleanup()

#Tell GPIO library to use GPIO references
GPIO.setmode(GPIO.BCM)

#Set Switch GPIO as input
#Pull high by default
GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(17, GPIO.BOTH, callback=sensorCallback, bouncetime=200)

#Wind Ddirection
i2c = busio.I2C(board.SCL, board.SDA)

ads = ADS.ADS1115(i2c)
Wind_Direction_Sensor = AnalogIn(ads, ADS.P0)

if __name__=="__main__":
   main()
