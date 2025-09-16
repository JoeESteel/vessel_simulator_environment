import pygame
import sys
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
        # Get key states once per frame for continuous presses
        keys = pygame.key.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            world.handle_event(event)
            
            # Handle one-press key events for mode changes
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_m: controller.set_mode("MANUAL")
                if event.key == pygame.K_a: controller.set_mode("AUTOHELM")
                if event.key == pygame.K_s: controller.set_mode("SEMI_AUTO") # FIX: Added key for SEMI_AUTO
                if event.key == pygame.K_w: 
                    controller.set_mode("WAYPOINT")
                    controller.target_speed_kts = 2.0
            
            # Handle mouse clicks for waypoints
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: # Left click
                    lat, lon = world.camera.screen_to_world(event.pos[0], event.pos[1])
                    controller.add_waypoint(lat, lon)

        # --- Control Logic ---
        # FIX: Created a proper if/elif structure for all modes
        if controller.mode == "MANUAL":
            thrust_cmd, rudder_cmd = controller.get_manual_commands(keys)
            vessel.thrust = thrust_cmd
            vessel.rudder_angle = rudder_cmd
        
        elif controller.mode == "SEMI_AUTO":
            # Handle continuous key presses for adjusting semi-auto targets
            if keys[pygame.K_q]: controller.target_thrust = min(1.0, controller.target_thrust + 0.01)
            if keys[pygame.K_a]: controller.target_thrust = max(-1.0, controller.target_thrust - 0.01)
            if keys[pygame.K_z]: controller.target_rudder = min(1.0, controller.target_rudder + 0.01)
            if keys[pygame.K_x]: controller.target_rudder = max(-1.0, controller.target_rudder - 0.01)

            thrust_cmd, rudder_cmd = controller.update(None, None, None, None) # state not needed
            vessel.thrust = thrust_cmd
            vessel.rudder_angle = rudder_cmd

        else: # AUTOHELM or WAYPOINT
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
        
        pygame.display.flip()
        world.clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()