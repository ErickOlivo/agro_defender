import pygame
import os

class Plant(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        
        image_path = os.path.join("assets", "images", "plant.png")
        try:
            original_image = pygame.image.load(image_path).convert_alpha()
            
            original_width, original_height = original_image.get_size()
            
            # 1. AUMENTAR TAMAÑO (De 100 a 160 o el valor que prefieras)
            target_width = 160 
            target_height = int(original_height * (target_width / original_width))
            
            self.image = pygame.transform.smoothscale(original_image, (target_width, target_height))
            
        except FileNotFoundError:
            self.image = pygame.Surface((160, 240))
            self.image.fill((34, 139, 34))
            
        self.rect = self.image.get_rect()
        
        # 2. CREAR MÁSCARA DE COLISIÓN PERFECTA (Ignora la transparencia)
        self.mask = pygame.mask.from_surface(self.image)
        
        self.rect.centerx = x
        self.rect.bottom = y
        
    def update(self):
        pass
