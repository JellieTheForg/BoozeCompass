import json
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Load zone bounding boxes
with open("zone_bounds.json") as f:
    zone_bounds = json.load(f)

# Load store coordinates for each zone
with open("zones.json") as f:
    zone_stores = json.load(f)

fig, ax = plt.subplots(figsize=(12, 10))

# Draw each zone as a rectangle and its store points
for zone, bounds in zone_bounds.items():
    lat_min = bounds["lat_min"]
    lat_max = bounds["lat_max"]
    lon_min = bounds["lon_min"]
    lon_max = bounds["lon_max"]

    # Draw the zone rectangle
    rect = patches.Rectangle(
        (lon_min, lat_min),
        lon_max - lon_min,
        lat_max - lat_min,
        linewidth=0.5,
        edgecolor='gray',
        facecolor='none'
    )
    ax.add_patch(rect)

    # Draw store points in that zone
    points = zone_stores.get(zone, [])
    for lat, lon in points:
        ax.plot(lon, lat, 'ro', markersize=2)

# Labeling and axis config
ax.set_title("Zone Grid with Store Points")
ax.set_xlabel("Longitude")
ax.set_ylabel("Latitude")
ax.set_aspect('equal', adjustable='box')

plt.tight_layout()
plt.show()
