import pygame
import os
from src.config import WINDOW_WIDTH, WINDOW_HEIGHT

class Player(pygame.sprite.Sprite):
    """
    Represents the player hand/cursor. Coordinates come from CV Worker.
    """
    def __init__(self):
        super().__init__()
        
        # Load the player hand sprite image
        image_path = os.path.join("assets", "images", "player.png")
        try:
            original_image = pygame.image.load(image_path).convert_alpha()
            
            # --- ESCALADO PROPORCIONAL (Evita que se vea achatada) ---
            original_width, original_height = original_image.get_size()
            
            # Definimos un ancho fijo (puedes subirlo a 90 o 100 si la quieres más grande)
            target_width = 80 
            
            # Calculamos la altura para mantener la proporción matemática
            target_height = int(original_height * (target_width / original_width))
            
            self.image = pygame.transform.smoothscale(original_image, (target_width, target_height))
            
        except FileNotFoundError:
            # Fallback en caso de error
            self.image = pygame.Surface((70, 70))
            self.image.fill((0, 191, 255)) # Deep Sky Blue
            
        self.rect = self.image.get_rect()
        # Inicializar fuera de pantalla
        self.rect.x = -self.rect.width
        self.rect.y = -self.rect.height

    def set_position(self, x, y):
        """
        Updates the player's position based on coordinates 
        received from the Computer Vision Worker.
        """
        self.rect.centerx = x
        self.rect.centery = y

    def update(self):
        """
        Required by Pygame Sprite Groups. 
        In this case, position is handled explicitly by set_position.
        """
        pass
