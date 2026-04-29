import pygame
import os

class Impact(pygame.sprite.Sprite):
    """
    A temporary visual effect (splat) that fades out and 
    destroys itself after a short duration.
    """
    def __init__(self, center_x: int, center_y: int):
        super().__init__()
        
        image_path = os.path.join("assets", "images", "impact.png")
        try:
            original_image = pygame.image.load(image_path).convert_alpha()
            
            # Escalado proporcional corregido
            orig_w, orig_h = original_image.get_size()
            target_w = 80
            target_h = int(orig_h * (target_w / orig_w)) # Definimos target_h
            
            # Usamos target_h aquí también
            self.image = pygame.transform.smoothscale(original_image, (target_w, target_h))
            
        except FileNotFoundError:
            self.image = pygame.Surface((1, 1))
            self.image.set_alpha(0)
            
        self.rect = self.image.get_rect()
        self.rect.center = (center_x, center_y)
        
        self.alpha = 255  
        self.fade_speed = 8  

    def update(self):
        self.alpha -= self.fade_speed
        if self.alpha <= 0:
            self.kill() 
        else:
            self.image.set_alpha(self.alpha)
