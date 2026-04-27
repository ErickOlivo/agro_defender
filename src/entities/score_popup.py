import pygame

class ScorePopup(pygame.sprite.Sprite):
    """
    A temporary floating text effect that appears when a pest is crushed.
    """
    def __init__(self, x: int, y: int, text: str = "+10"):
        super().__init__()
        font = pygame.font.SysFont("Arial", 28, bold=True)
        # White text with a small black shadow effect could be added later
        self.image = font.render(text, True, (255, 255, 255))
        self.rect = self.image.get_rect(center=(x, y))
        self.alpha = 255
        self.vertical_speed = -2  # Moves upwards

    def update(self):
        """Moves the text up and fades it out."""
        self.rect.y += self.vertical_speed
        self.alpha -= 8  # Transparency decrease
        
        if self.alpha <= 0:
            self.kill()
        else:
            self.image.set_alpha(self.alpha)
