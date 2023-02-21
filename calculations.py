import math
import ephem
import datetime
from decimal import Decimal

import constants


def calculate_intensity(sun_altitude, cloud_cover, direction, sun_azimuth, data_sunset, data_sunrise):
    """
    Calculates the intensity of the light that enters through a window.
    This function calculates the intensity of sunlight that is shining
    through a window at a particular time, based on several input parameters.
    It takes the current time, sun altitude, cloud cover, direction of the window,
    sun azimuth, and sunrise/sunset times as inputs.

    The function first checks if the current time is before sunrise or after sunset,
    in which case the intensity will be zero. Otherwise, it calculates the distance
    between the window and the sun, and the angle between the direction of the window
    and the sun's position. It then calculates the area of the sky visible through
    the window and adjusts for any obstructions or limited visibility.
    Finally, it calculates the intensity of sunlight that is shining
    through the window using an exponential decay model based on the distance and cloud cover.
    The result is returned as the output of the function.
    """
    # An correction is needed because the answer comes in the previous hour
    current_time = datetime.datetime.now()
    correct_hour = (current_time + datetime.timedelta(hours=-1)).strftime('%Y-%m-%d %H:00:00')

    # Check if it's before sunrise or after sunset
    if correct_hour < data_sunrise or correct_hour > data_sunset:
        I = 0
        return I

    # Convert input values to Decimal as well
    sun_altitude = Decimal(str(sun_altitude))
    sun_azimuth = Decimal(str(sun_azimuth))
    direction = Decimal(str(direction))
    cloud_cover = Decimal(str(cloud_cover))

    # Calculate the distance from the window to the sun
    d = constants.EARTH_RADIUS * Decimal(math.tan(math.radians(float(sun_altitude))))

    # Calculate the solid angle of the sky visible from the window (sky_area)

    # Convert sun_altitude and direction-sun_azimuth to float in radians
    sun_altitude = float(sun_altitude)
    sun_azimuth = float(sun_azimuth)
    direction = float(direction)
    sun_altitude_rad = math.radians(sun_altitude)
    sun_azimuth_rad = math.radians(sun_azimuth)
    direction_rad = math.radians(direction)

    # Calculate the absolute value of the cosine of the angle between the sun and the direction
    cosine_altitude_rad = Decimal(math.cos(sun_altitude_rad))
    cosine_direction_azimuth_rad = Decimal(math.cos(direction_rad - sun_azimuth_rad))
    cos_theta = abs(cosine_altitude_rad * cosine_direction_azimuth_rad)
    r = Decimal('1') - Decimal(math.cos(math.radians(90 - math.degrees(math.asin(float(cos_theta))))))
    sky_area = Decimal('2') * Decimal('3.14159265358979323846') * r

    # Calculate the visibility factor, which depends on the area of the window and
    # the solid angle of the sky visible from the window
    V = constants.WINDOW_AREA / sky_area

    # Calculate the angle between the direction the window is facing and the position of the sun
    angle = abs(direction - sun_azimuth)
    if angle > 180:
        angle = 360 - angle
    angle_factor = (Decimal('180') - Decimal(angle)) / Decimal('180')

    # Calculate the intensity of the sunlight shining through the window
    exp_term = Decimal(constants.K / 100000) * Decimal(d) * (cloud_cover)

    intensity = constants.I0 * Decimal(math.exp(-exp_term)) * V * angle_factor
    return float(intensity)


def calculations(source_position, data_api):
    if source_position == "North":
        direction = constants.NORTH_DIR
    elif source_position == "West":
        direction = constants.WEST_DIR
    elif source_position == "South":
        direction = constants.SOUTH_DIR
    elif source_position == "East":
        direction = constants.EAST_DIR
    dwd_cloud_cover = data_api[0]

    # Cloud cover (as a fraction from 0 to 1)
    cloud_cover = dwd_cloud_cover / 100

    # Calculation of the position of the sun
    oslo = ephem.Observer()
    oslo.lat = str(constants.OSLO_LAT)
    oslo.lon = str(constants.OSLO_LON)
    oslo.elevation = constants.ELEVATION  # in meters
    dt = datetime.datetime.strptime(data_api[1], '%Y-%m-%d %H:%M:%S')
    oslo_date = '{}/{}/{} {}:{}:{}'.format(dt.day, dt.month, dt.year, dt.hour, dt.minute, dt.second)
    oslo.date = oslo_date
    sun = ephem.Sun()
    sun.compute(oslo)
    sun_altitude = math.degrees(sun.alt)
    sun_azimuth = math.degrees(sun.az)

    data_sunset = data_api[1]
    data_sunrise = data_api[2]

    intansity_lux = calculate_intensity(sun_altitude, cloud_cover, direction, sun_azimuth, data_sunset, data_sunrise)
    return intansity_lux
