import pygame

class HoverButton:
    def __init__(self, x, y, width, height, text, font):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.hover_start_time = 0
        self.is_hovering = False
        self.fill_duration = 1500  # 1.5 segundos en milisegundos
        self.progress = 0.0        # Va de 0.0 a 1.0

    def update(self, cursor_rect):
        """Retorna True si el botón se llenó por completo."""
        if self.rect.colliderect(cursor_rect):
            if not self.is_hovering:
                self.is_hovering = True
                self.hover_start_time = pygame.time.get_ticks()
            else:
                elapsed = pygame.time.get_ticks() - self.hover_start_time
                self.progress = min(1.0, elapsed / self.fill_duration)
                
                if self.progress >= 1.0:
                    self.reset() # Lo reiniciamos para futuros usos
                    return True  # ¡Acción completada!
        else:
            self.reset()
            
        return False

    def reset(self):
        self.is_hovering = False
        self.progress = 0.0

    def draw(self, surface):
        # 1. Fondo oscuro del botón
        pygame.draw.rect(surface, (40, 40, 40), self.rect, border_radius=15)
        
        # 2. Barra de progreso verde que se va llenando de izquierda a derecha
        if self.progress > 0:
            fill_rect = pygame.Rect(self.rect.x, self.rect.y, int(self.rect.width * self.progress), self.rect.height)
            pygame.draw.rect(surface, (50, 205, 50), fill_rect, border_radius=15)
            
        # 3. Borde blanco brillante
        pygame.draw.rect(surface, (255, 255, 255), self.rect, 3, border_radius=15)
        
        # 4. Texto centrado
        text_surf = self.font.render(self.text, True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
