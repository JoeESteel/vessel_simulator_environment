import pygame
import math
import sys

# --- Constants ---
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 800
BACKGROUND_COLOR = (20, 40, 60) # Deep blue
VESSEL_COLOR = (255, 100, 100) # Red
TEXT_COLOR = (230, 230, 230)
GRID_COLOR = (50, 80, 110) # Faded blue for the grid

# --- World Constants ---
# These are calculated once at a representative latitude for the area (Southampton)
# and treated as constant for our small simulation area.
METERS_PER_DEGREE_LAT = 111132.954
METERS_PER_DEGREE_LON = 111320 * math.cos(math.radians(50.88))


class Camera:
    """ Manages the view (pan and zoom). All coordinate conversions happen here. """
    def __init__(self, lat, lon):
        self.lat = lat
        self.lon = lon
        # lon_span is the width of the screen in degrees of longitude. A smaller number is more zoomed in.
        self.lon_span = 0.04 # Start more zoomed in
        self.min_lon_span = 0.001 # Max zoom in
        self.max_lon_span = 0.2   # Max zoom out

    def update(self, target_lat, target_lon):
        """ Smoothly follows a target's position. """
        # Lerp (linear interpolation) for smooth camera movement
        self.lat += (target_lat - self.lat) * 0.1
        self.lon += (target_lon - self.lon) * 0.1

    def zoom(self, amount):
        """ Zooms the view in or out. """
        self.lon_span *= amount
        # Clamp the zoom level
        if self.lon_span < self.min_lon_span: self.lon_span = self.min_lon_span
        if self.lon_span > self.max_lon_span: self.lon_span = self.max_lon_span

    def world_to_screen(self, lat, lon):
        """ Converts a latitude/longitude pair to an (x, y) screen coordinate based on camera view. """
        # Calculate scale based on current zoom
        pixels_per_degree_lon = SCREEN_WIDTH / self.lon_span
        pixels_per_degree_lat = pixels_per_degree_lon * (METERS_PER_DEGREE_LAT / METERS_PER_DEGREE_LON)
        
        x = SCREEN_WIDTH / 2 + (lon - self.lon) * pixels_per_degree_lon
        y = SCREEN_HEIGHT / 2 - (lat - self.lat) * pixels_per_degree_lat
        return int(x), int(y)

    def screen_to_world(self, x, y):
        """ Converts an (x, y) screen coordinate to a latitude/longitude pair. """
        pixels_per_degree_lon = SCREEN_WIDTH / self.lon_span
        pixels_per_degree_lat = pixels_per_degree_lon * (METERS_PER_DEGREE_LAT / METERS_PER_DEGREE_LON)
        
        lon = self.lon + (x - SCREEN_WIDTH / 2) / pixels_per_degree_lon
        lat = self.lat - (y - SCREEN_HEIGHT / 2) / pixels_per_degree_lat
        return lat, lon
        
class Vessel:
    """ Represents a vessel with basic physics, operating in a lat/lon world. """
    def __init__(self, lat, lon):
        self.lat = lat
        self.lon = lon
        self.heading = math.radians(90)
        self.speed_mps = 0.0
        
        self.thrust = 0.0
        self.rudder_angle = 0.0
        
        self.length_meters = 1.0 # The vessel is 1m long in the real world
        self.max_speed_mps = 2.5
        self.acceleration = 0.02
        self.drag = 0.01
        self.turn_rate = 0.05

    def update(self):
        """ Updates the vessel's state based on physics and control inputs. """
        target_speed = self.thrust * self.max_speed_mps
        self.speed_mps += (target_speed - self.speed_mps) * self.acceleration
        
        if self.speed_mps > 0:
            self.speed_mps -= self.drag
            if self.speed_mps < 0: self.speed_mps = 0
        elif self.speed_mps < 0:
             self.speed_mps += self.drag
             if self.speed_mps > 0: self.speed_mps = 0

        if abs(self.speed_mps) > 0.1:
            turn_effectiveness = self.rudder_angle * (abs(self.speed_mps) / self.max_speed_mps)
            self.heading -= turn_effectiveness * self.turn_rate
        
        distance_meters = self.speed_mps / 60.0
        delta_lat = (distance_meters * math.sin(self.heading)) / METERS_PER_DEGREE_LAT
        delta_lon = (distance_meters * math.cos(self.heading)) / METERS_PER_DEGREE_LON
        self.lat += delta_lat
        self.lon += delta_lon

    def draw(self, screen, camera):
        """ Draws the vessel, scaling its size based on the camera zoom. """
        screen_x, screen_y = camera.world_to_screen(self.lat, self.lon)
        
        # Calculate the vessel's size in pixels based on its real-world length and current zoom
        meters_per_pixel = camera.lon_span * METERS_PER_DEGREE_LON / SCREEN_WIDTH
        size_in_pixels = self.length_meters / meters_per_pixel
        
        p1 = (
            screen_x + size_in_pixels * math.cos(self.heading),
            screen_y - size_in_pixels * math.sin(self.heading)
        )
        p2 = (
            screen_x + size_in_pixels * math.cos(self.heading + math.radians(140)),
            screen_y - size_in_pixels * math.sin(self.heading + math.radians(140))
        )
        p3 = (
            screen_x + size_in_pixels * math.cos(self.heading - math.radians(140)),
            screen_y - size_in_pixels * math.sin(self.heading - math.radians(140))
        )
        pygame.draw.polygon(screen, VESSEL_COLOR, [p1, p2, p3])

def draw_grid(screen, font, camera):
    """ Draws the lat/lon grid and labels relative to the camera view. """
    top_left_lat, top_left_lon = camera.screen_to_world(0, 0)
    bottom_right_lat, bottom_right_lon = camera.screen_to_world(SCREEN_WIDTH, SCREEN_HEIGHT)

    # Determine grid spacing based on zoom level to avoid clutter
    lon_span = bottom_right_lon - top_left_lon
    grid_interval = 0.001
    if lon_span > 0.02: grid_interval = 0.01
    if lon_span > 0.2: grid_interval = 0.1

    # Draw longitude lines (vertical)
    lon_start = math.floor(top_left_lon / grid_interval) * grid_interval
    for i in range(int(lon_span / grid_interval) + 2):
        lon = lon_start + i * grid_interval
        start_pos = camera.world_to_screen(top_left_lat, lon)
        end_pos = camera.world_to_screen(bottom_right_lat, lon)
        pygame.draw.line(screen, GRID_COLOR, start_pos, end_pos)
        label = f"{-lon:.3f}°W" if lon < 0 else f"{lon:.3f}°E"
        text_surface = font.render(label, True, GRID_COLOR)
        screen.blit(text_surface, (start_pos[0] + 5, 10))

    # Draw latitude lines (horizontal)
    lat_span = top_left_lat - bottom_right_lat
    lat_start = math.floor(bottom_right_lat / grid_interval) * grid_interval
    for i in range(int(lat_span / grid_interval) + 2):
        lat = lat_start + i * grid_interval
        start_pos = camera.world_to_screen(lat, top_left_lon)
        end_pos = camera.world_to_screen(lat, bottom_right_lon)
        pygame.draw.line(screen, GRID_COLOR, start_pos, end_pos)
        label = f"{lat:.3f}°N"
        text_surface = font.render(label, True, GRID_COLOR)
        screen.blit(text_surface, (10, start_pos[1] - 20))

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Vessel Simulator | Use Mouse Wheel to Zoom")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 24)
    info_font = pygame.font.Font(None, 30)

    # Start vessel at a specific point in Southampton Water
    start_lat, start_lon = 50.88, -1.38
    vessel = Vessel(start_lat, start_lon)
    camera = Camera(start_lat, start_lon)

    running = True
    while running:
        # --- Event Handling ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            # --- MOUSEWHEEL for ZOOM ---
            if event.type == pygame.MOUSEWHEEL:
                if event.y > 0: # Scroll up to zoom in
                    camera.zoom(0.8)
                elif event.y < 0: # Scroll down to zoom out
                    camera.zoom(1.2)
        
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]: vessel.thrust = 1.0
        elif keys[pygame.K_DOWN]: vessel.thrust = -0.5
        else: vessel.thrust = 0.0
        if keys[pygame.K_LEFT]: vessel.rudder_angle = 1.0
        elif keys[pygame.K_RIGHT]: vessel.rudder_angle = -1.0
        else: vessel.rudder_angle = 0.0

        # --- Update ---
        vessel.update()
        camera.update(vessel.lat, vessel.lon)

        # --- Drawing ---
        screen.fill(BACKGROUND_COLOR)
        draw_grid(screen, font, camera)
        vessel.draw(screen, camera)

        knots = vessel.speed_mps * 1.94384
        info_text = (
            f"Lat: {vessel.lat:.5f} | Lon: {vessel.lon:.5f} | "
            f"Speed: {knots:.1f} kts | "
            f"Heading: {math.degrees(vessel.heading) % 360:.0f}°"
        )
        text_surface = info_font.render(info_text, True, TEXT_COLOR)
        screen.blit(text_surface, (10, SCREEN_HEIGHT - 35))
        
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()


