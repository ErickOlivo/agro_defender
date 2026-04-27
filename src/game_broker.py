import pygame
import sys
from src.config import WINDOW_WIDTH, WINDOW_HEIGHT, FPS, COLOR_BLACK
from src.entities.player import Player

class GameBroker:
    """
    Main game engine responsible for rendering and game state management.
    Runs entirely on the main thread at a fixed FPS.
    """
    def __init__(self):
        # Initialize Pygame engine
        pygame.init()
        
        # Setup display
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Agro-Defender: Mission Rescue")
        
        # Clock restricts the while-loop to a specific FPS
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Initialize game entities
        self.player = Player()
        
        # Sprite groups for optimized rendering
        self.all_sprites = pygame.sprite.Group()
        self.all_sprites.add(self.player)

    def handle_events(self):
        """Processes window events and keystrokes."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

    def update_state(self):
        """Updates physics, positions, and game logic."""
        # For Phase 2: Simulate the CV Hand Tracking using the mouse position
        mouse_x, mouse_y = pygame.mouse.get_pos()
        
        # Send the simulated coordinates to the player entity using the new method
        self.player.set_position(mouse_x, mouse_y)
        
        # Safely calls the parameterless .update() on all sprites (enemies, etc.)
        self.all_sprites.update()

    def render(self):
        """Draws all elements to the screen."""
        # Clear the previous frame
        self.screen.fill(COLOR_BLACK)
        
        # Draw all active sprites
        self.all_sprites.draw(self.screen)
        
        # Swap the display buffer to screen
        pygame.display.flip()

    def run(self):
        """The main game loop. Blocks the main thread until game exit."""
        while self.running:
            self.handle_events()
            self.update_state()
            self.render()
            
            # Lock the framerate
            self.clock.tick(FPS)
            
        pygame.quit()
        sys.exit()
