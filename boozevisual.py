import pygame
import math
import numpy as np
import sys
import joblib

# placeholder, to be replaced by raspberry pi inputs
your_lat = 43.66739785769686
your_lon = -79.38122281349305
heading = 90

tree, store_locations_deg = joblib.load('tree.joblib')
store_locations_rad = np.radians(store_locations_deg)

pygame.init()
WIDTH, HEIGHT = 128, 64
pygame.display.set_caption("Booze Compass")
font = pygame.font.SysFont(None, 24)
pygame.mouse.set_visible(False)
pygame.mixer.quit()
info = pygame.display.Info()
screen = pygame.display.set_mode((info.current_w, info.current_h), pygame.FULLSCREEN)
pygame.event.set_grab(True)

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

# --- Drawing Function ---
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
    global heading, your_lat, your_lon, store_lat, store_lon

    clock = pygame.time.Clock()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

        (store_lat, store_lon), distance_to_store = find_closest_store(your_lat, your_lon)
        bearing_to_store = calculate_bearing(your_lat, your_lon, store_lat, store_lon)

        draw_compass(heading, bearing_to_store, distance_to_store)
        clock.tick(10)

    pygame.quit()

if __name__ == "__main__":
    main()