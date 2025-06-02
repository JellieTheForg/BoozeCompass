import math
import numpy as np
import serial
import joblib
import time
import smbus2 as smbus
#^CHANGE THIS TO JUST SMBUS WHEN ON RASPBERRY PI
from PIL import Image, ImageFont, ImageDraw
from adafruit_ssd1306 import SSD1306_I2C
import pynmea2
import board

tree, store_locations_deg = joblib.load('tree.joblib')
store_locations_rad = np.radians(store_locations_deg)

#placeholder values
your_lat = 43.66739785769686
your_lon = -79.38122281349305
heading = 90

# --- Compass Functions ---

def read_word(addr):
    ADDRESS = 0x1E
    bus = smbus.SMBus(1)
    bus.write_byte_data(ADDRESS, 0x00, 0x70)  # 8 samples, 15Hz
    bus.write_byte_data(ADDRESS, 0x01, 0x20)  # Gain = 1.3 gauss 
    bus.write_byte_data(ADDRESS, 0x02, 0x00)  # Continuous mode(doesn't sleep after taking one measurement)
    high = bus.read_byte_data(ADDRESS, addr)
    low = bus.read_byte_data(ADDRESS, addr + 1)
    val = (high << 8) + low
    if val > 32767:
        val -= 65536
    return val

def get_heading():
    x = read_word(0x03)
    y = read_word(0x07)
    
    heading_rad = math.atan2(y, x)
    heading_rad += get_local_declination(your_lat, your_lon)

    if heading_rad < 0:
        heading_rad += 2 * math.pi
    if heading_rad > 2 * math.pi:
        heading_rad -= 2 * math.pi

    return heading_rad * 180 / math.pi

def get_local_declination(lat, lon):
    toronto = (43.7, -79.4)
    kingston = (44.2, -76.5)
    dist_to_toronto = haversine(lat, lon, *toronto)
    dist_to_kingston = haversine(lat, lon, *kingston)

    declination_toronto = 0.1972222
    declination_kingston = 0.244346

    return declination_toronto if dist_to_toronto <= dist_to_kingston else declination_kingston

# --- GPS Functions ---
def haversine(lat1, lon1, lat2, lon2):
    R = 6371000  # earth radius in meters
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def calculate_bearing(lat1, lon1, lat2, lon2):
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_lambda = math.radians(lon2 - lon1)

    x = math.sin(delta_lambda) * math.cos(phi2)
    y = math.cos(phi1) * math.sin(phi2) - math.sin(phi1) * math.cos(phi2) * math.cos(delta_lambda)

    bearing = (math.degrees(math.atan2(x, y)) + 360) % 360
    return bearing

def find_closest_store(lat_deg, lon_deg):
    point_rad = np.radians([[lat_deg, lon_deg]])
    dist, ind = tree.query(point_rad, k=1)
    closest_index = ind[0][0]
    distance_m = dist[0][0] * 6371000
    return store_locations_deg[closest_index], distance_m

def get_gps_coords():
    """Fetches GPS coordinates once from the serial port"""
    port = "/dev/ttyAMA0"
    try:
        with serial.Serial(port, baudrate=9600, timeout=0.5) as ser:
            data = ser.readline()
            if data.startswith(b'$GPRMC'):
                msg = pynmea2.parse(data.decode('ascii'))
                if hasattr(msg, 'latitude') and hasattr(msg, 'longitude'):
                    return msg.latitude, msg.longitude
            return None  # No valid GPS data found
    
    except (serial.SerialException, pynmea2.ParseError, UnicodeDecodeError) as e:
        print(f"GPS error: {e}")
        return None
#^UNCOMMENT WHEN USING MODULES ON RASPI

# --- Display Functions ---
def init_display():
    i2c=board.I2C()
    disp = SSD1306_I2C(128, 64, i2c, addr=0x3C)
    disp.begin()
    disp.clear()
    disp.display()
    return disp

def draw_compass(disp, current_heading_deg, target_bearing_deg, distance_to_store):
    image = Image.new("1", (128, 64))
    draw = ImageDraw.Draw(image)
    
    #draw compass circle
    draw.ellipse((96-25, 32-25, 96+25, 32+25), outline=1, width=1)
    
    #draw arrow
    turn_angle = (target_bearing_deg - current_heading_deg) % 360
    turn_rad = math.radians(turn_angle)
    arrow_x = 96 + math.sin(turn_rad) * 25
    arrow_y = 32 - math.cos(turn_rad) * 25
    draw.line((96, 32, arrow_x, arrow_y), fill=1, width=2)
    
    #distance in meters
    font = ImageFont.load_default()
    draw.text((5, 24), f"{int(distance_to_store)}m", font=font, fill=1)
    disp.image(image)
    disp.display()

# --- Main Loop ---
def main():
    global heading, your_lat, your_lon
    #initialize screen
    disp = init_display()
    try:
        while True:
            #sensor data
            # heading = get_heading()  # Uncomment for real compass
            # your_lat, your_lon = get_gps_coords()  # Uncomment for real GPS
            
            (store_lat, store_lon), distance = find_closest_store(your_lat, your_lon)
            bearing = calculate_bearing(your_lat, your_lon, store_lat, store_lon)
            
            draw_compass(disp, heading, bearing, distance)
            time.sleep(0.1) 
            
    except KeyboardInterrupt:
        disp.clear()
        disp.display()
        print("\nExiting cleanly")

if __name__ == "__main__":
    main()