import pygame
import sys
from world import World
from vessel import Vessel
from controller import VesselController

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
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # Pass events to the world for camera control
            world.handle_event(event)
            
            # Pass events to the controller for mode changes and waypoint setting
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: # Left click
                    lat, lon = world.camera.screen_to_world(event.pos[0], event.pos[1])
                    controller.add_waypoint(lat, lon)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_m: controller.set_mode("MANUAL")
                if event.key == pygame.K_a: controller.set_mode("AUTOHELM")
                if event.key == pygame.K_w: 
                    controller.set_mode("WAYPOINT")
                    controller.target_speed_kts = 2.0

        # --- Control Logic ---
        if controller.mode == "MANUAL":
            # Get keyboard state for manual control
            keys = pygame.key.get_pressed()
            thrust_cmd, rudder_cmd = controller.get_manual_commands(keys)
            vessel.thrust = thrust_cmd
            vessel.rudder_angle = rudder_cmd
        else:
            # In autonomous modes, the controller provides the commands
            thrust_cmd, rudder_cmd = controller.update(
                vessel.lat, vessel.lon, vessel.heading, vessel.speed_mps
            )
            vessel.thrust = thrust_cmd
            vessel.rudder_angle = rudder_cmd

        # --- Update Physics and World State ---
        vessel.update()
        world.update(vessel) # Update camera and track

        # --- Drawing ---
        world.draw(vessel, controller)
        
        # Update the display
        pygame.display.flip()
        world.clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
