from decimal import Decimal
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

# In order to simplify calculations,
# the dimensions of the window and
# its height above the ground are preset.


EARTH_RADIUS = Decimal('6.371e6')  # in meters
WINDOW_HEIGHT = Decimal('1.5')  # in meters
WINDOW_WIDTH = Decimal('1')  # in meters
WINDOW_AREA = WINDOW_HEIGHT * WINDOW_WIDTH  # in square meters
I0 = Decimal('1361')  # Solar constant in W/m^2
K = Decimal('0.15')  # Attenuation coefficient of the atmosphere
