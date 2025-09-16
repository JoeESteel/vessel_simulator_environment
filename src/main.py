import pygame
import sys
import math
from .world import World
from .vessel import Vessel
from .controller import VesselController

def main():
    """ The main entry point for the application. """
    pygame.init()

    # --- Initialization ---
    world = World()
    vessel = Vessel(start_lat=50.88, start_lon=-1.38)
    controller = VesselController()

    # --- Main Loop ---
    running = True
    while running:
        # --- Event Handling ---
        keys = pygame.key.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            world.handle_event(event)
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_m: controller.set_mode("MANUAL")
                if event.key == pygame.K_s: controller.set_mode("SEMI_AUTO")
                if event.key == pygame.K_w: 
                    controller.set_mode("WAYPOINT")
                    controller.target_speed_kts = 2.0
                # When activating AUTOHELM, set target to current heading
                if event.key == pygame.K_a: 
                    controller.set_mode("AUTOHELM")
                    controller.target_heading_deg = math.degrees(vessel.heading) % 360

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    lat, lon = world.camera.screen_to_world(event.pos[0], event.pos[1])
                    controller.add_waypoint(lat, lon)

        # --- Control Logic ---
        if controller.mode == "MANUAL":
            thrust_cmd, rudder_cmd = controller.get_manual_commands(keys)
            vessel.thrust = thrust_cmd
            vessel.rudder_angle = rudder_cmd
        
        elif controller.mode == "SEMI_AUTO":
            if keys[pygame.K_q]: controller.target_thrust = min(1.0, controller.target_thrust + 0.01)
            if keys[pygame.K_a]: controller.target_thrust = max(-1.0, controller.target_thrust - 0.01)
            if keys[pygame.K_z]: controller.target_rudder = min(1.0, controller.target_rudder + 0.01)
            if keys[pygame.K_x]: controller.target_rudder = max(-1.0, controller.target_rudder - 0.01)

            thrust_cmd, rudder_cmd = controller.update(
                vessel.lat, vessel.lon, vessel.heading, vessel.speed_mps
            )
            vessel.thrust = thrust_cmd
            vessel.rudder_angle = rudder_cmd

        elif controller.mode == "AUTOHELM":
            # Allow user to adjust target heading with arrow keys
            if keys[pygame.K_LEFT]:
                controller.target_heading_deg = (controller.target_heading_deg - 0.5) % 360
            if keys[pygame.K_RIGHT]:
                controller.target_heading_deg = (controller.target_heading_deg + 0.5) % 360
            
            thrust_cmd, rudder_cmd = controller.update(
                vessel.lat, vessel.lon, vessel.heading, vessel.speed_mps
            )
            vessel.thrust = thrust_cmd
            vessel.rudder_angle = rudder_cmd

        elif controller.mode == "WAYPOINT":
            thrust_cmd, rudder_cmd = controller.update(
                vessel.lat, vessel.lon, vessel.heading, vessel.speed_mps
            )
            vessel.thrust = thrust_cmd
            vessel.rudder_angle = rudder_cmd

        # --- Update Physics and World State ---
        vessel.update()
        world.update(vessel)

        # --- Drawing ---
        world.draw(vessel, controller)
        
        pygame.display.flip()
        world.clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()