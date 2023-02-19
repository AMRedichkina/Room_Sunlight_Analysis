import arrow
import requests
import json
import sqlite3
import pandas as pd
import datetime

from secret import API_KEY
import CONSTANTS


def data_request():
    # Cloud data request
    current_time = arrow.now().floor('hour')
    response_cloud = requests.get(
         'https://api.stormglass.io/v2/weather/point',
    params={
        'lat': CONSTANTS.OSLO_LAT,
        'lng': CONSTANTS.OSLO_LON,
        'start': current_time.to('UTC').timestamp(),  # Convert to UTC timestamp
        'end': current_time.to('UTC').timestamp(),  # Convert to UTC timestamp
        'params': ','.join(['cloudCover']),
    },
    headers={
        'Authorization': API_KEY
    }
    )
    json_data_cloud = response_cloud.json()

    # Sunrise and sunset query
    start = arrow.now().floor('day')
    end = arrow.now().shift(days=1).floor('day')
    response_astronomy = requests.get(
        'https://api.stormglass.io/v2/astronomy/point',
    params={
        'lat': CONSTANTS.OSLO_LAT,
        'lng': CONSTANTS.OSLO_LON,
        'start': start.to('UTC').timestamp(),  # Convert to UTC timestamp
        'end': end.to('UTC').timestamp(),  # Convert to UTC timestamp
    },
    headers={
        'Authorization': API_KEY
    }
    )
    
    json_data_astronomy = response_astronomy.json()
    print(json_data_cloud)
    print(json_data_astronomy)
    
    data_cloud = json_data_cloud['hours'][0]['cloudCover']['dwd'] # Output: 95.01
    
    time_request = json_data_cloud['hours'][0]['time'] # Output: "2023-02-17T23:00:00+00:00"
    datetime_request = datetime.datetime.strptime(time_request, '%Y-%m-%dT%H:%M:%S%z')
    time_request_str = datetime_request.strftime('%Y-%m-%d %H:%M:%S')

    data_sunset = json_data_astronomy['data'][0]['sunset'] # Output: "2023-02-18T16:15:19+00:00"
    datetime_sunset = datetime.datetime.strptime(data_sunset, '%Y-%m-%dT%H:%M:%S%z')
    time_sunset_str = datetime_sunset.strftime('%Y-%m-%d %H:%M:%S')

    data_sunrise = json_data_astronomy['data'][0]['sunrise'] # Output: "2023-02-18T06:49:30+00:00"
    datetime_sunrise = datetime.datetime.strptime(data_sunrise, '%Y-%m-%dT%H:%M:%S%z')
    time_sunrise_str = datetime_sunrise.strftime('%Y-%m-%d %H:%M:%S')

    db_create(time_request_str, data_cloud, time_sunset_str, time_sunrise_str)


def db_create(time_request_str, data_cloud, time_sunset_str, time_sunrise_str):
    """
    Create table
    """
    conn = sqlite3.connect('mydatabase.db')
    c = conn.cursor()

    # Check if table exists
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='mytable';")
    result = c.fetchone()
    if not result:
        c.execute('''CREATE TABLE mytable
                     (time_request text UNIQUE, data_cloud int, data_sunset text, data_sunrise text)''')
    
    #insert th data in table
    try:
        c.execute("INSERT INTO mytable VALUES (?, ?, ?, ?)", (time_request_str, data_cloud, time_sunset_str, time_sunrise_str))
    except sqlite3.IntegrityError:
        print("Current_hour value already exists in the table")

    conn.commit()
    conn.close()


def recive_data_api():
    conn = sqlite3.connect('mydatabase.db')
    c = conn.cursor()

    current_time = datetime.datetime.now()
    next_hour = (current_time + datetime.timedelta(hours=-1)).strftime('%Y-%m-%d %H:00:00')
    print(current_time, next_hour)
    # Check if the mytable table and the same value exists
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='mytable'")
    table_exists = c.fetchone() is not None

    # Check if the current_hour_new value is present in the current_hour column of the mytable table
    if table_exists:
        c.execute("SELECT time_request FROM mytable")
        time_request_row = [row[0] for row in c.fetchall()]
        if next_hour in time_request_row:
            print('data exist')
        else:
            data_request()
    else:
        data_request()

    # Close the cursor and the database connection
    c.close()
    conn.close()

def recive_data_from_table():
    conn = sqlite3.connect('mydatabase.db')
    c = conn.cursor()

    current_time = datetime.datetime.now()
    next_hour = (current_time + datetime.timedelta(hours=-1)).strftime('%Y-%m-%d %H:00:00')
    
    #print table
    c.execute("SELECT * FROM mytable")
    rows = c.fetchall()
    for row in rows:
         print(row)

    c.execute("SELECT * FROM mytable WHERE time_request = ?", (next_hour,))
    data = c.fetchone()
    data_cloud = data[1]
    data_sunset = data[2]
    data_sunrise = data[3]

    data_api = (data_cloud, data_sunset, data_sunrise)

    conn.close()
    return data_api
