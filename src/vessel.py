import math
import pygame

# --- Constants ---
VESSEL_COLOR = (255, 100, 100)
METERS_PER_DEGREE_LON = 111320 * math.cos(math.radians(50.88)) # Specific to Southampton

class Vessel:
    """ Represents a vessel with basic physics, operating in a lat/lon world. """
    def __init__(self, start_lat, start_lon):
        self.lat = start_lat
        self.lon = start_lon
        self.heading = math.radians(0) # Radians, North (0°)
        self.speed_mps = 0.0
        
        # Control inputs
        self.thrust = 0.0       # Range -1.0 to 1.0
        self.rudder_angle = 0.0 # Range -1.0 to 1.0

        # --- Physical Properties (Updated) ---
        self.length_meters = 1.0
        self.max_speed_mps = 5.14 # Approx. 10 knots
        self.acceleration = 0.02
        self.drag_coefficient = 0.01 # Proportional drag for coasting effect
        self.turn_rate = 0.03 # Reduced for more gradual turning

        self.METERS_PER_DEGREE_LAT = 111132.954


    def update(self):
        """ Updates the vessel's state based on physics and control inputs. """
        # --- Speed Calculation ---
        # Acceleration is proportional to the difference between target and current speed
        target_speed = self.thrust * self.max_speed_mps
        self.speed_mps += (target_speed - self.speed_mps) * self.acceleration
        
        # --- Drag Calculation (Updated for Momentum) ---
        # Apply proportional drag. The vessel now loses a small percentage of its speed each frame.
        self.speed_mps *= (1.0 - self.drag_coefficient)

        # --- Heading Calculation ---
        if abs(self.speed_mps) > 0.1:
            # Rudder is more effective at higher speeds
            turn_effectiveness = self.rudder_angle * (abs(self.speed_mps) / self.max_speed_mps)
            self.heading -= turn_effectiveness * self.turn_rate
        
        # Keep heading within 0 to 2*pi
        self.heading %= (2 * math.pi)

        # --- Position Calculation (Navigational Standard) ---
        # Convert speed to distance for this frame (assuming 60 FPS)
        distance_meters = self.speed_mps / 60.0
        
        # Calculate change in lat (North/South) and lon (East/West)
        delta_lat = (distance_meters * math.cos(self.heading)) / self.METERS_PER_DEGREE_LAT
        delta_lon = (distance_meters * math.sin(self.heading)) / METERS_PER_DEGREE_LON
        
        self.lat += delta_lat
        self.lon += delta_lon

    def draw(self, screen, camera):
        """ Draws the vessel, scaling its size based on the camera zoom. """
        screen_x, screen_y = camera.world_to_screen(self.lat, self.lon)
        
        # Calculate vessel size in pixels
        world_width_m = camera.lon_span * METERS_PER_DEGREE_LON
        pixels_per_meter = screen.get_width() / world_width_m
        size_in_pixels = self.length_meters * pixels_per_meter
        
        # Define triangle points relative to vessel position and NAVIGATIONAL heading
        p1 = (
            screen_x + size_in_pixels * math.sin(self.heading),
            screen_y - size_in_pixels * math.cos(self.heading)
        )
        p2 = (
            screen_x + size_in_pixels * 0.6 * math.sin(self.heading + math.radians(140)),
            screen_y - size_in_pixels * 0.6 * math.cos(self.heading + math.radians(140))
        )
        p3 = (
            screen_x + size_in_pixels * 0.6 * math.sin(self.heading - math.radians(140)),
            screen_y - size_in_pixels * 0.6 * math.cos(self.heading - math.radians(140))
        )
        
        # The '2' at the end tells pygame to draw an outline of thickness 2
        pygame.draw.polygon(screen, VESSEL_COLOR, [p1, p2, p3], 2)
