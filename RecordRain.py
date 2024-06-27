#!/usr/bin/env python

# Import required libraries
import time
import RPi.GPIO as GPIO
import sqlite3
import datetime as datetime

#Database Schema
#BEGIN;
#CREATE TABLE rain (datetime TEXT, rain_count NUMERIC);
#COMMIT;

def sensorCallback(channel):
  # Called if sensor output changes
  if GPIO.input(channel):
        rain_count = 0
  else:
        rain_count = 1
        #Save to weatherdb database
        connection = sqlite3.connect("/media/WeatherPi/weatherdb")
        cursor = connection.cursor()

       #Build INSERT query
        now = datetime.datetime.now()
        sql = "INSERT INTO rain VALUES(" + "'"  + str(now.strftime("%Y-%m-%d %H:%M:%S")) + "', " + str(rain_count) + ")"
        cursor.execute(sql)
        connection.commit()
        cursor.close()
        connection.close()

def main():
  # Wrap main content in a try block so we can
  # catch the user pressing CTRL-C and run the
  # GPIO cleanup function. This will also prevent
  # the user seeing lots of unnecessary error
  # messages.

  # Get initial reading
  sensorCallback(26)

  try:
    # Loop until users quits with CTRL-C
    while True :
      time.sleep(0.1)

  except KeyboardInterrupt:
    # Reset GPIO settings
    GPIO.cleanup()

# Tell GPIO library to use GPIO references
GPIO.setmode(GPIO.BCM)

# Set Switch GPIO as input
# Pull high by default
GPIO.setup(26, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(26, GPIO.BOTH, callback=sensorCallback, bouncetime=200)

if __name__=="__main__":
   main()
