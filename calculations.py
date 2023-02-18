import sqlite3
import arrow
import math
import ephem
import datetime
import pytz

import  CONSTANTS


def calculate_intensity(sun_altitude, cloud_cover, direction, sun_azimuth, data_sunset, data_sunrise):
        """
        'I' is the total light intensity entering the room through the window, in lux.

        2.This function uses the Beer-Lambert law:
        I = I0 * e^(-k * d),
        where I0 is the intensity of sunlight at the top of the atmosphere,
        K is the extinction coefficient, and d is the distance that the light
        has to travel through the atmosphere and clouds to reach the window.
        I0 = 1367  # Solar constant (W/m^2)
        K = 0.15  # Extinction coefficient for cloud cover

        This formula was modified:
        I = T *(I0 * e^(-k * dcloud_cover) * V),
        where
        T - the total transmittance of the window,
        V - the view factor. The function using
        the "Hottel-Whillier-Bliss" (HWB) method (the view factor 
        can be calculated based on the ratio of the window area 
        to the total area of the visible sky hemisphere). 

        2. The formula for the visible sky area from the geometry of a spherical surface.
        The full surface area of a sphere is given by 4pir^2, where r is the radius of the sphere.
        The visible sky area is then the portion of this surface area
        that is visible through the window, which is calculated as the area of
        a half-sphere (2pir^2) minus the area of the portion of the sphere that
        is blocked by the horizon (pir^2cos(angle)). 
        So this gives the visible sky area as a fraction of the total surface area
        of a hemisphere with a radius of 1 (since the actual radius
        of the hemisphere is not needed for the calculation). 

        """
        #now = datetime.datetime.now(pytz.UTC)
        now_time = '2023-02-18T00:15:19+00:00'
        now = datetime.datetime.strptime(now_time, '%Y-%m-%dT%H:%M:%S%z').replace(tzinfo=pytz.timezone('Europe/Oslo')).astimezone(pytz.UTC)
        sunset_time = datetime.datetime.strptime(data_sunset, '%Y-%m-%dT%H:%M:%S%z').replace(tzinfo=pytz.timezone('Europe/Oslo')).astimezone(pytz.UTC)
        sunrise_time = datetime.datetime.strptime(data_sunrise, '%Y-%m-%dT%H:%M:%S%z').replace(tzinfo=pytz.timezone('Europe/Oslo')).astimezone(pytz.UTC)
        # Check if it's before sunrise or after sunset
        if now < sunrise_time or now > sunset_time:
            I = 0
            return I
        
        d = CONSTANTS.ROOM_HEIGHT/ math.sin(math.radians(sun_altitude))

        angle = abs(direction - sun_azimuth)
        if angle > 180:
            angle = 360 - angle
        sky_area = 2 * math.pi * (1 - math.cos(math.radians(angle)))
        
        V = CONSTANTS.WINDOW_AREA / sky_area

        I = CONSTANTS.I0 * math.exp(- CONSTANTS.K * d * cloud_cover) * V
        print(I)
        return I
     

def calculations(source_position, data_api):

    if source_position == "North":
        direction = CONSTANTS.NORTH_DIR
    elif source_position == "West":
        direction = CONSTANTS.WEST_DIR
    elif source_position == "South":
         direction = CONSTANTS.SOUTH_DIR
    elif source_position == "East":
        direction = CONSTANTS.EAST_DIR
    dwd_cloud_cover = data_api[0]

    # Cloud cover (as a fraction from 0 to 1)
    cloud_cover = dwd_cloud_cover / 100

    # Calculation of the position of the sun
    oslo = ephem.Observer()
    oslo.lat = str(CONSTANTS.OSLO_LAT)  
    oslo.lon = str(CONSTANTS.OSLO_LON)
    oslo.elevation = CONSTANTS.ELEVATION  # in meters
    dt = datetime.datetime.strptime(data_api[1], '%Y-%m-%dT%H:%M:%S%z')
    oslo_date = '{}/{}/{} {}:{}:{}'.format(dt.day, dt.month, dt.year, dt.hour, dt.minute, dt.second)

    oslo.date = oslo_date
    sun = ephem.Sun()
    sun.compute(oslo)
    sun_altitude = math.degrees(sun.alt)
    sun_azimuth = math.degrees(sun.az)

    data_sunset = data_api[1]
    data_sunrise = data_api[2]

    intansity_lum = calculate_intensity(sun_altitude, cloud_cover, direction, sun_azimuth, data_sunset, data_sunrise)
    return intansity_lum
