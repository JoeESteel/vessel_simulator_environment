import math
import pygame

# A simple PID controller class
class PID:
    def __init__(self, Kp, Ki, Kd, setpoint=0):
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd
        self.setpoint = setpoint
        self._integral = 0
        self._previous_error = 0

    def update(self, measured_value):
        error = self.setpoint - measured_value
        self._integral += error
        derivative = error - self._previous_error
        self._previous_error = error
        return self.Kp * error + self.Ki * self._integral + self.Kd * derivative
    
    def reset(self):
        self._integral = 0
        self._previous_error = 0

class VesselController:
    """ The 'brain' of the vessel, containing all autonomous logic. """
    def __init__(self):
        self.mode = "MANUAL" # MANUAL, AUTOHELM, WAYPOINT, SEMI_AUTO
        
        # --- Autohelm & Waypoint Targets (0 deg = North) ---
        self.target_heading_deg = 0.0
        self.target_heading_rad = math.radians(self.target_heading_deg)
        self.target_speed_kts = 2.0
        self.heading_pid = PID(Kp=1.0, Ki=0.1, Kd=0.05)
        
        # --- Waypoint State ---
        self.waypoints = []
        self.current_waypoint_index = 0
        self.WAYPOINT_ARRIVAL_DISTANCE_M = 3.0

        # --- Semi-Auto Targets ---
        self.target_thrust = 0.0    # -1.0 to 1.0
        self.target_rudder = 0.0  # -1.0 to 1.0

    def set_mode(self, mode):
        if mode in ["MANUAL", "AUTOHELM", "WAYPOINT", "SEMI_AUTO"]:
            self.mode = mode
            print(f"Controller mode set to: {self.mode}")
            self.heading_pid.reset()
        else:
            print(f"Warning: Invalid mode '{mode}' requested.")

    def add_waypoint(self, lat, lon):
        self.waypoints.append((lat, lon))
        print(f"Added waypoint: ({lat:.5f}, {lon:.5f})")
    
    def get_manual_commands(self, keys):
        thrust_cmd = 0.0
        if keys[pygame.K_UP]: thrust_cmd = 1.0
        elif keys[pygame.K_DOWN]: thrust_cmd = -0.5
        
        rudder_cmd = 0.0
        if keys[pygame.K_LEFT]: rudder_cmd = 1.0
        elif keys[pygame.K_RIGHT]: rudder_cmd = -1.0
        return thrust_cmd, rudder_cmd

    def update(self, lat, lon, heading_rad, speed_mps):
        """ The main logic loop for the controller. """
        if self.mode == "AUTOHELM":
            error = self._wrap_angle(self.target_heading_rad - heading_rad)
            rudder_cmd = self.heading_pid.update(-error)
            thrust_cmd = (self.target_speed_kts / 1.94384) / 2.5
            return max(-1.0, min(1.0, thrust_cmd)), max(-1.0, min(1.0, rudder_cmd))
        
        elif self.mode == "SEMI_AUTO":
            return self.target_thrust, self.target_rudder

        elif self.mode == "WAYPOINT":
            if not self.waypoints or self.current_waypoint_index >= len(self.waypoints):
                return 0.0, 0.0

            target_wp = self.waypoints[self.current_waypoint_index]
            dist_to_wp = self._calculate_distance(lat, lon, target_wp[0], target_wp[1])
            
            if dist_to_wp < self.WAYPOINT_ARRIVAL_DISTANCE_M:
                self.current_waypoint_index += 1
                print(f"Arrived at waypoint. Moving to next.")
                if self.current_waypoint_index >= len(self.waypoints):
                    print("Final waypoint reached.")
                    return 0.0, 0.0
                target_wp = self.waypoints[self.current_waypoint_index]

            # --- Heading Calculation (Navigational Standard) ---
            delta_lon = target_wp[1] - lon
            delta_lat = target_wp[0] - lat
            # atan2(dx, dy) gives 0 for North
            target_heading = math.atan2(delta_lon, delta_lat)
            
            if target_heading < 0:
                target_heading += 2 * math.pi
            
            self.target_heading_rad = target_heading
            
            error = self._wrap_angle(self.target_heading_rad - heading_rad)
            rudder_cmd = self.heading_pid.update(-error)
            thrust_cmd = (self.target_speed_kts / 1.94384) / 2.5
            
            return max(-1.0, min(1.0, thrust_cmd)), max(-1.0, min(1.0, rudder_cmd))

        return 0.0, 0.0
    
    def _wrap_angle(self, angle):
        """ Wrap angle in radians to [-pi, pi]. """
        return (angle + math.pi) % (2 * math.pi) - math.pi

    def _calculate_distance(self, lat1, lon1, lat2, lon2):
        """ Calculate distance in meters between two lat/lon points (Haversine formula). """
        R = 6371e3 # Earth radius in meters
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lon2 - lon1)

        a = math.sin(delta_phi / 2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c

