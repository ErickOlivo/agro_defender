import os
import random
import pygame
from src.entities.impact import Impact
from src.entities.enemy import Enemy
from src.entities.ladybug import GoldenLadybug
from src.entities.grasshopper import Grasshopper
from src.entities.freeze import FreezePowerUp
from src.entities.score_popup import ScorePopup
from src.ui.virtual_button import HoverButton
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

        # Sprite Groups
        self.all_sprites = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.powerups = pygame.sprite.Group()

        self.is_frozen = False
        self.freeze_duration = 3000
        self.freeze_start_time = 0
        
        # --- CREACIÓN DE LAS 3 PLANTAS ---
        self.plants = pygame.sprite.Group()
        self.effects = pygame.sprite.Group()

        # ==========================================
        # NEW: FEVER MODE SYSTEM  <--- AÑADE ESTO AQUÍ
        # ==========================================
        self.is_fever_mode = False
        self.fever_duration = 10000  # 5 segundos de frenesí
        self.fever_start_time = 0
        self.fever_threshold = 7    # Se activa a los 7 kills
        
        # Las distribuimos a lo ancho de la pantalla (25%, 50% y 75%)
        plant1 = Plant(WINDOW_WIDTH // 4, WINDOW_HEIGHT - 10)
        plant2 = Plant(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 10)
        plant3 = Plant(3 * WINDOW_WIDTH // 4, WINDOW_HEIGHT - 10)
        
        # Añadimos las 3 plantas a su propio grupo y al grupo general
        self.plants.add(plant1, plant2, plant3)
        self.all_sprites.add(plant1, plant2, plant3)
        

        

        self.all_sprites.add(self.player)
        
        # Vision Worker
        self.vision_worker = VisionWorker()

        # --- AUDIO INITIALIZATION ---
        pygame.mixer.init()
        
        # 1. Cargar y configurar Efectos de Sonido (SFX)
        self.snd_splat = pygame.mixer.Sound("assets/sounds/splat.wav")
        self.snd_damage = pygame.mixer.Sound("assets/sounds/damage.wav")
        self.snd_heal = pygame.mixer.Sound("assets/sounds/heal.wav")
        self.snd_freeze = pygame.mixer.Sound("assets/sounds/freeze.wav")
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
            
        # ==========================================
        # NEW: SISTEMA DE BOTONES VIRTUALES (HOVER)
        # ==========================================
        # Definimos el tamaño y centramos los botones en la parte inferior
        btn_w, btn_h = 300, 60
        btn_x = (WINDOW_WIDTH // 2) - (btn_w // 2)
        btn_y = WINDOW_HEIGHT - 120
        
        self.btn_start = HoverButton(btn_x, btn_y, btn_w, btn_h, "INICIAR JUEGO", self.font_medium)
        self.btn_resume = HoverButton(btn_x, btn_y, btn_w, btn_h, "REANUDAR", self.font_medium)
        self.btn_restart = HoverButton(btn_x, btn_y, btn_w, btn_h, "REINTENTAR", self.font_medium)
        
        # Temporizador para no perder tiempo de juego mientras está en pausa
        self.pause_start_time = 0

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
        hits = pygame.sprite.spritecollide(self.player, self.enemies, True, pygame.sprite.collide_mask)
        for hit in hits:
            # --- COMBO LOGIC ---
            self.snd_splat.play()
            self.combo += 1
            self.multiplier = 1 + (self.combo // 5)
            
            # --- NUEVO: FIEBRE LOGIC ---
            # Multiplicador x3 si estamos en modo fiebre
            fever_multiplier = 3 if self.is_fever_mode else 1
            points_to_add = 10 * self.multiplier * fever_multiplier
            self.score += points_to_add
            
            # ACTIVAR FIEBRE si llega a 7 kills seguidos (y no está ya activa)
            if self.combo >= self.fever_threshold and not self.is_fever_mode:
                self.activate_fever_mode()
            # ---------------------------
            
            # --- Visual Feedback ---
            splat = Impact(hit.rect.centerx, hit.rect.centery)
            popup = ScorePopup(hit.rect.centerx, hit.rect.centery, text=f"+{points_to_add}")
            
            self.effects.add(splat, popup)
            self.all_sprites.add(splat, popup)
            
        # 2. Enemy hits ANY Plant (Damage)
        plant_hits = pygame.sprite.groupcollide(self.plants, self.enemies, False, True, collided=pygame.sprite.collide_mask)
        
        for plant, enemies_that_hit in plant_hits.items():
            for hit in enemies_that_hit:
                # --- NUEVA LÓGICA DE PROTECCIÓN ---
                if self.is_fever_mode:
                    # Si estamos en fiebre, el bicho muere pero NO hay daño ni reset
                    self.snd_splat.play() 
                    # Opcional: añadir un splat visual aquí también
                    splat = Impact(hit.rect.centerx, hit.rect.centery)
                    self.effects.add(splat)
                    self.all_sprites.add(splat)
                else:
                    # Solo recibimos daño si NO estamos en fiebre
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

        # 3. Player catches Power-ups (Merge Ladybug and Freeze)
        powerup_hits = pygame.sprite.spritecollide(self.player, self.powerups, True, pygame.sprite.collide_mask)
        for p in powerup_hits:
            clase_powerup = p.__class__.__name__
            
            if clase_powerup == "GoldenLadybug":
                self.snd_heal.play()
                self.lives = min(3, self.lives + 1) 
                
                popup = ScorePopup(p.rect.centerx, p.rect.centery, text="LIFE +1")
                self.shake_intensity = 5 
                
                self.effects.add(popup)
                self.all_sprites.add(popup)
                
            elif clase_powerup == "FreezePowerUp":
                self.snd_freeze.play()
                self.is_frozen = True
                self.freeze_start_time = pygame.time.get_ticks()

        # 4. Enemy falls off screen (Cleanup)
        for enemy in self.enemies:
            if enemy.rect.top > WINDOW_HEIGHT:
                enemy.kill()
    def activate_fever_mode(self):
        """Activa el modo frenesí: Mano gigante y música acelerada."""
        self.is_fever_mode = True
        self.fever_start_time = pygame.time.get_ticks()
        
        # 1. AGRANDAR LA MANO (A 140px)
        orig_w, orig_h = self.player.image.get_size()
        target_w = 140  
        target_h = int(orig_h * (target_w / orig_w))
        self.player.image = pygame.transform.smoothscale(self.player.image, (target_w, target_h))
        # Mantenemos el centro en el mismo lugar para que no "salte" visualmente
        self.player.rect = self.player.image.get_rect(center=self.player.rect.center)
        self.player.mask = pygame.mask.from_surface(self.player.image)

        # 2. CAMBIAR MÚSICA (Con un try-except por si aún no tienes el archivo de audio)
        try:
            pygame.mixer.music.load(os.path.join("assets", "sounds", "bgm_fever.wav"))
            pygame.mixer.music.play(-1)
        except Exception:
            print("[DEBUG] No se encontró bgm_fever.wav, la música seguirá normal.")

    def deactivate_fever_mode(self):
        """Desactiva el modo frenesí y restaura los valores normales."""
        self.is_fever_mode = False
        self.combo = 0 
        
        # 1. RESTAURAR MANO (Volver a 80px)
        target_w = 80
        orig_w, orig_h = self.player.image.get_size()
        target_h = int(orig_h * (target_w / orig_w))
        self.player.image = pygame.transform.smoothscale(self.player.image, (target_w, target_h))
        self.player.rect = self.player.image.get_rect(center=self.player.rect.center)
        self.player.mask = pygame.mask.from_surface(self.player.image)

        # 2. RESTAURAR MÚSICA NORMAL (El archivo que pusiste en tu __init__)
        try:
            pygame.mixer.music.load(os.path.join("assets", "sounds", "bg_music.wav"))
            pygame.mixer.music.play(-1)
        except Exception:
            pass



            
    def update_state(self):
        """Updates physics, positions, and game logic."""
        # Always update player position via webcam thread
        self.player.set_position(self.vision_worker.hand_x, self.vision_worker.hand_y)
        
        # ==========================================
        # ESTADO: MENÚ DE INICIO
        # ==========================================
        if self.state == "START":
            # Si el botón se llena al 100%, iniciamos el juego
            if self.btn_start.update(self.player.rect):
                self.state = "PLAYING"
                self.start_time = pygame.time.get_ticks()
                self.last_spawn_time = self.start_time
                self.score = 0
                self.lives = 3
                self.combo = 0
                
        # ==========================================
        # ESTADO: JUEGO EN PAUSA
        # ==========================================
        elif self.state == "PAUSED":
            # Si el botón se llena al 100%, reanudamos
            if self.btn_resume.update(self.player.rect):
                self.state = "PLAYING"
                
                # Compensamos el tiempo que estuvimos en pausa para no perder segundos
                pause_duration = pygame.time.get_ticks() - self.pause_start_time
                self.start_time += pause_duration
                self.last_spawn_time += pause_duration
                
                if getattr(self, 'is_frozen', False): 
                    self.freeze_start_time += pause_duration
                if getattr(self, 'is_fever_mode', False): 
                    self.fever_start_time += pause_duration

        # ==========================================
        # ESTADO: JUGANDO
        # ==========================================
        elif self.state == "PLAYING":
            # --- DETECCIÓN DE GESTO: PUÑO PARA PAUSAR ---
            if self.vision_worker.is_fist:
                self.state = "PAUSED"
                self.pause_start_time = pygame.time.get_ticks()
                return # Salimos del update para congelar la lógica de inmediato
            
            current_time = pygame.time.get_ticks()

            # --- 1. LÓGICA DE TEMPORIZADOR DE CONGELACIÓN Y FIEBRE ---
            if self.is_frozen:
                if current_time - self.freeze_start_time > self.freeze_duration:
                    self.is_frozen = False
                    
            if getattr(self, 'is_fever_mode', False):
                if current_time - self.fever_start_time > self.fever_duration:
                    self.deactivate_fever_mode()

            # --- 2. ACTUALIZACIÓN DE MOVIMIENTOS ---
            self.enemies.update(self.is_frozen) 
            self.powerups.update() 
            self.player.update()
            self.effects.update()

            # --- 3. LÓGICA DE TIEMPO DE JUEGO ---
            elapsed_seconds = (current_time - self.start_time) // 1000
            remaining_time = max(0, GAME_DURATION_SECONDS - elapsed_seconds)
            
            if remaining_time == 0:
                self.state = "GAME_OVER"
                if self.score > self.high_score:
                    self.high_score = self.score
                    self.save_high_score()
            
            # --- 4. SPAWN DE ENEMIGOS (Solo si no está congelado) ---
            if not self.is_frozen:
                # Enemigo Normal
                dynamic_spawn_rate = max(200, int(SPAWN_RATE_MILLISECONDS * (remaining_time / GAME_DURATION_SECONDS)))
                if current_time - self.last_spawn_time > dynamic_spawn_rate:
                    new_enemy = Enemy()
                    self.enemies.add(new_enemy)
                    self.all_sprites.add(new_enemy)
                    self.last_spawn_time = current_time

                # Saltamontes (Grasshopper)
                if random.random() < 0.02:
                    new_grasshopper = Grasshopper()
                    self.enemies.add(new_grasshopper)
                    self.all_sprites.add(new_grasshopper)

            # --- 5. SPAWN DE POWER-UPS ---
            # Ladybug
            if random.random() < 0.003:
                if len(self.powerups) == 0:
                    lady = GoldenLadybug()
                    self.powerups.add(lady)
                    self.all_sprites.add(lady)

            # Cristal de Hielo (Freeze) - Ajustado a 0.003
            if random.random() < 0.003:
                new_freeze = FreezePowerUp()
                self.powerups.add(new_freeze)
                self.all_sprites.add(new_freeze)

            # --- 6. COLISIONES ---
            self.check_collisions()

        # ==========================================
        # ESTADO: GAME OVER
        # ==========================================
        elif self.state == "GAME_OVER":
            # Si el jugador mantiene la mano sobre el botón de reintento
            if self.btn_restart.update(self.player.rect):
                # Reiniciamos al estado START para mostrar las instrucciones
                # y permitir que el jugador se prepare de nuevo
                self.state = "START"
                
                # Reseteamos los botones para que no se queden con progreso
                self.btn_start.reset()
                self.btn_restart.reset()
                self.btn_resume.reset()

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
            offset_x = random.randint(-self.shake_intensity, self.shake_intensity)
            offset_y = random.randint(-self.shake_intensity, self.shake_intensity)
            self.shake_intensity -= 1 

        # --- 2. DIBUJAR EL FONDO ---
        if self.bg_image:
            self.screen.blit(self.bg_image, (offset_x, offset_y))
        else:
            self.screen.fill(COLOR_BLACK)
        
        # ==========================================
        # ESTADO: MENÚ DE INICIO
        # ==========================================
        if self.state == "START":
            self.player.update() 
            temp_rect = self.player.rect.copy()
            temp_rect.x += offset_x
            temp_rect.y += offset_y
            self.screen.blit(self.player.image, temp_rect)
            
            # --- TÍTULO Y RÉCORD ---
            self.draw_text("AGRO-DEFENDER", self.font_large, COLOR_WHITE, WINDOW_WIDTH//2 + offset_x, WINDOW_HEIGHT//4 + offset_y, True)
            self.draw_text(f"RECORD: {self.high_score}", self.font_medium, (255, 215, 0), WINDOW_WIDTH//2 + offset_x, WINDOW_HEIGHT//4 + 70 + offset_y, True)
            
            # --- INSTRUCCIONES ACTUALIZADAS (Controles por gestos) ---
            self.draw_text("CÓMO JUGAR:", self.font_medium, (200, 200, 255), WINDOW_WIDTH//2 + offset_x, WINDOW_HEIGHT//2 - 20 + offset_y, True)
                        
            self.draw_text(" Mueve la mano abierta para controlar la mira y aplastar plagas", self.font_small, COLOR_WHITE, WINDOW_WIDTH//2 + offset_x, WINDOW_HEIGHT//2 + 25 + offset_y, True)
                        
            self.draw_text("Cierra la mano (PUÑO) en cualquier momento para PAUSAR", self.font_small, (255, 100, 100), WINDOW_WIDTH//2 + offset_x, WINDOW_HEIGHT//2 + 65 + offset_y, True)
                                   
            self.draw_text("- Mariquita = +1 Vida  |  Cristal = Congelar Tiempo", self.font_small, (173, 216, 230), WINDOW_WIDTH//2 + offset_x, WINDOW_HEIGHT//2 + 105 + offset_y, True)                                   
            self.draw_text("¡7 Kills seguidos activan el MODO FIEBRE!", self.font_small, (255, 215, 0), WINDOW_WIDTH//2 + offset_x, WINDOW_HEIGHT//2 + 145 + offset_y, True)
            
            # --- BOTÓN DE INICIO VIRTUAL ---
            # Ya no usamos "Press SPACE", ahora dibujamos el botón virtual
            self.btn_start.draw(self.screen)
            
            # --- CRÉDITOS ---
            credits_text = "Desarrollado por: Erick Olivo"
            self.draw_text(credits_text, self.font_small, (150, 150, 150), WINDOW_WIDTH//2 + offset_x, WINDOW_HEIGHT - 40 + offset_y, True)
            
        # ==========================================
        # ESTADO: JUEGO EN PAUSA
        # ==========================================
        elif self.state == "PAUSED":
            # Dibujamos todo congelado de fondo
            self.all_sprites.draw(self.screen)
            
            # Capa oscura
            pause_overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
            pause_overlay.fill((0, 0, 0, 150))
            self.screen.blit(pause_overlay, (0, 0))
            
            self.draw_text("JUEGO EN PAUSA", self.font_large, COLOR_WHITE, WINDOW_WIDTH//2, WINDOW_HEIGHT//2 - 50, True)
            
            # Dibujamos el botón para reanudar
            self.btn_resume.draw(self.screen)
            
            # Dibujamos la mano por encima para interactuar
            self.player.update()
            self.screen.blit(self.player.image, self.player.rect)

        # ==========================================
        # ESTADO: JUGANDO
        # ==========================================
        elif self.state == "PLAYING":
            self.all_sprites.draw(self.screen)
            
            # --- EFECTO VISUAL DE HIELO (OVERLAY) ---
            if getattr(self, 'is_frozen', False):
                freeze_overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
                freeze_overlay.fill((173, 216, 230, 80)) 
                self.screen.blit(freeze_overlay, (0, 0))
                
                freeze_text = self.font_medium.render("¡TIEMPO CONGELADO!", True, (255, 255, 255))
                text_rect = freeze_text.get_rect(center=(WINDOW_WIDTH // 2, 130))
                self.screen.blit(freeze_text, text_rect)
                
            # --- EFECTO VISUAL DE FRENESÍ (FRENESÍ) ---
            if getattr(self, 'is_fever_mode', False):
                import math
                current_time = pygame.time.get_ticks()
                
                # Calculamos el tiempo restante del frenesí
                fever_elapsed = current_time - self.fever_start_time
                fever_time_left = max(0, (self.fever_duration - fever_elapsed) // 1000)
                
                # Overlay parpadeante
                pulse = int(math.sin(current_time * 0.01) * 20) + 60
                frenzy_overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
                frenzy_overlay.fill((255, 69, 0, pulse)) 
                self.screen.blit(frenzy_overlay, (0, 0))
                
                # Mensaje de estado
                self.draw_text("¡FRENESÍ: CULTIVO PROTEGIDO!", self.font_large, (255, 255, 0), WINDOW_WIDTH//2, 130, True)
                
                # CRONÓMETRO DEL FRENESÍ
                self.draw_text(f"TIEMPO RESTANTE: {fever_time_left}s", self.font_medium, (255, 255, 255), WINDOW_WIDTH//2, 190, True)
                
            # --- HUD (Heads Up Display) ---
            current_time = pygame.time.get_ticks()
            time_left = max(0, GAME_DURATION_SECONDS - ((current_time - self.start_time) // 1000))
            
            self.draw_text(f"Score: {self.score}", self.font_medium, COLOR_WHITE, 20, 20)
            
            # --- DIBUJAR CORAZONES ---
            if self.heart_image:
                for i in range(self.lives):
                    self.screen.blit(self.heart_image, (20 + (i * 35), 65))
            else:
                self.draw_text(f"Lives: {self.lives}", self.font_medium, COLOR_WHITE, 20, 60)

            if self.combo > 0:
                combo_color = (255, 215, 0) if self.multiplier > 1 else COLOR_WHITE
                self.draw_text(f"Combo: {self.combo} (x{self.multiplier})", 
                               self.font_medium, combo_color, 20, 100)
            
            self.draw_text(f"Time: {time_left}s", self.font_medium, COLOR_WHITE, WINDOW_WIDTH - 200, 20)
            
        # ==========================================
        # ESTADO: GAME OVER
        # ==========================================
        elif self.state == "GAME_OVER":
            self.player.update() 
            self.screen.blit(self.player.image, self.player.rect)
            self.draw_text("GAME OVER", self.font_large, COLOR_WHITE, WINDOW_WIDTH//2, WINDOW_HEIGHT//2 - 50, True)
            self.draw_text(f"Final Score: {self.score}", self.font_medium, COLOR_WHITE, WINDOW_WIDTH//2, WINDOW_HEIGHT//2 + 20, True)
            # AQUÍ TE DEJO EL ESPACIO POR SI LUEGO QUIERES PONER BOTÓN DE REINICIO TAMBIÉN
            self.draw_text(f"RECORD: {self.high_score}", self.font_medium, (255, 215, 0), WINDOW_WIDTH//2, WINDOW_HEIGHT//2 - 90, True)

            self.btn_restart.draw(self.screen)         

        # Dibuja un pequeño punto guía en el centro de la mira para precisión extra
        pygame.draw.circle(self.screen, (0, 255, 255), self.player.rect.center, 5)     
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
