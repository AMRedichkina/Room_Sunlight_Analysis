import arrow
import datetime
import requests
import sqlite3

from secret import API_KEY
import constants


def db_create(time_request_str, data_cloud, time_sunset_str, time_sunrise_str):
    """
    Create a new table if it doesn't exist and insert data into it.
    """
    conn = sqlite3.connect('mydatabase.db')
    c = conn.cursor()

    # Check if table exists
    try:
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='mytable';")
        result = c.fetchone()
        if not result:
            c.execute('''CREATE TABLE mytable
                     (time_request text UNIQUE, data_cloud int, data_sunset text, data_sunrise text)''')
    except Exception as e:
        raise ValueError("Error while creating table: {}".format(str(e)))

    # Insert the data into the table
    c.execute("INSERT INTO mytable VALUES (?, ?, ?, ?)", (time_request_str, data_cloud, time_sunset_str, time_sunrise_str))

    conn.commit()
    conn.close()


def data_request():
    """
    Requests cloud cover, sunrise and sunset data from Stormglass API for Oslo
    and call function 'db_create' to save it to a database.
    """
    # Check for API key
    if not API_KEY:
        raise ValueError('No API key found')

    # Cloud data request
    current_time = arrow.now().floor('hour')
    response_cloud = requests.get(
        'https://api.stormglass.io/v2/weather/point',
    params={
        'lat': constants.OSLO_LAT,
        'lng': constants.OSLO_LON,
        'start': current_time.to('UTC').timestamp(),  # Convert to UTC timestamp
        'end': current_time.to('UTC').timestamp(),  # Convert to UTC timestamp
        'params': ','.join(['cloudCover']),
    },
    headers={
        'Authorization': API_KEY
    }
    )

    json_data_cloud = response_cloud.json()

    # Sunrise and sunset data request
    start = arrow.now().floor('day')
    end = arrow.now().shift(days=1).floor('day')
    response_astronomy = requests.get(
        'https://api.stormglass.io/v2/astronomy/point',
    params={
        'lat': constants.OSLO_LAT,
        'lng': constants.OSLO_LON,
        'start': start.to('UTC').timestamp(),
        'end': end.to('UTC').timestamp(),
    },
    headers={
        'Authorization': API_KEY
    }
    )
    
    json_data_astronomy = response_astronomy.json()

    # Extract data
    try:
        data_cloud = json_data_cloud['hours'][0]['cloudCover']['dwd']  # Output: 95.01
        
        time_request = json_data_cloud['hours'][0]['time']  # Output: "2023-02-17T23:00:00+00:00"
        datetime_request = datetime.datetime.strptime(time_request, '%Y-%m-%dT%H:%M:%S%z')
        time_request_str = datetime_request.strftime('%Y-%m-%d %H:%M:%S')

        data_sunset = json_data_astronomy['data'][0]['sunset']  # Output: "2023-02-18T16:15:19+00:00"
        datetime_sunset = datetime.datetime.strptime(data_sunset, '%Y-%m-%dT%H:%M:%S%z')
        time_sunset_str = datetime_sunset.strftime('%Y-%m-%d %H:%M:%S')

        data_sunrise = json_data_astronomy['data'][0]['sunrise']  # Output: "2023-02-18T06:49:30+00:00"
        datetime_sunrise = datetime.datetime.strptime(data_sunrise, '%Y-%m-%dT%H:%M:%S%z')
        time_sunrise_str = datetime_sunrise.strftime('%Y-%m-%d %H:%M:%S')
    except (KeyError, IndexError) as err:
        raise ValueError(f'Error in extracting data from response: {err}')

    db_create(time_request_str, data_cloud, time_sunset_str, time_sunrise_str)


def recive_data_api():
    """
    Check if there is data in the database and if not,
    call the function 'data_request'
    """
    conn = sqlite3.connect('mydatabase.db')
    c = conn.cursor()

    # An correction is needed because the answer comes in the previous hour
    current_time = datetime.datetime.now()
    correct_hour = (current_time + datetime.timedelta(hours=-1)).strftime('%Y-%m-%d %H:00:00')

    # Check if table exists
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='mytable'")
    table_exists = c.fetchone() is not None

    # Check if the data has already been requested at this hour
    # and if not, then request
    if table_exists:
        c.execute("SELECT time_request FROM mytable")
        time_request_row = [row[0] for row in c.fetchall()]
        if correct_hour not in time_request_row:
            data_request()
    else:
        data_request()

    c.close()
    conn.close()


def retrieve_data_from_table():
    """
    Retrieves the data from the mytable table
    """
    conn = sqlite3.connect('mydatabase.db')
    c = conn.cursor()

    # An correction is needed because the answer comes in the previous hour
    current_time = datetime.datetime.now()
    correct_hour = (current_time + datetime.timedelta(hours=-1)).strftime('%Y-%m-%d %H:00:00')

    c.execute("SELECT * FROM mytable WHERE time_request = ?", (correct_hour,))
    data = c.fetchone()
    data_cloud = data[1]
    data_sunset = data[2]
    data_sunrise = data[3]

    if data_cloud is None:
        raise ValueError('Most likely, the number of requests has ended. Please check it out.')

    data_api = (data_cloud, data_sunset, data_sunrise)

    conn.close()
    return data_api
