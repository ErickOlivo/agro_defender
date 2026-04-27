import pygame
import sys
from src.config import WINDOW_WIDTH, WINDOW_HEIGHT, FPS, COLOR_BLACK
from src.entities.player import Player
from src.vision_worker import VisionWorker  # NEW: Import the CV thread

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
        
        # NEW: Initialize the background vision worker
        self.vision_worker = VisionWorker()

    def handle_events(self):
        """Processes window events and keystrokes."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

    def update_state(self):
        """Updates physics, positions, and game logic."""
        # NEW: Read coordinates from the background vision thread instead of the mouse
        target_x = self.vision_worker.hand_x
        target_y = self.vision_worker.hand_y
        
        # Send the real-time CV coordinates to the player entity
        self.player.set_position(target_x, target_y)
        
        # Safely calls the parameterless .update() on all sprites
        self.all_sprites.update()

    def render(self):
        """Draws all elements to the screen."""
        self.screen.fill(COLOR_BLACK)
        self.all_sprites.draw(self.screen)
        pygame.display.flip()

    def run(self):
        """The main game loop. Blocks the main thread until game exit."""
        print("[INFO] Starting Vision Worker Thread... (Webcam should turn on)")
        self.vision_worker.start()  # NEW: Start the background camera thread
        
        while self.running:
            self.handle_events()
            self.update_state()
            self.render()
            
            # Lock the framerate
            self.clock.tick(FPS)
            
        print("[INFO] Shutting down camera and engine...")
        self.vision_worker.stop()  # NEW: Safely release the webcam
        pygame.quit()
        sys.exit()
