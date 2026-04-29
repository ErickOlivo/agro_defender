import pygame
import os
import random
from src.config import WINDOW_WIDTH, WINDOW_HEIGHT

class FreezePowerUp(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        
        image_path = os.path.join("assets", "images", "freeze_powerup.png")
        try:
            img = pygame.image.load(image_path).convert_alpha()
            # Tamaño similar a la Ladybug
            original_width, original_height = img.get_size()
            target_width = 60
            target_height = int(original_height * (target_width / original_width))
            self.image = pygame.transform.smoothscale(img, (target_width, target_height))
        except FileNotFoundError:
            self.image = pygame.Surface((40, 40))
            self.image.fill((173, 216, 230)) # Light Blue
            
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        
        self.rect.x = random.randint(50, WINDOW_WIDTH - 50)
        self.rect.y = -self.rect.height
        self.speed_y = 4

    def update(self):
        self.rect.y += self.speed_y
        if self.rect.top > WINDOW_HEIGHT:
            self.kill()
