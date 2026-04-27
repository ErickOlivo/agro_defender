import os
import random
import pygame
from src.entities.impact import Impact
from src.entities.enemy import Enemy
from src.entities.ladybug import GoldenLadybug
from src.entities.score_popup import ScorePopup
import sys
from src.config import (
    WINDOW_WIDTH, WINDOW_HEIGHT, FPS, COLOR_BLACK, COLOR_WHITE, 
    SPAWN_RATE_MILLISECONDS, GAME_DURATION_SECONDS, PLAYER_LIVES
)
from src.entities.player import Player
from src.entities.enemy import Enemy
from src.entities.plant import Plant
from src.vision_worker import VisionWorker

class GameBroker:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Agro-Defender: Mission Rescue")
        self.clock = pygame.time.Clock()
        self.running = True
        
        # UI Fonts
        self.font_large = pygame.font.SysFont("Arial", 64, bold=True)
        self.font_medium = pygame.font.SysFont("Arial", 36, bold=True)
        
        # ==========================================
        # NEW: Background Loading Logic
        # ==========================================
        self.bg_image = None
        bg_path = os.path.join("assets", "images", "background.png")
        try:
            # .convert() optimizes the image for faster blitting to the screen
            loaded_bg = pygame.image.load(bg_path).convert()
            self.bg_image = pygame.transform.smoothscale(loaded_bg, (WINDOW_WIDTH, WINDOW_HEIGHT))
        except FileNotFoundError:
            print(f"[WARNING] Background image not found at {bg_path}")
            
        # Game State Variables
        self.state = "START"  # States: START, PLAYING, GAME_OVER
        self.score = 0
        self.lives = PLAYER_LIVES
        self.combo = 0
        self.multiplier = 1
        self.shake_intensity = 0
        self.start_time = 0
        self.last_spawn_time = 0
        
        # Initialize Entities
        self.player = Player()
        self.plant = Plant()
        
        # Sprite Groups
        self.all_sprites = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.powerups = pygame.sprite.Group()
        
        self.all_sprites.add(self.plant)
        self.all_sprites.add(self.player)
        
        # Vision Worker
        self.vision_worker = VisionWorker()


    def reset_game(self):
        """Resets variables for a new game."""
        self.score = 0
        self.lives = PLAYER_LIVES

        self.combo = 0
        self.multiplier = 1
        
        for enemy in self.enemies:
            enemy.kill()
        for p in self.powerups:
            p.kill()
        self.start_time = pygame.time.get_ticks()
        self.state = "PLAYING"

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            # Spacebar to start or restart the game
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if self.state in ["START", "GAME_OVER"]:
                        self.reset_game()

    def spawn_enemy(self, current_time):
        """Spawns a new enemy based on the spawn rate."""
        if current_time - self.last_spawn_time > SPAWN_RATE_MILLISECONDS:
            new_enemy = Enemy()
            self.enemies.add(new_enemy)
            self.all_sprites.add(new_enemy)
            self.last_spawn_time = current_time

    def check_collisions(self):
        """Handles logic when objects overlap."""
        # 1. Player hits Enemy (Crush pest)
        hits = pygame.sprite.spritecollide(self.player, self.enemies, True)
        for hit in hits:
            # --- COMBO LOGIC ---
            self.combo += 1
            self.multiplier = 1 + (self.combo // 5)
            
            points_to_add = 10 * self.multiplier
            self.score += points_to_add
            
            # Visual Feedback
            splat = Impact(hit.rect.centerx, hit.rect.centery)
            popup = ScorePopup(hit.rect.centerx, hit.rect.centery, text=f"+{points_to_add}")
            
            self.all_sprites.add(splat)
            self.all_sprites.add(popup)
            
        # 2. Enemy hits Plant (Damage)
        plant_hits = pygame.sprite.spritecollide(self.plant, self.enemies, True)
        for hit in plant_hits:
            self.lives -= 1
            self.combo = 0
            self.multiplier = 1
            self.shake_intensity = 15
            
            if self.lives <= 0:
                self.state = "GAME_OVER"

        # --- 3. NUEVA: Player catches Golden Ladybug (Heal) ---
        # Detectamos si la mano toca a la mariquita dorada
        healing_hits = pygame.sprite.spritecollide(self.player, self.powerups, True)
        for hit in healing_hits:
            self.lives += 1  # Incrementamos vida
            
            # Feedback visual: Texto flotante indicando la curación
            popup = ScorePopup(hit.rect.centerx, hit.rect.centery, text="LIFE +1")
            # Opcional: Un pequeño shake suave y positivo
            self.shake_intensity = 5 
            
            self.all_sprites.add(popup)

        # 4. Enemy falls off screen (Cleanup)
        for enemy in self.enemies:
            if enemy.rect.top > WINDOW_HEIGHT:
                enemy.kill()
                
    def update_state(self):
        """Updates physics, positions, and game logic."""
        # Always update player position via webcam thread
        self.player.set_position(self.vision_worker.hand_x, self.vision_worker.hand_y)
        
        if self.state == "PLAYING":
            current_time = pygame.time.get_ticks()
            elapsed_seconds = (current_time - self.start_time) // 1000
            remaining_time = max(0, GAME_DURATION_SECONDS - elapsed_seconds)
            
            if remaining_time == 0:
                self.state = "GAME_OVER"
            
            # Progressive Difficulty: Faster spawns as time runs out
            dynamic_spawn_rate = max(200, int(SPAWN_RATE_MILLISECONDS * (remaining_time / GAME_DURATION_SECONDS)))
            
            if current_time - self.last_spawn_time > dynamic_spawn_rate:
                new_enemy = Enemy()
                self.enemies.add(new_enemy)
                self.all_sprites.add(new_enemy)
                self.last_spawn_time = current_time
            # --- SPAWN DE LADYBUG (RRECUPEACIÓN DE VIDA) ---
            # Un 0.3% de probabilidad por frame (Aprox. una cada 5-6 segundos)
            if random.random() < 0.003:
                # Solo permitimos una mariquita en pantalla a la vez para que sea valiosa
                if len(self.powerups) == 0:
                    lady = GoldenLadybug()
                    self.powerups.add(lady)
                    self.all_sprites.add(lady)

            self.all_sprites.update()
            self.check_collisions()

    def draw_text(self, text, font, color, x, y, center=False):
        """Helper method to draw text on screen."""
        surface = font.render(text, True, color)
        rect = surface.get_rect()
        if center:
            rect.center = (x, y)
        else:
            rect.topleft = (x, y)
        self.screen.blit(surface, rect)

    def render(self):
        # --- 1. LÓGICA DE CÁLCULO DEL SHAKE ---
        offset_x = 0
        offset_y = 0
        
        if self.shake_intensity > 0:
            # Generamos un movimiento aleatorio basado en la intensidad actual
            offset_x = random.randint(-self.shake_intensity, self.shake_intensity)
            offset_y = random.randint(-self.shake_intensity, self.shake_intensity)
            # Reducimos la intensidad para que la sacudida se detenga gradualmente
            self.shake_intensity -= 1 

        # --- 2. DIBUJAR EL FONDO (Con el offset aplicado) ---
        if self.bg_image:
            # Ahora el fondo no siempre se dibuja en (0,0), sino que "vibra"
            self.screen.blit(self.bg_image, (offset_x, offset_y))
        else:
            self.screen.fill(COLOR_BLACK)
        
        # --- 3. DIBUJAR ESTADOS ---
        if self.state == "START":
            self.player.update() 
            # También aplicamos el offset a la mano en el inicio para coherencia visual
            temp_rect = self.player.rect.copy()
            temp_rect.x += offset_x
            temp_rect.y += offset_y
            self.screen.blit(self.player.image, temp_rect)
            
            self.draw_text("AGRO-DEFENDER", self.font_large, COLOR_WHITE, WINDOW_WIDTH//2 + offset_x, WINDOW_HEIGHT//2 - 50 + offset_y, True)
            self.draw_text("Press SPACE to Start", self.font_medium, COLOR_WHITE, WINDOW_WIDTH//2 + offset_x, WINDOW_HEIGHT//2 + 50 + offset_y, True)
            
        elif self.state == "PLAYING":
            # Para que los sprites también vibren, podemos dibujarlos en una superficie temporal 
            # o simplemente desplazar sus posiciones de dibujo. 
            # Por simplicidad, los dibujaremos normalmente, el fondo vibrando ya da el 80% del efecto.
            self.all_sprites.draw(self.screen)
            
            # HUD (Heads Up Display)
            current_time = pygame.time.get_ticks()
            time_left = max(0, GAME_DURATION_SECONDS - ((current_time - self.start_time) // 1000))
            
            self.draw_text(f"Score: {self.score}", self.font_medium, COLOR_WHITE, 20, 20)
            self.draw_text(f"Lives: {self.lives}", self.font_medium, COLOR_WHITE, 20, 60)

            if self.combo > 0:
                combo_color = (255, 215, 0) if self.multiplier > 1 else COLOR_WHITE
                self.draw_text(f"Combo: {self.combo} (x{self.multiplier})", 
                               self.font_medium, combo_color, 20, 100)
            
            self.draw_text(f"Time: {time_left}s", self.font_medium, COLOR_WHITE, WINDOW_WIDTH - 200, 20)
            
        elif self.state == "GAME_OVER":
            self.player.update() 
            self.screen.blit(self.player.image, self.player.rect)
            self.draw_text("GAME OVER", self.font_large, COLOR_WHITE, WINDOW_WIDTH//2, WINDOW_HEIGHT//2 - 50, True)
            self.draw_text(f"Final Score: {self.score}", self.font_medium, COLOR_WHITE, WINDOW_WIDTH//2, WINDOW_HEIGHT//2 + 20, True)
            self.draw_text("Press SPACE to Restart", self.font_medium, COLOR_WHITE, WINDOW_WIDTH//2, WINDOW_HEIGHT//2 + 80, True)

        pygame.display.flip()

   
    def run(self):
        print("[INFO] Starting Vision Worker Thread...")
        self.vision_worker.start()
        
        while self.running:
            self.handle_events()
            self.update_state()
            self.render()
            self.clock.tick(FPS)
            
        print("[INFO] Shutting down...")
        self.vision_worker.stop()
        pygame.quit()
        sys.exit()
