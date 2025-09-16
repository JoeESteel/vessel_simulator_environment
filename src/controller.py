import math
import pygame

# --- World Constants ---
METERS_PER_DEGREE_LAT = 111132.954
METERS_PER_DEGREE_LON = 111320 * math.cos(math.radians(50.88))

# --- Helper Functions ---
def calculate_distance(lat1, lon1, lat2, lon2):
    """ Calculate distance between two lat/lon points in meters. """
    delta_lat_m = (lat2 - lat1) * METERS_PER_DEGREE_LAT
    delta_lon_m = (lon2 - lon1) * METERS_PER_DEGREE_LON
    return math.sqrt(delta_lat_m**2 + delta_lon_m**2)

def calculate_bearing(lat1, lon1, lat2, lon2):
    """ Calculate bearing from point 1 to point 2 in radians. """
    delta_lon = math.radians(lon2 - lon1)
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    y = math.sin(delta_lon) * math.cos(lat2_rad)
    x = math.cos(lat1_rad) * math.sin(lat2_rad) - math.sin(lat1_rad) * math.cos(lat2_rad) * math.cos(delta_lon)
    # Bearing needs to be returned for standard navigational calculations (North=0, East=90)
    # The result of atan2 is from -pi to pi, with 0 pointing East. We need to adjust.
    initial_bearing = math.atan2(y, x)
    return (initial_bearing + (2 * math.pi)) % (2 * math.pi)


class VesselController:
    """ The 'Brain' of the vessel. Contains all autonomous logic. """
    def __init__(self):
        self.mode = "MANUAL"
        
        self.target_heading_deg = 90
        self.target_speed_kts = 0
        
        self.waypoints = []
        self.current_waypoint_index = 0
        self.arrival_radius_m = 5

        self.heading_kP = 1.5
        self.speed_kP = 0.8

    def set_mode(self, mode):
        if mode in ["MANUAL", "AUTOHELM", "WAYPOINT"]:
            self.mode = mode
            print(f"Controller mode set to: {self.mode}")
            if mode == "WAYPOINT":
                self.current_waypoint_index = 0

    def add_waypoint(self, lat, lon):
        self.waypoints.append((lat, lon))
        
    def get_manual_commands(self, keys):
        """ Processes keyboard input for manual control. """
        thrust = 0.0
        if keys[pygame.K_UP]: thrust = 1.0
        elif keys[pygame.K_DOWN]: thrust = -0.5
        
        rudder = 0.0
        if keys[pygame.K_LEFT]: rudder = 1.0
        elif keys[pygame.K_RIGHT]: rudder = -1.0
        
        return thrust, rudder

    def update(self, current_lat, current_lon, current_heading_rad, current_speed_mps):
        """ Main logic loop for the controller. Returns thrust and rudder commands. """
        if self.mode == "MANUAL":
            return 0, 0 

        elif self.mode == "AUTOHELM":
            return self._run_autohelm(current_heading_rad, current_speed_mps, math.radians(self.target_heading_deg))

        elif self.mode == "WAYPOINT":
            if not self.waypoints or self.current_waypoint_index >= len(self.waypoints):
                self.target_speed_kts = 0
                return self._run_autohelm(current_heading_rad, current_speed_mps, current_heading_rad)

            target_lat, target_lon = self.waypoints[self.current_waypoint_index]
            distance_to_wp = calculate_distance(current_lat, current_lon, target_lat, target_lon)
            
            if distance_to_wp < self.arrival_radius_m:
                print(f"Arrived at waypoint {self.current_waypoint_index}")
                self.current_waypoint_index += 1
                if self.current_waypoint_index >= len(self.waypoints):
                    self.target_speed_kts = 0
                    return 0, 0
            
            target_bearing_rad = calculate_bearing(current_lat, current_lon, target_lat, target_lon)
            return self._run_autohelm(current_heading_rad, current_speed_mps, target_bearing_rad)
        
        return 0, 0

    def _run_autohelm(self, current_heading_rad, current_speed_mps, target_heading_rad):
        # Note: Vessel heading is 0=East, Nav bearing is 0=North. We must convert.
        nav_current_heading_rad = (math.pi/2 - current_heading_rad + 2*math.pi) % (2*math.pi)
        nav_target_heading_rad = (math.pi/2 - target_heading_rad + 2*math.pi) % (2*math.pi)

        heading_error = nav_target_heading_rad - nav_current_heading_rad
        if heading_error > math.pi: heading_error -= 2 * math.pi
        if heading_error < -math.pi: heading_error += 2 * math.pi
        
        rudder_cmd = self.heading_kP * heading_error
        
        target_speed_mps = self.target_speed_kts * 0.514444
        speed_error = target_speed_mps - current_speed_mps
        thrust_cmd = self.speed_kP * speed_error

        rudder_cmd = max(-1.0, min(1.0, rudder_cmd))
        thrust_cmd = max(-0.5, min(1.0, thrust_cmd))

        return thrust_cmd, rudder_cmd
