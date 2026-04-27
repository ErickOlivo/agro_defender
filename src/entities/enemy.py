import pygame
import random
from src.config import WINDOW_WIDTH, ENEMY_SPEED_MIN, ENEMY_SPEED_MAX, COLOR_ENEMY_RED

class Enemy(pygame.sprite.Sprite):
    """
    Represents a pest/enemy falling from the top of the screen.
    """
    def __init__(self):
        super().__init__()
        # Placeholder for the enemy sprite (a red square for now)
        self.image = pygame.Surface((40, 40))
        self.image.fill(COLOR_ENEMY_RED)
        
        self.rect = self.image.get_rect()
        
        # Spawn at a random horizontal position, just above the screen
        self.rect.x = random.randint(0, WINDOW_WIDTH - self.rect.width)
        self.rect.y = -self.rect.height
        
        # Assign a random falling speed
        self.speed = random.randint(ENEMY_SPEED_MIN, ENEMY_SPEED_MAX)

    def update(self):
        """Moves the enemy downwards. Called automatically by the sprite group."""
        self.rect.y += self.speed
