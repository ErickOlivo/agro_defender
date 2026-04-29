import pygame
import random
import os
from src.config import WINDOW_WIDTH, ENEMY_SPEED_MIN, ENEMY_SPEED_MAX

class Enemy(pygame.sprite.Sprite):
    """
    Represents a falling pest with frame-by-frame animation.
    """
    def __init__(self):
        super().__init__()
        
        # 1. Cargar y procesar la lista de frames
        self.frames = []
        for i in range(3):
            try:
                # Cargamos enemy_0, enemy_1, enemy_2
                img = pygame.image.load(os.path.join("assets", "images", f"enemy_{i}.png")).convert_alpha()
                
                # --- ESCALADO PROPORCIONAL (Mantenemos tamaño 80) ---
                original_width, original_height = img.get_size()
                target_width = 80  
                target_height = int(original_height * (target_width / original_width))
                
                img = pygame.transform.smoothscale(img, (target_width, target_height))
                
                # --- ROTAR 180 GRADOS (Para que caigan mirando hacia abajo) ---
                img = pygame.transform.rotate(img, 180)
                
                self.frames.append(img)
            except FileNotFoundError:
                # Fallback por si falta alguna imagen
                img = pygame.Surface((80, 80))
                img.fill((220, 20, 60))
                self.frames.append(img)
                
        # 2. Configurar animación
        self.current_frame = 0
        # Damos una velocidad de animación ligeramente aleatoria para que no todos muevan las patas al mismo tiempo
        self.animation_speed = random.uniform(0.15, 0.25) 
        
        self.image = self.frames[self.current_frame]
        self.rect = self.image.get_rect()
        
        # MÁSCARA PARA COLISIONES PERFECTAS
        self.mask = pygame.mask.from_surface(self.image)
        
        # 3. Posición inicial y velocidad de caída
        self.rect.x = random.randint(0, WINDOW_WIDTH - self.rect.width)
        self.rect.y = -self.rect.height
        
        self.speed = random.randint(ENEMY_SPEED_MIN, ENEMY_SPEED_MAX)

    def update(self):
        # Mover hacia abajo
        self.rect.y += self.speed
        
        # Animar
        self.current_frame += self.animation_speed
        if self.current_frame >= len(self.frames):
            self.current_frame = 0
            
        # Actualizar la imagen actual según el frame
        self.image = self.frames[int(self.current_frame)]
        
        # Actualizar la máscara en cada frame para que las colisiones 
        # sean exactas incluso cuando mueven las patas
        self.mask = pygame.mask.from_surface(self.image)
