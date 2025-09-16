import math
import pygame

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
        if abs(error) < 0.5:
             self._integral += error
        else:
             self._integral = 0
        derivative = error - self._previous_error
        self._previous_error = error
        output = self.Kp * error + self.Ki * self._integral + self.Kd * derivative
        return max(-1.0, min(1.0, output))
    
    def reset(self):
        self._integral = 0
        self._previous_error = 0

class VesselController:
    def __init__(self):
        self.mode = "MANUAL"
        
        self.target_heading_deg = 0.0
        self.target_speed_kts = 2.0
        self.heading_pid = PID(Kp=0.8, Ki=0.02, Kd=0.1)
        
        self.waypoints = []
        self.current_waypoint_index = 0
        self.WAYPOINT_ARRIVAL_DISTANCE_M = 5.0

        self.cross_track_error_m = 0.0

        self.target_thrust = 0.0
        self.target_rudder = 0.0

    def set_mode(self, mode):
        if mode in ["MANUAL", "AUTOHELM", "WAYPOINT", "SEMI_AUTO"]:
            self.mode = mode
            print(f"Controller mode set to: {self.mode}")
            self.heading_pid.reset()
        else:
            print(f"Warning: Invalid mode '{mode}' requested.")

    def add_waypoint(self, lat, lon):
        self.waypoints.append((lat, lon))
        print(f"Added waypoint {len(self.waypoints)}: ({lat:.5f}, {lon:.5f})")
    
    def clear_waypoints(self):
        self.waypoints = []
        self.current_waypoint_index = 0
        print("All waypoints cleared.")

    def remove_last_waypoint(self):
        if self.waypoints:
            self.waypoints.pop()
            if self.current_waypoint_index >= len(self.waypoints):
                self.current_waypoint_index = max(0, len(self.waypoints) -1)
            print("Removed last waypoint.")
    
    def get_manual_commands(self, keys):
        thrust_cmd = 0.0
        if keys[pygame.K_UP]: thrust_cmd = 1.0
        elif keys[pygame.K_DOWN]: thrust_cmd = -0.5
        
        rudder_cmd = 0.0
        if keys[pygame.K_LEFT]: rudder_cmd = 1.0
        elif keys[pygame.K_RIGHT]: rudder_cmd = -1.0
        return thrust_cmd, rudder_cmd

    def update(self, lat, lon, heading_rad, speed_mps):
        if self.mode == "AUTOHELM":
            self.cross_track_error_m = 0.0
            target_heading_rad = math.radians(self.target_heading_deg)
            error = self._wrap_angle(target_heading_rad - heading_rad)
            rudder_cmd = self.heading_pid.update(error)
            thrust_cmd = (self.target_speed_kts / 1.94384) / 2.5
            return thrust_cmd, rudder_cmd
        
        elif self.mode == "SEMI_AUTO":
            self.cross_track_error_m = 0.0
            return self.target_thrust, self.target_rudder

        elif self.mode == "WAYPOINT":
            if not self.waypoints or self.current_waypoint_index >= len(self.waypoints):
                self.cross_track_error_m = 0.0
                return 0.0, 0.0

            target_wp = self.waypoints[self.current_waypoint_index]
            dist_to_wp = self._calculate_distance(lat, lon, target_wp[0], target_wp[1])
            
            if dist_to_wp < self.WAYPOINT_ARRIVAL_DISTANCE_M:
                self.current_waypoint_index += 1
                if self.current_waypoint_index >= len(self.waypoints):
                    print("Final waypoint reached.")
                    return 0.0, 0.0
            
            start_wp = self.waypoints[self.current_waypoint_index - 1] if self.current_waypoint_index > 0 else (lat, lon)
            target_wp = self.waypoints[self.current_waypoint_index]
            
            self.cross_track_error_m = self._calculate_distance_to_track(lat, lon, start_wp[0], start_wp[1], target_wp[0], target_wp[1])
            track_bearing_rad = self._calculate_bearing(start_wp[0], start_wp[1], target_wp[0], target_wp[1])

            correction_angle = math.atan2(-self.cross_track_error_m, max(10, speed_mps * 5))
            target_heading_rad = self._wrap_angle(track_bearing_rad + correction_angle)
            
            self.target_heading_deg = math.degrees(target_heading_rad) % 360
            
            error = self._wrap_angle(target_heading_rad - heading_rad)
            rudder_cmd = self.heading_pid.update(error)
            thrust_cmd = (self.target_speed_kts / 1.94384) / 2.5
            return thrust_cmd, rudder_cmd

        self.cross_track_error_m = 0.0
        return 0.0, 0.0
    
    def _wrap_angle(self, angle):
        return (angle + math.pi) % (2 * math.pi) - math.pi

    def _calculate_distance(self, lat1, lon1, lat2, lon2):
        R = 6371e3
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lon2 - lon1)
        a = math.sin(delta_phi / 2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c
        
    def _calculate_bearing(self, lat1, lon1, lat2, lon2):
        # FIX: Corrected the bearing calculation.
        # This formula correctly calculates the initial bearing from point 1 to 2.
        delta_lon = math.radians(lon2 - lon1)
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        
        y = math.sin(delta_lon) * math.cos(lat2_rad)
        x = math.cos(lat1_rad) * math.sin(lat2_rad) - math.sin(lat1_rad) * math.cos(lat2_rad) * math.cos(delta_lon)
        
        # atan2(y, x) returns the bearing in radians from North.
        bearing = math.atan2(y, x)
        return (bearing + 2 * math.pi) % (2 * math.pi) # Normalize to 0-2pi

    def _calculate_distance_to_track(self, lat_p, lon_p, lat_1, lon_1, lat_2, lon_2):
        bearing_to_point = self._calculate_bearing(lat_1, lon_1, lat_p, lon_p)
        track_bearing = self._calculate_bearing(lat_1, lon_1, lat_2, lon_2)
        distance_from_start = self._calculate_distance(lat_1, lon_1, lat_p, lon_p)
        
        angle_diff = self._wrap_angle(bearing_to_point - track_bearing)
        xts = math.sin(angle_diff) * distance_from_start
        return xts

