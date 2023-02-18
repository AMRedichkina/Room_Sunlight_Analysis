#
OSLO_LAT = 59.9139
OSLO_LON = 10.7522

# Meters above sea level (Oslo)
ELEVATION = 23 



# Direction of each window (in degrees)
NORTH_DIR = 0
SOUTH_DIR = 180
WEST_DIR = 270
EAST_DIR = 90

# Solar constant (W/m^2)
I0 = 1367

# Extinction coefficient for cloud cover
K = 0.15

#In order to simplify calculations,
# the dimensions of the window and
# its height above the ground are preset.

# The height of the room above ground level and floor
ROOM_HEIGHT = 3 # meters (distance from the ground)
WINDOW_WIDTH = 1.5  # meters
WINDOW_HEIGHT = 1.0  # meters
WINDOW_AREA = WINDOW_WIDTH * WINDOW_HEIGHT
WINDOW_DISTANCE = 1.5  # meters (distance from the floor)
WINDOW_TRANSMITTANCE = 0.5 # the total transmittance of the window
WINDOW_CENTER = WINDOW_DISTANCE + WINDOW_HEIGHT / 2