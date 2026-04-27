import pygame
import os

class Player(pygame.sprite.Sprite):
    """
    Represents the player's hand/shield in the game using a loaded sprite.
    """
    def __init__(self):
        super().__init__()
        
        # Load the player sprite image
        image_path = os.path.join("assets", "images", "player.png")
        try:
            original_image = pygame.image.load(image_path).convert_alpha()
            # Scale it down to a good cursor size (e.g., 80x80 pixels)
            self.image = pygame.transform.smoothscale(original_image, (80, 80))
        except FileNotFoundError:
            print(f"[WARNING] Could not find {image_path}. Using fallback shape.")
            self.image = pygame.Surface((50, 50), pygame.SRCALPHA)
            pygame.draw.circle(self.image, (65, 105, 225), (25, 25), 25)
            
        self.rect = self.image.get_rect()
        self.rect.center = (0, 0)

    def set_position(self, x: int, y: int):
        self.rect.center = (x, y)

    def update(self):
        pass
