# WeatherPi

Built my own weather station that uploads observations to Weather Underground. Currently collects the following observations:

_**3D Printed Parts**_
These were gathered mainly from Thingiverse. I added attribution as appropriate. For the pole mounts, I resized these to fit my printed parts (since the mounts weren't designed for these components)
1) 

_**Hardware**_
1) **Controller** -- RaspberryPi Zero W (used 2 because solar radiation/air quality sensors are in a different enclosure from the rest of the weather station).
3) **Temperature, Humidity, Pressure, Altitude, Dew Point** -- BME280
4) **Wind Direction** -- 12-Bit Hall Angle Sensor, 0.088° Resolution, 360° Rotation, 0-5V Output 
5) **Anemometer (wind speed sensor)** --  A3144/OH3144/AH3144E Hall Effect Sensor
6) **Rain Bucket** -- LM393 Speed Measuring Module Tacho Sensor Slot Type IR Optocoupler
7) **UV Solar Radiation** -- Adafruit 1918 Analog UV Light Sensor Breakout - GUVA-S12SD
8) **PM1.0, PM2.5 and PM10.0 Concentration (air quality)** -- Adafruit PMSA003I Air Quality Breakout - STEMMA QT
9) **Analog-to-Digital ADC Converter** -- ADS1115 4 Channel 16 Bit 16 Byte I2C IIC ADC Module with Pro Gain Amplifier
