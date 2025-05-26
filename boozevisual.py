import pygame
import math
import time


# Your current location
your_lat = 43.643435266106145
your_lon = -79.5204522388619
heading = 90

# List of stores (lat, long)
stores = [
    (43.649226974387176, -79.50770127189931),
    (43.6532, -79.5034),
    (43.6415, -79.5153),
    (43.6387, -79.5286),
    (43.6478, -79.5192),
    (43.6352, -79.5221),
    (43.6505, -79.5308),
    (43.6423, -79.5107),
    (43.6461, -79.5259),
    (43.6398, -79.5174)
]


pygame.init()
WIDTH, HEIGHT = 400, 400
CENTER = (WIDTH // 2, HEIGHT // 2)
RADIUS = 150
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Booze Compass")
font = pygame.font.SysFont(None, 24)


store_lat, store_lon = stores[0]
# --- GPS Functions ---
def haversine(lat1, lon1, lat2, lon2):
    R = 6371000  # Earth radius in meters
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2)**2 + \
        math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2)**2

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def calculate_bearing(lat1, lon1, lat2, lon2):
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_lambda = math.radians(lon2 - lon1)

    x = math.sin(delta_lambda) * math.cos(phi2)
    y = math.cos(phi1) * math.sin(phi2) - \
        math.sin(phi1) * math.cos(phi2) * math.cos(delta_lambda)

    bearing = (math.degrees(math.atan2(x, y)) + 360) % 360
    return bearing

def find_closest_store(current_lat, current_lon, stores):
    closest_store = None
    min_distance = float('inf')
    
    for store in stores:
        distance = haversine(current_lat, current_lon, store[0], store[1])
        if distance < min_distance:
            min_distance = distance
            closest_store = store
    
    return closest_store

# --- Drawing Function ---
def draw_compass(current_heading_deg, target_bearing_deg, distance_to_store):
    screen.fill((30, 30, 30))

    pygame.draw.circle(screen, (200, 200, 200), CENTER, RADIUS, 2)

    for angle, label in zip([0, 90, 180, 270], ["N", "E", "S", "W"]):
        rad = math.radians(angle)
        x = CENTER[0] + math.sin(rad) * (RADIUS + 10)
        y = CENTER[1] - math.cos(rad) * (RADIUS + 10)
        text = font.render(label, True, (255, 255, 255))
        rect = text.get_rect(center=(x, y))
        screen.blit(text, rect)

    # Calculate the relative turn direction
    turn_angle = (target_bearing_deg - current_heading_deg) % 360
    turn_rad = math.radians(turn_angle)

    x = CENTER[0] + math.sin(turn_rad) * RADIUS
    y = CENTER[1] - math.cos(turn_rad) * RADIUS
    pygame.draw.line(screen, (0, 255, 0), CENTER, (x, y), 4)

    dist_text = font.render(f"Distance: {int(distance_to_store)} m", True, (255, 255, 255))
    screen.blit(dist_text, (10, 10))

    pygame.display.flip()

# --- Main Loop ---

def main():
    global heading, your_lat, your_lon, store_lat, store_lon
    
    # Find closest store
    closest_store = find_closest_store(your_lat, your_lon, stores)
    store_lat, store_lon = closest_store
    
    clock = pygame.time.Clock()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Calculate target data
        bearing_to_store = calculate_bearing(your_lat, your_lon, store_lat, store_lon)
        distance_to_store = haversine(your_lat, your_lon, store_lat, store_lon)

        draw_compass(heading, bearing_to_store, distance_to_store)
        clock.tick(10)

    pygame.quit()

if __name__ == "__main__":
    main()