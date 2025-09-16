import pygame
import math
import sys

# --- Constants ---
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 800
BACKGROUND_COLOR = (20, 40, 60) # Deep blue
VESSEL_COLOR = (255, 100, 100) # Red
TEXT_COLOR = (230, 230, 230)

class Vessel:
    """
    Represents a vessel with basic physics.
    It responds to thrust and rudder inputs.
    """
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.heading = math.radians(90) # Start pointing North (up). Radians are used for math.
        self.speed = 0.0
        
        # Control inputs
        self.thrust = 0.0 # -1.0 (reverse) to 1.0 (full ahead)
        self.rudder_angle = 0.0 # -1.0 (hard left) to 1.0 (hard right)
        
        # Vessel characteristics
        self.size = 15
        self.max_speed = 5.0
        self.acceleration = 0.02
        self.drag = 0.01 # Simple friction
        self.turn_rate = 0.05 # How quickly it turns

    def update(self):
        """ Updates the vessel's state based on physics and control inputs. """
        
        # 1. Apply thrust to change speed
        target_speed = self.thrust * self.max_speed
        # Smoothly accelerate or decelerate towards the target speed
        self.speed += (target_speed - self.speed) * self.acceleration
        
        # 2. Apply drag to slow down
        if self.speed > 0:
            self.speed -= self.drag
            if self.speed < 0: self.speed = 0
        elif self.speed < 0:
             self.speed += self.drag
             if self.speed > 0: self.speed = 0

        # 3. Apply rudder to change heading
        if abs(self.speed) > 0.1: # Can only turn when moving
            # The faster you go, the more effective the rudder
            turn_effectiveness = self.rudder_angle * (abs(self.speed) / self.max_speed)
            self.heading -= turn_effectiveness * self.turn_rate
        
        # 4. Update position based on heading and speed
        # Note: We use -sin for y because Pygame's y-axis is inverted (0 is at the top)
        self.x += math.cos(self.heading) * self.speed
        self.y -= math.sin(self.heading) * self.speed
        
        # 5. Screen wrapping (teleport to the other side if you go off-screen)
        if self.x > SCREEN_WIDTH: self.x = 0
        if self.x < 0: self.x = SCREEN_WIDTH
        if self.y > SCREEN_HEIGHT: self.y = 0
        if self.y < 0: self.y = SCREEN_HEIGHT

    def draw(self, screen):
        """ Draws the vessel on the screen. """
        # A simple triangle shape for the vessel
        # Tip of the triangle
        p1 = (
            self.x + self.size * math.cos(self.heading),
            self.y - self.size * math.sin(self.heading)
        )
        # Rear left
        p2 = (
            self.x + self.size * math.cos(self.heading + math.radians(140)),
            self.y - self.size * math.sin(self.heading + math.radians(140))
        )
        # Rear right
        p3 = (
            self.x + self.size * math.cos(self.heading - math.radians(140)),
            self.y - self.size * math.sin(self.heading - math.radians(140))
        )
        pygame.draw.polygon(screen, VESSEL_COLOR, [p1, p2, p3])

def main():
    """ The main function to run the simulator. """
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Basic Vessel Simulator")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 30)

    # Create the vessel in the center of the screen
    vessel = Vessel(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)

    running = True
    while running:
        # --- Event Handling ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        # --- Keyboard Input ---
        keys = pygame.key.get_pressed()
        
        # Thrust control
        if keys[pygame.K_UP]:
            vessel.thrust = 1.0
        elif keys[pygame.K_DOWN]:
            vessel.thrust = -0.5 # Slower reverse
        else:
            vessel.thrust = 0.0 # Coast
            
        # Rudder control
        if keys[pygame.K_LEFT]:
            vessel.rudder_angle = 1.0
        elif keys[pygame.K_RIGHT]:
            vessel.rudder_angle = -1.0
        else:
            vessel.rudder_angle = 0.0 # Straighten rudder

        # --- Update ---
        vessel.update()

        # --- Drawing ---
        screen.fill(BACKGROUND_COLOR)
        vessel.draw(screen)

        # Display status text
        info_text = (
            f"Speed: {vessel.speed:.1f} | "
            f"Heading: {math.degrees(vessel.heading) % 360:.0f}° | "
            f"Thrust: {vessel.thrust:.1f} | "
            f"Rudder: {vessel.rudder_angle:.1f}"
        )
        text_surface = font.render(info_text, True, TEXT_COLOR)
        screen.blit(text_surface, (10, 10))
        
        # Update the display
        pygame.display.flip()

        # Cap the frame rate
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
