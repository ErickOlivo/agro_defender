import pygame
import random
import os
from src.config import WINDOW_WIDTH, ENEMY_SPEED_MIN, ENEMY_SPEED_MAX

class Enemy(pygame.sprite.Sprite):
    """
    Represents a pest/enemy falling from the top using a loaded sprite.
    """
    def __init__(self):
        super().__init__()
        
        # Load the enemy sprite image
        image_path = os.path.join("assets", "images", "enemy.png")
        try:
            original_image = pygame.image.load(image_path).convert_alpha()
            # Scale it to a bug size (e.g., 60x60 pixels)
            self.image = pygame.transform.smoothscale(original_image, (60, 60))
        except FileNotFoundError:
            self.image = pygame.Surface((40, 40))
            self.image.fill((220, 20, 60))
            
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, WINDOW_WIDTH - self.rect.width)
        self.rect.y = -self.rect.height
        
        self.speed = random.randint(ENEMY_SPEED_MIN, ENEMY_SPEED_MAX)

    def update(self):
        self.rect.y += self.speed
