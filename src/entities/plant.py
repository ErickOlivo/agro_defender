import pygame
from src.config import WINDOW_WIDTH, WINDOW_HEIGHT, COLOR_PLANT_GREEN

class Plant(pygame.sprite.Sprite):
    """
    Represents the Mother Plant to be defended at the bottom of the screen.
    """
    def __init__(self):
        super().__init__()
        # Placeholder for the plant (a green wide rectangle)
        self.image = pygame.Surface((200, 80))
        self.image.fill(COLOR_PLANT_GREEN)
        
        self.rect = self.image.get_rect()
        # Position it at the bottom center
        self.rect.centerx = WINDOW_WIDTH // 2
        self.rect.bottom = WINDOW_HEIGHT
        
    def update(self):
        """Static object, no movement needed."""
        pass
