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
    SPAWN_RATE_MILLISECONDS, GAME_DURATION_SECONDS, PLAYER_LIVES, MUSIC_VOLUME, SFX_VOLUME
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
        self.font_small = pygame.font.SysFont("Arial", 24, bold=True)
        
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

        self.highscore_file = "highscore.txt"
        self.high_score = self.load_high_score()
        
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

        # --- AUDIO INITIALIZATION ---
        pygame.mixer.init()
        
        # 1. Cargar y configurar Efectos de Sonido (SFX)
        self.snd_splat = pygame.mixer.Sound("assets/sounds/splat.wav")
        self.snd_damage = pygame.mixer.Sound("assets/sounds/damage.wav")
        self.snd_heal = pygame.mixer.Sound("assets/sounds/heal.wav")
        
        # Aplicar volumen independiente a los efectos
        self.snd_splat.set_volume(SFX_VOLUME)
        self.snd_damage.set_volume(SFX_VOLUME)
        self.snd_heal.set_volume(SFX_VOLUME)
        
        # 2. Cargar y configurar Música de Fondo
        # Usamos mixer.music porque hace streaming del archivo (consume menos RAM)
        pygame.mixer.music.load("assets/sounds/bg_music.wav")
        pygame.mixer.music.set_volume(MUSIC_VOLUME)
        # Reproducir en loop infinito (-1)
        pygame.mixer.music.play(-1)

        # --- CARGAR ASSET DE VIDA ---
        self.heart_image = None
        heart_path = os.path.join("assets", "images", "heart.png")
        try:
            loaded_heart = pygame.image.load(heart_path).convert_alpha()
            self.heart_image = pygame.transform.smoothscale(loaded_heart, (30, 30))
        except FileNotFoundError:
            print(f"[WARNING] Heart image not found at {heart_path}")


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
                    # Tecla M para mutear/desmutear la música
                    if event.key == pygame.K_m:
                        if pygame.mixer.music.get_busy():
                            if pygame.mixer.music.get_volume() > 0:
                                pygame.mixer.music.set_volume(0)
                            else:
                                pygame.mixer.music.set_volume(MUSIC_VOLUME)

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
            self.snd_splat.play()
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
            self.snd_damage.play()
            self.lives -= 1
            self.combo = 0
            self.multiplier = 1
            self.shake_intensity = 15
            
            if self.lives <= 0:
                self.state = "GAME_OVER"

                if self.score > self.high_score:
                    self.high_score = self.score
                    self.save_high_score()

        # --- 3. NUEVA: Player catches Golden Ladybug (Heal) ---
        # Detectamos si la mano toca a la mariquita dorada
        healing_hits = pygame.sprite.spritecollide(self.player, self.powerups, True)
        for hit in healing_hits:
            self.snd_heal.play()
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

                if self.score > self.high_score:
                    self.high_score = self.score
                    self.save_high_score()
            
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
            
            # --- TÍTULO Y RÉCORD (Cuarto superior de la pantalla) ---
            self.draw_text("AGRO-DEFENDER", self.font_large, COLOR_WHITE, WINDOW_WIDTH//2 + offset_x, WINDOW_HEIGHT//4 + offset_y, True)
            self.draw_text(f"RECORD: {self.high_score}", self.font_medium, (255, 215, 0), WINDOW_WIDTH//2 + offset_x, WINDOW_HEIGHT//4 + 70 + offset_y, True)
            
            # --- INSTRUCCIONES DE JUEGO (Centro de la pantalla) ---
            self.draw_text("CÓMO JUGAR:", self.font_medium, (200, 200, 255), WINDOW_WIDTH//2 + offset_x, WINDOW_HEIGHT//2 + offset_y, True)
            self.draw_text("- Mueve tu mano frente a la cámara para controlar el escudo", self.font_small, COLOR_WHITE, WINDOW_WIDTH//2 + offset_x, WINDOW_HEIGHT//2 + 50 + offset_y, True)
            self.draw_text("- Aplasta las plagas antes de que toquen la planta", self.font_small, COLOR_WHITE, WINDOW_WIDTH//2 + offset_x, WINDOW_HEIGHT//2 + 90 + offset_y, True)
            self.draw_text("- Atrapa la mariquita dorada para recuperar vidas", self.font_small, (255, 215, 0), WINDOW_WIDTH//2 + offset_x, WINDOW_HEIGHT//2 + 130 + offset_y, True)
            
            # --- BOTÓN DE INICIO (Anclado cerca de la parte inferior) ---
            self.draw_text("Press SPACE to Start", self.font_medium, (50, 255, 100), WINDOW_WIDTH//2 + offset_x, WINDOW_HEIGHT - 120 + offset_y, True)
            
            # --- CRÉDITOS DEL EQUIPO (Pegado al borde inferior) ---
            credits_text = "Desarrollado por: Erick Olivo"
            self.draw_text(credits_text, self.font_small, (150, 150, 150), WINDOW_WIDTH//2 + offset_x, WINDOW_HEIGHT - 40 + offset_y, True)
            
        elif self.state == "PLAYING":
            # Para que los sprites también vibren, podemos dibujarlos en una superficie temporal 
            # o simplemente desplazar sus posiciones de dibujo. 
            # Por simplicidad, los dibujaremos normalmente, el fondo vibrando ya da el 80% del efecto.
            self.all_sprites.draw(self.screen)
            
            # HUD (Heads Up Display)
            current_time = pygame.time.get_ticks()
            time_left = max(0, GAME_DURATION_SECONDS - ((current_time - self.start_time) // 1000))
            
            self.draw_text(f"Score: {self.score}", self.font_medium, COLOR_WHITE, 20, 20)

            # HUD (Heads Up Display)
            self.draw_text(f"Score: {self.score}", self.font_medium, COLOR_WHITE, 20, 20)
            
            # --- DIBUJAR CORAZONES EN LUGAR DE TEXTO ---
            if self.heart_image:
                for i in range(self.lives):
                    # Los dibuja uno al lado del otro con un espacio de 35 píxeles
                    self.screen.blit(self.heart_image, (20 + (i * 35), 65))
            else:
                # Fallback por si la imagen no carga
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
            self.draw_text(f"RECORD: {self.high_score}", self.font_medium, (255, 215, 0), WINDOW_WIDTH//2, WINDOW_HEIGHT//2 - 90, True)
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

    def load_high_score(self):
        """Lee el récord desde un archivo local."""
        try:
            with open(self.highscore_file, "r") as f:
                return int(f.read())
        except (FileNotFoundError, ValueError):
            # Si el archivo no existe o está vacío, el récord es 0
            return 0

    def save_high_score(self):
        """Guarda el récord actual en un archivo local."""
        with open(self.highscore_file, "w") as f:
            f.write(str(self.high_score))
