import pygame
from src.config import COLOR_CURSOR_BLUE

class Player(pygame.sprite.Sprite):
    """
    Represents the player's hand/shield in the game.
    Inherits from pygame.sprite.Sprite for efficient rendering and collision.
    """
    def __init__(self):
        super().__init__()
        # Create a transparent surface for the shield
        self.image = pygame.Surface((50, 50), pygame.SRCALPHA)
        
        # Draw a simple blue circle as a placeholder for the hand cursor
        pygame.draw.circle(self.image, COLOR_CURSOR_BLUE, (25, 25), 25)
        
        self.rect = self.image.get_rect()
        self.rect.center = (0, 0)

    def set_position(self, x: int, y: int):
        """
        Updates the player's coordinates.
        Called directly by the broker when receiving tracking data.
        """
        self.rect.center = (x, y)

    def update(self):
        """
        Standard Pygame method called by sprite groups.
        Required to avoid argument mismatch errors.
        """
        pass
