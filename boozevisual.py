import pygame
import math
import numpy as np
import joblib
import serial
import smbus2 as smbus
import pynmea2

tree, store_locations_deg = joblib.load('treeall.joblib')
store_locations_rad = np.radians(store_locations_deg)

# placeholder, to be replaced by raspberry pi inputs(functions are already in this file, just not used)
your_lat = 43.66739785769686
your_lon = -79.38122281349305
heading = 90

# --- Compass ---

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
    heading_rad += get_local_declination(your_lat,your_lon) # local magnetic declination in radians

    if heading_rad < 0:
        heading_rad += 2 * math.pi
    if heading_rad > 2 * math.pi:
        heading_rad -= 2 * math.pi

    return heading_rad * 180 / math.pi

#Some bullshit called true and magnetic north forced me to make this function, it just gives an output for adjusted heading
def get_local_declination(lat, lon):
    toronto = (43.7, -79.4) #I'm only really going to use this in toronto or kingston, but I can add more cities later(maybe even something that connects to the internet???!!!)
    kingston = (44.2, -76.5)
    dist_to_toronto = haversine(lat, lon, *toronto)
    dist_to_kingston = haversine(lat, lon, *kingston)

    # saved declinations
    declination_toronto = 0.1972222
    declination_kingston = 0.244346

    if dist_to_toronto <= dist_to_kingston:
        return declination_toronto
    else:
        return declination_kingston

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

"""
def get_gps_coords()
	port="/dev/ttyAMA0"
	ser=serial.Serial(port, baudrate=9600, timeout=0.5)
	dataout = pynmea2.NMEAStreamReader()
	newdata=ser.readline()

	if newdata[0:6] == "$GPRMC":
		newmsg=pynmea2.parse(newdata)
		your_lat=newmsg.latitude
		your_lon=newmsg.longitude
    return your_lat, your_lon
"""
#^UNCOMMENT WHEN USING MODULES ON RASPI

# --- Drawing Function ---
pygame.init()
WIDTH, HEIGHT = 128, 64
pygame.display.set_caption("Booze Compass")
font = pygame.font.SysFont(None, 24)
pygame.mouse.set_visible(False)
pygame.mixer.quit()
info = pygame.display.Info()
screen = pygame.display.set_mode((info.current_w, info.current_h), pygame.FULLSCREEN)
pygame.event.set_grab(True)

def draw_compass(current_heading_deg, target_bearing_deg, distance_to_store):
    screen.fill((0, 0, 0))

    COMPASS_RADIUS = 25
    COMPASS_CENTER = (96, 32)

    pygame.draw.circle(screen, (255, 255, 255), COMPASS_CENTER, COMPASS_RADIUS, 1)

    turn_angle = (target_bearing_deg - current_heading_deg) % 360
    turn_rad = math.radians(turn_angle)
    arrow_x = COMPASS_CENTER[0] + math.sin(turn_rad) * COMPASS_RADIUS
    arrow_y = COMPASS_CENTER[1] - math.cos(turn_rad) * COMPASS_RADIUS
    pygame.draw.line(screen, (255, 255, 255), COMPASS_CENTER, (arrow_x, arrow_y), 2)

    distance_str = f"{int(distance_to_store)}m"
    value_text = font.render(distance_str, True, (255, 255, 255))
    screen.blit(value_text, (5, 24))

    pygame.display.flip()

# --- Main Loop ---
def main():
    global heading, your_lat, your_lon
    
    try:
        clock = pygame.time.Clock()
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    running = False
            
            #sensor data 
            # heading = get_heading()  # Uncomment for real compass
            # your_lat, your_lon = get_gps_coords()  # Uncomment for real GPS
            
            (store_lat, store_lon), distance_to_store = find_closest_store(your_lat, your_lon)
            bearing_to_store = calculate_bearing(your_lat, your_lon, store_lat, store_lon)
            draw_compass(heading, bearing_to_store, distance_to_store)
            clock.tick(10)
            
    finally:
        pygame.quit()

if __name__ == "__main__":
    main()