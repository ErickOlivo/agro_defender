import pygame
import random
import os
import math
from src.config import WINDOW_WIDTH, ENEMY_SPEED_MIN

class Grasshopper(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.frames = []
        for i in range(3):
            try:
                img = pygame.image.load(os.path.join("assets", "images", f"grasshopper_{i}.png")).convert_alpha()
                original_width, original_height = img.get_size()
                target_width = 85 # Un poco más grande que el bicho normal
                target_height = int(original_height * (target_width / original_width))
                img = pygame.transform.smoothscale(img, (target_width, target_height))
                img = pygame.transform.rotate(img, 180)
                self.frames.append(img)
            except FileNotFoundError:
                img = pygame.Surface((80, 80))
                img.fill((50, 205, 50)) # Verde lima
                self.frames.append(img)

        self.current_frame = 0
        self.animation_speed = 0.15
        self.image = self.frames[self.current_frame]
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)

        # Lógica de movimiento
        self.rect.x = random.randint(100, WINDOW_WIDTH - 100)
        self.rect.y = -self.rect.height
        
        self.speed_y = random.uniform(1.5, 2.5)
        self.amplitude = random.randint(50, 100) # Qué tan ancho es el zigzag
        self.frequency = random.uniform(0.01, 0.025) # Qué tan rápido oscila
        self.spawn_time = random.uniform(0, 100) # Desfase para que no todos zigzagueen igual

    def update(self, is_frozen=False):
        if is_frozen:
            return # Si está congelado, no se mueve ni anima

        # Movimiento en ZigZag usando Seno
        self.rect.y += self.speed_y
        self.rect.x += math.sin(self.rect.y * self.frequency + self.spawn_time) * (self.amplitude * self.frequency)

        # Mantener dentro de la pantalla
        if self.rect.left < 0: self.rect.left = 0
        if self.rect.right > WINDOW_WIDTH: self.rect.right = WINDOW_WIDTH

        # Animación
        self.current_frame += self.animation_speed
        if self.current_frame >= len(self.frames):
            self.current_frame = 0
        self.image = self.frames[int(self.current_frame)]
        self.mask = pygame.mask.from_surface(self.image)
