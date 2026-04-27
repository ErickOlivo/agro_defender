import pygame
import os
from src.config import WINDOW_WIDTH, WINDOW_HEIGHT

class Plant(pygame.sprite.Sprite):
    """
    Represents the Mother Plant using a loaded sprite.
    """
    def __init__(self):
        super().__init__()
        
        # Load the plant sprite image
        image_path = os.path.join("assets", "images", "plant.png")
        try:
            original_image = pygame.image.load(image_path).convert_alpha()
            # Scale the plant to be large and visible at the bottom (e.g., 150x200)
            self.image = pygame.transform.smoothscale(original_image, (150, 200))
        except FileNotFoundError:
            self.image = pygame.Surface((200, 80))
            self.image.fill((34, 139, 34))
            
        self.rect = self.image.get_rect()
        self.rect.centerx = WINDOW_WIDTH // 2
        # Place it right at the bottom of the window
        self.rect.bottom = WINDOW_HEIGHT
        
    def update(self):
        pass
