import arrow
import requests
import json
import sqlite3
import pandas as pd

import secrets
import CONSTANTS


def data_request():
    # current_time = arrow.now().floor('hour')
    # response_cloud = requests.get(
    #     'https://api.stormglass.io/v2/weather/point',
    # params={
    #     'lat': CONSTANTS.OSLO_LAT,
    #     'lng': CONSTANTS.OSLO_LON,
    #     'start': current_time.to('UTC').timestamp(),  # Convert to UTC timestamp
    #     'end': current_time.to('UTC').timestamp(),  # Convert to UTC timestamp
    #     'params': ','.join(['cloudCover']),
    # },
    # headers={
    #     'Authorization': secrets.API_KEY
    # }
    # )

    # start = arrow.now().floor('day')
    # end = arrow.now().shift(days=1).floor('day')
    # response_astronomy = requests.get(
    #     'https://api.stormglass.io/v2/astronomy/point',
    # params={
    #     'lat': CONSTANTS.OSLO_LAT,
    #     'lng': CONSTANTS.OSLO_LON,
    #     'start': start.to('UTC').timestamp(),  # Convert to UTC timestamp
    #     'end': end.to('UTC').timestamp(),  # Convert to UTC timestamp
    # },
    # headers={
    #     'Authorization': secrets.API_KEY
    # }
    # )
    
    # json_data_cloud = response_cloud.json()
    current_time = arrow.now().floor('hour')
    json_data_cloud = {
    "hours": [
        {
            "cloudCover": {
                "dwd": 63.75,
                "noaa": 17.83,
                "sg": 14.3,
                "smhi": 12.5,
                "yr": 14.3
            },
            "time": "2023-02-17T23:00:00+00:00"
        }
    ],
    "meta": {
        "cost": 1,
        "dailyQuota": 10,
        "end": "2023-02-17 23:00",
        "lat": 59.9139,
        "lng": 10.7522,
        "params": [
            "cloudCover"
        ],
        "requestCount": 9,
        "start": "2023-02-17 23:00"
    }
}
    #print(json.dumps(json_data_cloud, indent=4))
    data_cloud = json_data_cloud['hours'][0]['cloudCover']['dwd'] # 95.01

    #json_data_astronomy = response_astronomy.json()
    json_data_astronomy = {
    "data": [
        {
            "astronomicalDawn": "2023-02-18T04:29:46+00:00",
            "astronomicalDusk": "2023-02-18T18:35:04+00:00",
            "civilDawn": "2023-02-18T06:06:09+00:00",
            "civilDusk": "2023-02-18T16:58:40+00:00",
            "moonFraction": 0.0722327901155913,
            "moonPhase": {
                "closest": {
                    "text": "New moon",
                    "time": "2023-02-20T12:23:00+00:00",
                    "value": 1
                },
                "current": {
                    "text": "Waning crescent",
                    "time": "2023-02-17T23:00:00+00:00",
                    "value": 0.9133856261502009
                }
            },
            "moonrise": "2023-02-17T06:51:49+00:00",
            "moonset": "2023-02-17T10:42:49+00:00",
            "nauticalDawn": "2023-02-18T05:17:45+00:00",
            "nauticalDusk": "2023-02-18T17:47:05+00:00",
            "sunrise": "2023-02-18T06:49:30+00:00",
            "sunset": "2023-02-18T16:15:19+00:00",
            "time": "2023-02-17T23:00:00+00:00"
        },
        {
            "astronomicalDawn": "2023-02-19T04:27:13+00:00",
            "astronomicalDusk": "2023-02-19T18:37:26+00:00",
            "civilDawn": "2023-02-19T06:03:34+00:00",
            "civilDusk": "2023-02-19T17:01:06+00:00",
            "moonFraction": 0.024215138597253327,
            "moonPhase": {
                "closest": {
                    "text": "New moon",
                    "time": "2023-02-20T10:14:00+00:00",
                    "value": 1
                },
                "current": {
                    "text": "Waning crescent",
                    "time": "2023-02-18T23:00:00+00:00",
                    "value": 0.9502649990493587
                }
            },
            "moonrise": "2023-02-18T07:16:21+00:00",
            "moonset": "2023-02-18T12:33:18+00:00",
            "nauticalDawn": "2023-02-19T05:15:14+00:00",
            "nauticalDusk": "2023-02-19T17:49:25+00:00",
            "sunrise": "2023-02-19T06:46:45+00:00",
            "sunset": "2023-02-19T16:17:55+00:00",
            "time": "2023-02-18T23:00:00+00:00"
        }
    ],
    "meta": {
        "cost": 1,
        "dailyQuota": 10,
        "lat": 59.9139,
        "lng": 10.7522,
        "requestCount": 10,
        "start": "2023-02-17 23:00"
    }
}
    
    data_sunset = json_data_astronomy['data'][0]['sunset'] # Output: "2023-02-18T16:15:19+00:00"
    data_sunrise = json_data_astronomy['data'][0]['sunrise'] # Output: "2023-02-18T06:49:30+00:00"

    db_create(current_time, data_cloud, data_sunset, data_sunrise)


def db_create(current_time, data_cloud, data_sunset, data_sunrise):
    current_time_str = current_time.format('YYYY-MM-DD HH:mm:ss')

    # Create table
    print('create table')
    conn = sqlite3.connect('mydatabase.db')
    c = conn.cursor()
    # Check if table exists
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='mytable';")
    result = c.fetchone()
    if result:
        # Table exists, do not create it again
        print('Table already exists')
    else:
        # Table does not exist, create it
        c.execute('''CREATE TABLE mytable
                     (current_hour text UNIQUE, data_cloud int, data_sunset text, data_sunrise text)''')
        #print('Table created')
    try:
        c.execute("INSERT INTO mytable VALUES (?, ?, ?, ?)", (current_time_str, data_cloud, data_sunset, data_sunrise))
    except sqlite3.IntegrityError:
        print("current_hour value already exists in the table")
    conn.commit()
    conn.close()


def recive_data_api():
    conn = sqlite3.connect('mydatabase.db')
    c = conn.cursor()
    #c.execute('''DROP TABLE mytable''')
    current_hour_new = arrow.now().floor('hour')

    # Check if the mytable table and the same value exists
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='mytable'")
    table_exists = c.fetchone() is not None
    # Check if the current_hour_new value is present in the current_hour column of the mytable table
    if table_exists:
        c.execute("SELECT current_hour FROM mytable")
        current_hours = [row[0] for row in c.fetchall()]
        if current_hour_new in current_hours:
            print('data exist')
        else:
            data_request()
            print('done')
    else:
        data_request()

    # Close the cursor and the database connection
    c.close()
    conn.close()

def recive_data_from_table():
    conn = sqlite3.connect('mydatabase.db')
    c = conn.cursor()
    #current_time = arrow.now().floor('hour')
    #current_time_str = current_time.format('YYYY-MM-DD HH:mm:ss')
    current_time_str = '2023-02-18 00:13:00' #'2023-02-18 00:00:00'
    c.execute("SELECT * FROM mytable")

    # fetch all the results and print each row
    rows = c.fetchall()
    for data in rows:
    #     print(row)
    # c.execute("SELECT * FROM mytable WHERE current_hour = ?", (current_time_str,))
    # data = c.fetchone()
    # print(data)
        data_cloud = data[1]
        data_sunset = data[2]
        data_sunrise = data[3]

    conn.close()
    
    data_api = (data_cloud, data_sunset, data_sunrise)
    return data_api
