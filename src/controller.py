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

    def update(self, measured_value, dt=1):
        error = self.setpoint - measured_value
        self._integral += error * dt
        derivative = (error - self._previous_error) / dt if dt > 0 else 0
        self._previous_error = error
        output = self.Kp * error + self.Ki * self._integral + self.Kd * derivative
        return output
    
    def reset(self):
        self._integral = 0
        self._previous_error = 0

class VesselController:
    def __init__(self):
        self.mode = "MANUAL"
        
        # --- PID Controllers ---
        self.heading_pid = PID(Kp=0.8, Ki=0.02, Kd=0.1)
        self.speed_pid = PID(Kp=0.5, Ki=0.1, Kd=0.05) 

        # --- Autonomous Targets ---
        self.target_heading_deg = 0.0
        self.target_speed_kts = 0.0
        
        # --- Waypoint State ---
        self.waypoints = []
        self.current_waypoint_index = 0
        self.WAYPOINT_ARRIVAL_DISTANCE_M = 7.0
        self.cross_track_error_m = 0.0

        # --- NEW: Tunable Waypoint Arrival Parameters ---
        self.APPROACH_SPEED_LIMIT_DISTANCE_M = 50.0 # Start slowing down 50m away
        self.HARD_STEERING_ANGLE_DEG = 90.0
        self.NORMAL_STEERING_ANGLE_DEG = 20.0
        self.HARD_RUDDER_CMD = 1.0
        self.NORMAL_RUDDER_CMD = 0.6

        # --- Semi-Auto Targets ---
        self.target_thrust = 0.0
        self.target_rudder = 0.0

    def set_mode(self, mode):
        if mode in ["MANUAL", "AUTOHELM", "WAYPOINT", "SEMI_AUTO"]:
            self.mode = mode
            print(f"Controller mode set to: {self.mode}")
            self.heading_pid.reset()
            self.speed_pid.reset()
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
                self.current_waypoint_index = max(0, len(self.waypoints) - 1)
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
        thrust_cmd, rudder_cmd = 0.0, 0.0

        if self.mode == "MANUAL":
             return None, None 

        elif self.mode == "SEMI_AUTO":
            self.cross_track_error_m = 0.0 # No XTE in this mode
            return self.target_thrust, self.target_rudder

        elif self.mode == "AUTOHELM":
            self.cross_track_error_m = 0.0 # No XTE in this mode
            target_speed_mps = self.target_speed_kts * 0.514444
            self.speed_pid.setpoint = target_speed_mps
            thrust_cmd = self.speed_pid.update(speed_mps)
            
            target_heading_rad = math.radians(self.target_heading_deg)
            error = self._wrap_angle(target_heading_rad - heading_rad)
            rudder_cmd = self.heading_pid.update(error)
        
        elif self.mode == "WAYPOINT":
            if not self.waypoints or self.current_waypoint_index >= len(self.waypoints):
                self.cross_track_error_m = 0.0
                return 0.0, 0.0

            target_wp = self.waypoints[self.current_waypoint_index]
            dist_to_wp = self._calculate_distance(lat, lon, target_wp[0], target_wp[1])

            # --- FIX: Calculate XTE for UI display ---
            start_wp = self.waypoints[self.current_waypoint_index - 1] if self.current_waypoint_index > 0 else (lat, lon)
            self.cross_track_error_m = self._calculate_distance_to_track(lat, lon, start_wp[0], start_wp[1], target_wp[0], target_wp[1])

            if dist_to_wp < self.WAYPOINT_ARRIVAL_DISTANCE_M:
                self.current_waypoint_index += 1
                if self.current_waypoint_index >= len(self.waypoints):
                    print("Final waypoint reached.")
                    return 0.0, 0.0
                else:
                    print(f"Waypoint {self.current_waypoint_index} reached. Proceeding to next.")

            # --- Speed Limiter on Approach ---
            current_target_speed_kts = self.target_speed_kts
            if dist_to_wp < self.APPROACH_SPEED_LIMIT_DISTANCE_M:
                scale = max(0.2, dist_to_wp / self.APPROACH_SPEED_LIMIT_DISTANCE_M)
                current_target_speed_kts *= scale
            
            target_speed_mps = current_target_speed_kts * 0.514444
            self.speed_pid.setpoint = target_speed_mps
            thrust_cmd = self.speed_pid.update(speed_mps)

            # --- Tiered Rudder Control based on Bearing ---
            bearing_to_wp_rad = self._calculate_bearing(lat, lon, target_wp[0], target_wp[1])
            heading_error_rad = self._wrap_angle(bearing_to_wp_rad - heading_rad)
            heading_error_deg = abs(math.degrees(heading_error_rad))
            
            rudder_direction = 1.0 if heading_error_rad > 0 else -1.0

            if heading_error_deg > self.HARD_STEERING_ANGLE_DEG:
                rudder_cmd = self.HARD_RUDDER_CMD * -rudder_direction
            elif heading_error_deg > self.NORMAL_STEERING_ANGLE_DEG:
                rudder_cmd = self.NORMAL_RUDDER_CMD * -rudder_direction
            else:
                rudder_cmd = self.heading_pid.update(heading_error_rad)

        # Clamp all final commands
        thrust_cmd = max(-1.0, min(1.0, thrust_cmd))
        rudder_cmd = max(-1.0, min(1.0, rudder_cmd))
        return thrust_cmd, rudder_cmd

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
        delta_lon = math.radians(lon2 - lon1)
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        y = math.sin(delta_lon) * math.cos(lat2_rad)
        x = math.cos(lat1_rad) * math.sin(lat2_rad) - math.sin(lat1_rad) * math.cos(lat2_rad) * math.cos(delta_lon)
        bearing = math.atan2(y, x)
        return (bearing + 2 * math.pi) % (2 * math.pi)

    def _calculate_distance_to_track(self, lat_p, lon_p, lat_1, lon_1, lat_2, lon_2):
        bearing_to_point = self._calculate_bearing(lat_1, lon_1, lat_p, lon_p)
        track_bearing = self._calculate_bearing(lat_1, lon_1, lat_2, lon_2)
        distance_from_start = self._calculate_distance(lat_1, lon_1, lat_p, lon_p)
        angle_diff = self._wrap_angle(bearing_to_point - track_bearing)
        xts = math.sin(angle_diff) * distance_from_start
        return xts


