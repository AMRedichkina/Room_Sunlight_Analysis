import math
import ephem
import datetime

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

    # Calculate the distance from the window to the sun
    d = constants.WINDOW_HEIGHT / math.sin(math.radians(sun_altitude))

    # Calculate the solid angle of the sky visible from the window
    cos_theta = abs(math.cos(math.radians(sun_altitude)) * math.cos(math.radians(direction - sun_azimuth)))
    sky_area = 2 * math.pi * (1 - math.cos(math.radians(90 - math.degrees(math.asin(cos_theta)))))
    # Calculate the visibility factor, which depends on the area of the window and
    # the solid angle of the sky visible from the window
    V = constants.WINDOW_AREA / sky_area
    if V > constants.MAX_VISABILITY_THROUGHT_WINDOW:
        V = constants.MAX_VISABILITY_THROUGHT_WINDOW

    # Calculate the angle between the direction the window is facing and the position of the sun
    angle = abs(direction - sun_azimuth)
    if angle > 180:
        angle = 360 - angle
    angle_factor = (180 - angle) / 180

    # Calculate the intensity of the sunlight shining through the window
    I = constants.I0 * math.exp(- constants.K * d * cloud_cover) * V * angle_factor

    return I


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
