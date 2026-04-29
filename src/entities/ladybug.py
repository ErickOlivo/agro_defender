import pygame 
import random   
import os
from src.config import WINDOW_WIDTH, WINDOW_HEIGHT

class GoldenLadybug(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        
        # 1. Cargar y escalar proporcionalmente la lista de frames
        self.frames = []
        for i in range(3):
            try:
                img = pygame.image.load(f"assets/images/ladybug_{i}.png").convert_alpha()
                
                # --- ESCALADO PROPORCIONAL ---
                original_width, original_height = img.get_size()
                target_width = 85 # Ajusta este valor si la quieres más grande/pequeña
                target_height = int(original_height * (target_width / original_width))
                
                img = pygame.transform.smoothscale(img, (target_width, target_height))
                self.frames.append(img)
            except FileNotFoundError:
                img = pygame.Surface((45, 45))
                img.fill((255, 215, 0))
                self.frames.append(img)
                
        self.current_frame = 0
        
        # 2. Lógica de dirección y ROTACIÓN
        self.side = random.choice(["left", "right"])
        if self.side == "left":
            # Aparece en la izquierda, se mueve a la DERECHA
            self.speed_x = random.randint(3, 6)
            # Como la imagen original mira hacia ARRIBA, rotamos -90 grados para que mire a la derecha
            self.frames = [pygame.transform.rotate(f, -90) for f in self.frames]
            
            # Asignamos la imagen y rectángulo DESPUÉS de rotar
            self.image = self.frames[self.current_frame]
            self.rect = self.image.get_rect()
            self.rect.x = -self.rect.width
            
        else:
            # Aparece en la derecha, se mueve a la IZQUIERDA
            self.speed_x = random.randint(-6, -3)
            # Rotamos 90 grados para que mire a la izquierda
            self.frames = [pygame.transform.rotate(f, 90) for f in self.frames]
            
            # Asignamos la imagen y rectángulo DESPUÉS de rotar
            self.image = self.frames[self.current_frame]
            self.rect = self.image.get_rect()
            self.rect.x = WINDOW_WIDTH
            
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
