import pygame
import math

# --- Constants ---
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 800
BACKGROUND_COLOR = (20, 40, 60)
TEXT_COLOR = (230, 230, 230)
GRID_COLOR = (50, 80, 110)
BREADCRUMB_COLOR = (255, 255, 0)
TRACK_LINE_COLOR = (200, 200, 100)
WAYPOINT_COLOR = (0, 255, 0)
WAYPOINT_LINE_COLOR = (0, 150, 0)
ACTIVE_LEG_COLOR = (255, 0, 255)
HEADING_LINE_COLOR = (255, 100, 100, 150)
ARRIVAL_CIRCLE_COLOR = (0, 255, 255, 100) # Semi-transparent cyan

# --- World Constants ---
METERS_PER_DEGREE_LAT = 111132.954
METERS_PER_DEGREE_LON = 111320 * math.cos(math.radians(50.88))

class Camera:
    def __init__(self, lat, lon):
        self.lat = lat
        self.lon = lon
        self.lon_span = 0.04
        self.min_lon_span = 0.0001
        self.max_lon_span = 0.2

    def update(self, target_lat, target_lon):
        self.lat += (target_lat - self.lat) * 0.1
        self.lon += (target_lon - self.lon) * 0.1

    def zoom(self, amount):
        self.lon_span *= amount
        self.lon_span = max(self.min_lon_span, min(self.max_lon_span, self.lon_span))

    def world_to_screen(self, lat, lon):
        pixels_per_degree_lon = SCREEN_WIDTH / self.lon_span
        pixels_per_degree_lat = pixels_per_degree_lon * (METERS_PER_DEGREE_LAT / METERS_PER_DEGREE_LON)
        x = SCREEN_WIDTH / 2 + (lon - self.lon) * pixels_per_degree_lon
        y = SCREEN_HEIGHT / 2 - (lat - self.lat) * pixels_per_degree_lat
        return int(x), int(y)

    def screen_to_world(self, x, y):
        pixels_per_degree_lon = SCREEN_WIDTH / self.lon_span
        pixels_per_degree_lat = pixels_per_degree_lon * (METERS_PER_DEGREE_LAT / METERS_PER_DEGREE_LON)
        lon = self.lon + (x - SCREEN_WIDTH / 2) / pixels_per_degree_lon
        lat = self.lat - (y - SCREEN_HEIGHT / 2) / pixels_per_degree_lat
        return lat, lon
        
    def meters_to_pixels(self, meters):
        world_width_m = self.lon_span * METERS_PER_DEGREE_LON
        if world_width_m > 0:
            return (meters / world_width_m) * SCREEN_WIDTH
        return 1

class World:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Vessel Simulator | (C)lear WPs, (Backspace)Remove Last")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 24)
        self.info_font = pygame.font.Font(None, 30)
        self.camera = Camera(50.88, -1.38)

        self.track_points = []
        self.breadcrumbs = []
        self.last_breadcrumb_time = 0
        self.BREADCRUMB_INTERVAL_MS = 3000
        self.start_time = pygame.time.get_ticks()

    def handle_event(self, event):
        if event.type == pygame.MOUSEWHEEL:
            if event.y > 0: self.camera.zoom(0.8)
            elif event.y < 0: self.camera.zoom(1.2)

    def update(self, vessel):
        self.camera.update(vessel.lat, vessel.lon)
        current_time = pygame.time.get_ticks()
        self.track_points.append((vessel.lat, vessel.lon))
        if current_time - self.last_breadcrumb_time > self.BREADCRUMB_INTERVAL_MS:
            self.breadcrumbs.append((vessel.lat, vessel.lon))
            self.last_breadcrumb_time = current_time

    def draw(self, vessel, controller):
        self.screen.fill(BACKGROUND_COLOR)
        self._draw_grid()
        self._draw_track()
        self._draw_waypoints(vessel, controller)
        vessel.draw(self.screen, self.camera)
        self._draw_ui(vessel, controller)
        self._draw_scale_bar()
        self._draw_heading_line(vessel)

    def _draw_grid(self):
        top_left_lat, top_left_lon = self.camera.screen_to_world(0, 0)
        bottom_right_lat, bottom_right_lon = self.camera.screen_to_world(SCREEN_WIDTH, SCREEN_HEIGHT)

        lon_span = bottom_right_lon - top_left_lon
        grid_interval = 0.001
        if lon_span > 0.02: grid_interval = 0.01
        if lon_span > 0.2: grid_interval = 0.1

        lon_start = math.floor(top_left_lon / grid_interval) * grid_interval
        for i in range(int(lon_span / grid_interval) + 2):
            lon = lon_start + i * grid_interval
            start_pos = self.camera.world_to_screen(top_left_lat, lon)
            end_pos = self.camera.world_to_screen(bottom_right_lat, lon)
            pygame.draw.line(self.screen, GRID_COLOR, start_pos, end_pos)

        lat_span = top_left_lat - bottom_right_lat
        lat_start = math.floor(bottom_right_lat / grid_interval) * grid_interval
        for i in range(int(lat_span / grid_interval) + 2):
            lat = lat_start + i * grid_interval
            start_pos = self.camera.world_to_screen(lat, top_left_lon)
            end_pos = self.camera.world_to_screen(lat, bottom_right_lon)
            pygame.draw.line(self.screen, GRID_COLOR, start_pos, end_pos)

    def _draw_track(self):
        if len(self.track_points) > 1:
            points = [self.camera.world_to_screen(lat, lon) for lat, lon in self.track_points]
            pygame.draw.lines(self.screen, TRACK_LINE_COLOR, False, points, 1)
        for lat, lon in self.breadcrumbs:
            sx, sy = self.camera.world_to_screen(lat, lon)
            pygame.draw.circle(self.screen, BREADCRUMB_COLOR, (sx, sy), 2)

    def _draw_waypoints(self, vessel, controller):
        waypoints = controller.waypoints
        if not waypoints: return
        
        if len(waypoints) > 1:
            points = [self.camera.world_to_screen(lat, lon) for lat, lon in waypoints]
            pygame.draw.lines(self.screen, WAYPOINT_LINE_COLOR, False, points, 2)
        
        if controller.mode == "WAYPOINT" and controller.current_waypoint_index < len(waypoints):
            start_idx = controller.current_waypoint_index -1
            end_idx = controller.current_waypoint_index
            if start_idx >= 0:
                start_pos = self.camera.world_to_screen(waypoints[start_idx][0], waypoints[start_idx][1])
            else:
                start_pos = self.camera.world_to_screen(vessel.lat, vessel.lon)
            end_pos = self.camera.world_to_screen(waypoints[end_idx][0], waypoints[end_idx][1])
            pygame.draw.line(self.screen, ACTIVE_LEG_COLOR, start_pos, end_pos, 3)
            
            arrival_radius_pixels = self.camera.meters_to_pixels(controller.WAYPOINT_ARRIVAL_DISTANCE_M)
            if arrival_radius_pixels > 1:
                target_surface = pygame.Surface((arrival_radius_pixels*2, arrival_radius_pixels*2), pygame.SRCALPHA)
                pygame.draw.circle(target_surface, ARRIVAL_CIRCLE_COLOR, (arrival_radius_pixels, arrival_radius_pixels), int(arrival_radius_pixels))
                self.screen.blit(target_surface, (end_pos[0] - arrival_radius_pixels, end_pos[1] - arrival_radius_pixels))

        for i, (lat, lon) in enumerate(waypoints):
            sx, sy = self.camera.world_to_screen(lat, lon)
            color = ACTIVE_LEG_COLOR if i == controller.current_waypoint_index else WAYPOINT_COLOR
            pygame.draw.circle(self.screen, color, (sx, sy), 6)
            pygame.draw.circle(self.screen, (0,0,0), (sx, sy), 6, 1)
            num_surface = self.font.render(str(i + 1), True, TEXT_COLOR)
            self.screen.blit(num_surface, (sx + 10, sy - 10))
    
    def _draw_heading_line(self, vessel):
        start_pos = self.camera.world_to_screen(vessel.lat, vessel.lon)
        line_length = 50
        end_x = start_pos[0] + line_length * math.sin(vessel.heading)
        end_y = start_pos[1] - line_length * math.cos(vessel.heading)
        pygame.draw.line(self.screen, HEADING_LINE_COLOR, start_pos, (end_x, end_y), 2)

    def _draw_ui(self, vessel, controller):
        current_time = pygame.time.get_ticks()
        elapsed_seconds = (current_time - self.start_time) // 1000
        timer_text = f"T: {elapsed_seconds // 60:02d}:{elapsed_seconds % 60:02d}"
        knots = vessel.speed_mps * 1.94384
        
        mode_text = f"Mode: {controller.mode}"
        if controller.mode == "AUTOHELM":
             mode_text += f" (Target: {controller.target_heading_deg:.0f}° @ {controller.target_speed_kts:.1f} kts)"
        elif controller.mode == "WAYPOINT" and controller.waypoints:
             wp_text = f" (WP {min(controller.current_waypoint_index + 1, len(controller.waypoints))}/{len(controller.waypoints)})"
             xt_text = f" (XTE: {controller.cross_track_error_m:.1f}m)"
             mode_text += wp_text + xt_text
        elif controller.mode == "SEMI_AUTO":
            mode_text += f" (Thrust: {controller.target_thrust*100:.0f}%, Rudder: {controller.target_rudder*100:.0f}%)"
        
        # FIX: Corrected the typo from 'v' to 'vessel'
        info_text = (
            f"Lat: {vessel.lat:.5f} | Lon: {vessel.lon:.5f} | "
            f"Speed: {knots:.1f} kts | "
            f"Heading: {math.degrees(vessel.heading) % 360:.0f}°"
        )

        timer_surface = self.info_font.render(timer_text, True, TEXT_COLOR)
        info_surface = self.info_font.render(info_text, True, TEXT_COLOR)
        mode_surface = self.info_font.render(mode_text, True, TEXT_COLOR)
        self.screen.blit(mode_surface, (10, 10))
        self.screen.blit(info_surface, (10, SCREEN_HEIGHT - 35))
        self.screen.blit(timer_surface, (SCREEN_WIDTH - 120, 10))
        
    def _draw_scale_bar(self):
        world_width_m = self.camera.lon_span * METERS_PER_DEGREE_LON
        target_scale_m = world_width_m / 8.0
        
        if target_scale_m <= 0: return
        
        power_of_10 = 10**math.floor(math.log10(target_scale_m))
        relative_value = target_scale_m / power_of_10
        if relative_value < 2: nice_scale_m = 1 * power_of_10
        elif relative_value < 5: nice_scale_m = 2 * power_of_10
        else: nice_scale_m = 5 * power_of_10
        
        scale_bar_pixels = (nice_scale_m / world_width_m) * SCREEN_WIDTH
        
        x, y = 30, SCREEN_HEIGHT - 60
        
        pygame.draw.line(self.screen, TEXT_COLOR, (x, y), (x + scale_bar_pixels, y), 2)
        pygame.draw.line(self.screen, TEXT_COLOR, (x, y - 5), (x, y + 5), 2)
        pygame.draw.line(self.screen, TEXT_COLOR, (x + scale_bar_pixels, y - 5), (x + scale_bar_pixels, y + 5), 2)
        
        label = f"{int(nice_scale_m)} m" if nice_scale_m >=1 else f"{nice_scale_m:.1f} m"
        text_surface = self.font.render(label, True, TEXT_COLOR)
        text_rect = text_surface.get_rect(centerx=x + scale_bar_pixels / 2, y=y - 25)
        self.screen.blit(text_surface, text_rect)

