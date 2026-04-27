import pygame
import os

class Impact(pygame.sprite.Sprite):
    """
    A temporary visual effect (splat) that appears when an enemy is crushed.
    Destroys itself after a short duration.
    """
    def __init__(self, center_x: int, center_y: int):
        super().__init__()
        
        image_path = os.path.join("assets", "images", "impact.png")
        try:
            original_image = pygame.image.load(image_path).convert_alpha()
            self.image = pygame.transform.smoothscale(original_image, (80, 80))
        except FileNotFoundError:
            # Fallback invisible box if no image
            self.image = pygame.Surface((1, 1))
            self.image.set_alpha(0)
            
        self.rect = self.image.get_rect()
        self.rect.center = (center_x, center_y)
        
        # How many frames the splat stays on screen (e.g., 30 frames = 0.5 seconds at 60 FPS)
        self.lifetime = 30 

    def update(self):
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.kill() # Remove itself from all sprite groups
