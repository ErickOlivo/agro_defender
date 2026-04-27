import pygame 
import random   
import os
from src.config import WINDOW_WIDTH, WINDOW_HEIGHT

class GoldenLadybug(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        
        # 1. Cargar lista de frames para animar
        self.frames = []
        for i in range(3):
            img = pygame.image.load(f"assets/images/ladybug_{i}.png").convert_alpha()
            img = pygame.transform.smoothscale(img, (50, 50))
            self.frames.append(img)
            
        self.current_frame = 0
        self.image = self.frames[self.current_frame]
        self.rect = self.image.get_rect()
        
        # 2. Lógica de dirección
        self.side = random.choice(["left", "right"])
        if self.side == "left":
            self.rect.x = -self.rect.width
            self.speed_x = random.randint(3, 6)
            # Mira a la derecha (normal)
        else:
            self.rect.x = WINDOW_WIDTH
            self.speed_x = random.randint(-6, -3)
            # VOLTEAR IMAGEN para que mire a la izquierda
            self.frames = [pygame.transform.flip(f, True, False) for f in self.frames]
            
        self.rect.y = random.randint(50, WINDOW_HEIGHT // 2)
        self.animation_speed = 0.2 # Controla qué tan rápido "aletea"

    def update(self):
        # Mover
        self.rect.x += self.speed_x
        
        # Animar
        self.current_frame += self.animation_speed
        if self.current_frame >= len(self.frames):
            self.current_frame = 0
        self.image = self.frames[int(self.current_frame)]
        
        # Cleanup
        if self.rect.right < -50 or self.rect.left > WINDOW_WIDTH + 50:
            self.kill()
