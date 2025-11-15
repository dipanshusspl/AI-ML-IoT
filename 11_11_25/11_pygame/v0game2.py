import pygame
import cv2
import mediapipe as mp
import numpy as np
import random
import math
from enum import Enum
from collections import deque

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 50, 50)
GREEN = (50, 255, 50)
BLUE = (50, 150, 255)
YELLOW = (255, 255, 50)
PURPLE = (200, 50, 255)
ORANGE = (255, 165, 50)
CYAN = (50, 255, 255)
DARK_BG = (15, 15, 35)
NEON_PINK = (255, 20, 147)
NEON_GREEN = (57, 255, 20)

# Game states
class GameState(Enum):
    MENU = 1
    PLAYING = 2
    PAUSED = 3
    GAME_OVER = 4

# Player class
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.width = 40
        self.height = 50
        self.image = pygame.Surface((self.width, self.height))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.vel_x = 0
        self.vel_y = 0
        self.on_ground = False
        self.jump_power = 15
        self.health = 100
        self.max_health = 100
        self.shield = False
        self.shield_time = 0
        self.invincible_time = 0
        self.draw_player()
        
    def draw_player(self):
        self.image.fill(DARK_BG)
        if self.shield:
            pygame.draw.circle(self.image, CYAN, (self.width // 2, self.height // 2), self.width // 2 + 3, 2)
        color = NEON_GREEN if self.invincible_time > 0 else BLUE
        pygame.draw.rect(self.image, color, (0, 0, self.width, self.height))
        pygame.draw.circle(self.image, YELLOW, (self.width // 4, self.height // 4), 4)
        pygame.draw.circle(self.image, YELLOW, (self.width - self.width // 4, self.height // 4), 4)
        
    def update(self):
        # Gravity
        self.vel_y += 0.6
        self.rect.y += self.vel_y
        self.rect.x += self.vel_x
        
        # Floor collision
        if self.rect.bottom >= SCREEN_HEIGHT - 50:
            self.rect.bottom = SCREEN_HEIGHT - 50
            self.vel_y = 0
            self.on_ground = True
        else:
            self.on_ground = False
            
        # Screen boundaries
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
            
        # Friction
        self.vel_x *= 0.9
        
        # Update timers
        if self.shield_time > 0:
            self.shield_time -= 1
            self.shield = True
        else:
            self.shield = False
            
        if self.invincible_time > 0:
            self.invincible_time -= 1
            
        self.draw_player()
        
    def jump(self):
        if self.on_ground:
            self.vel_y = -self.jump_power
            
    def move_left(self):
        self.vel_x = -8
        
    def move_right(self):
        self.vel_x = 8
        
    def take_damage(self, amount):
        if not self.shield and self.invincible_time <= 0:
            self.health -= amount
            self.invincible_time = 30
            return True
        return False

# Obstacle class
class Obstacle(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, speed):
        super().__init__()
        self.width = width
        self.height = height
        self.image = pygame.Surface((width, height))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed = speed
        self.color = RED
        self.draw_obstacle()
        
    def draw_obstacle(self):
        self.image.fill(DARK_BG)
        pygame.draw.rect(self.image, self.color, (0, 0, self.width, self.height))
        pygame.draw.rect(self.image, NEON_PINK, (0, 0, self.width, self.height), 2)
        
    def update(self):
        self.rect.y += self.speed
        
    def is_off_screen(self):
        return self.rect.top > SCREEN_HEIGHT

# PowerUp class
class PowerUp(pygame.sprite.Sprite):
    def __init__(self, x, y, power_type):
        super().__init__()
        self.width = 30
        self.height = 30
        self.image = pygame.Surface((self.width, self.height))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.power_type = power_type  # "health", "shield", "slow", "score"
        self.speed = 3
        self.rotation = 0
        self.draw_powerup()
        
    def draw_powerup(self):
        self.image.fill(DARK_BG)
        self.rotation = (self.rotation + 5) % 360
        
        if self.power_type == "health":
            color = GREEN
        elif self.power_type == "shield":
            color = CYAN
        elif self.power_type == "slow":
            color = ORANGE
        else:  # score
            color = YELLOW
            
        pygame.draw.circle(self.image, color, (self.width // 2, self.height // 2), self.width // 2)
        pygame.draw.circle(self.image, WHITE, (self.width // 2, self.height // 2), self.width // 2 - 3, 2)
        
    def update(self):
        self.rect.y += self.speed
        self.draw_powerup()
        
    def is_off_screen(self):
        return self.rect.top > SCREEN_HEIGHT

# Game class
class GestureGuardian:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Gesture Guardian - Use Hand Gestures & Arrow Keys!")
        self.clock = pygame.time.Clock()
        self.font_large = pygame.font.Font(None, 60)
        self.font_medium = pygame.font.Font(None, 40)
        self.font_small = pygame.font.Font(None, 24)
        
        # Game state
        self.state = GameState.MENU
        self.score = 0
        self.wave = 1
        self.game_time = 0
        
        # Sprites
        self.all_sprites = pygame.sprite.Group()
        self.obstacles = pygame.sprite.Group()
        self.powerups = pygame.sprite.Group()
        self.player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100)
        self.all_sprites.add(self.player)
        
        # Spawn timing
        self.spawn_timer = 0
        self.spawn_rate = 40
        self.slow_effect = 0
        
        # Hand tracking
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )
        self.mp_drawing = mp.solutions.drawing_utils
        self.hand_x = SCREEN_WIDTH // 2
        self.hand_y = SCREEN_HEIGHT // 2
        self.hand_detected = False
        self.gesture_history = deque(maxlen=10)
        
    def detect_hand_gesture(self, frame):
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb_frame)
        
        self.hand_detected = False
        
        if results.multi_hand_landmarks:
            hand_landmarks = results.multi_hand_landmarks[0]
            
            # Get hand position (middle of palm)
            hand_x = int(hand_landmarks.landmark[9].x * SCREEN_WIDTH)
            hand_y = int(hand_landmarks.landmark[9].y * SCREEN_HEIGHT * 0.6)  # Scale to game area
            
            self.hand_x = hand_x
            self.hand_y = hand_y
            self.hand_detected = True
            
            # Detect gesture - check finger positions
            landmarks = hand_landmarks.landmark
            
            # Check if hand is open (all fingers extended) or closed (fist)
            fingers_up = []
            for i in [4, 8, 12, 16, 20]:
                fingers_up.append(landmarks[i].y < landmarks[i - 2].y)
            
            fingers_extended = sum(fingers_up)
            
            # Store gesture
            self.gesture_history.append({
                'x': hand_x,
                'fingers': fingers_extended,
                'y': hand_y
            })
            
            # Detect jump gesture (hand raised high)
            if hand_y < SCREEN_HEIGHT * 0.2:
                return "jump"
            
            # Detect punch/attack gesture (fist - less than 2 fingers extended)
            if fingers_extended <= 1:
                return "attack"
                
        return None
        
    def handle_input(self, gesture):
        keys = pygame.key.get_pressed()
        
        # Arrow key controls
        if keys[pygame.K_LEFT]:
            self.player.move_left()
        if keys[pygame.K_RIGHT]:
            self.player.move_right()
        if keys[pygame.K_UP]:
            self.player.jump()
        if keys[pygame.K_SPACE]:
            self.player.jump()
            
        # Gesture controls
        if gesture == "jump":
            self.player.jump()
        elif gesture == "attack":
            self.create_attack()
            
        # Hand position control (horizontal movement)
        if self.hand_detected:
            # Map hand position to player horizontal movement
            hand_screen_center = SCREEN_WIDTH // 2
            deviation = self.hand_x - hand_screen_center
            
            if abs(deviation) > 50:
                if deviation > 0:
                    self.player.move_right()
                else:
                    self.player.move_left()
                    
    def create_attack(self):
        # Visual feedback for attack
        pass
        
    def spawn_obstacle(self):
        x = random.randint(0, SCREEN_WIDTH - 50)
        y = -50
        width = random.randint(40, 80)
        height = random.randint(30, 60)
        speed = 3 + (self.wave * 0.5)
        
        if random.random() < 0.15:  # 15% chance for powerup instead
            self.powerups.add(PowerUp(x, y, random.choice(["health", "shield", "slow", "score"])))
        else:
            obstacle = Obstacle(x, y, width, height, speed)
            self.obstacles.add(obstacle)
            self.all_sprites.add(obstacle)
            
    def spawn_powerup(self):
        x = random.randint(0, SCREEN_WIDTH - 30)
        y = -30
        power_type = random.choice(["health", "shield", "slow", "score"])
        powerup = PowerUp(x, y, power_type)
        self.powerups.add(powerup)
        self.all_sprites.add(powerup)
        
    def update_game(self):
        self.all_sprites.update()
        
        # Spawn obstacles
        self.spawn_timer += 1
        if self.spawn_timer > self.spawn_rate:
            self.spawn_obstacle()
            self.spawn_timer = 0
            
        # Update slow effect
        if self.slow_effect > 0:
            self.slow_effect -= 1
            
        # Collision detection - obstacles
        hits = pygame.sprite.spritecollide(self.player, self.obstacles, True)
        for obstacle in hits:
            if self.player.take_damage(10):
                self.score -= 5
            self.obstacles.discard(obstacle)
            if obstacle in self.all_sprites:
                self.all_sprites.remove(obstacle)
                
        # Collision detection - powerups
        powerup_hits = pygame.sprite.spritecollide(self.player, self.powerups, True)
        for powerup in powerup_hits:
            if powerup.power_type == "health":
                self.player.health = min(self.player.health + 25, self.player.max_health)
                self.score += 50
            elif powerup.power_type == "shield":
                self.player.shield_time = 150
                self.score += 75
            elif powerup.power_type == "slow":
                self.slow_effect = 200
                for obs in self.obstacles:
                    obs.speed *= 0.5
                self.score += 100
            elif powerup.power_type == "score":
                self.score += 250
                
            self.all_sprites.remove(powerup)
            
        # Remove off-screen objects
        for obstacle in list(self.obstacles):
            if obstacle.is_off_screen():
                self.obstacles.remove(obstacle)
                self.all_sprites.remove(obstacle)
                self.score += 10
                
        for powerup in list(self.powerups):
            if powerup.is_off_screen():
                self.all_sprites.remove(powerup)
                self.powerups.remove(powerup)
                
        # Update wave difficulty
        if self.game_time % 600 == 0 and self.game_time > 0:
            self.wave += 1
            self.spawn_rate = max(20, self.spawn_rate - 3)
            
        # Game over condition
        if self.player.health <= 0:
            self.state = GameState.GAME_OVER
            
        self.game_time += 1
        
    def draw_game(self):
        self.screen.fill(DARK_BG)
        
        # Draw floor
        pygame.draw.line(self.screen, NEON_GREEN, (0, SCREEN_HEIGHT - 50), (SCREEN_WIDTH, SCREEN_HEIGHT - 50), 3)
        
        # Draw all sprites
        self.all_sprites.draw(self.screen)
        
        # Draw hand indicator
        if self.hand_detected:
            pygame.draw.circle(self.screen, NEON_PINK, (self.hand_x, self.hand_y), 15, 2)
            pygame.draw.line(self.screen, NEON_PINK, (self.hand_x - 10, self.hand_y), (self.hand_x + 10, self.hand_y), 2)
            pygame.draw.line(self.screen, NEON_PINK, (self.hand_x, self.hand_y - 10), (self.hand_x, self.hand_y + 10), 2)
            
        # Draw UI
        health_text = self.font_small.render(f"Health: {self.player.health}", True, GREEN if self.player.health > 50 else RED)
        self.screen.blit(health_text, (20, 20))
        
        score_text = self.font_small.render(f"Score: {self.score}", True, YELLOW)
        self.screen.blit(score_text, (SCREEN_WIDTH - 300, 20))
        
        wave_text = self.font_small.render(f"Wave: {self.wave}", True, NEON_PINK)
        self.screen.blit(wave_text, (SCREEN_WIDTH // 2 - 50, 20))
        
        if self.player.shield:
            shield_text = self.font_small.render("SHIELD ACTIVE", True, CYAN)
            self.screen.blit(shield_text, (20, 60))
            
        pygame.display.flip()
        
    def draw_menu(self):
        self.screen.fill(DARK_BG)
        
        title = self.font_large.render("GESTURE GUARDIAN", True, NEON_PINK)
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 50))
        
        subtitle = self.font_medium.render("Control with Hand Gestures or Arrow Keys", True, CYAN)
        self.screen.blit(subtitle, (SCREEN_WIDTH // 2 - subtitle.get_width() // 2, 150))
        
        controls = [
            "ARROW KEYS: Move Left/Right, Jump",
            "HAND POSITION: Move character left/right",
            "RAISE HAND HIGH: Jump",
            "MAKE A FIST: Attack (coming soon!)",
            "AVOID RED OBSTACLES",
            "COLLECT POWER-UPS FOR BONUS POINTS"
        ]
        
        y = 250
        for control in controls:
            text = self.font_small.render(control, True, WHITE)
            self.screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, y))
            y += 50
            
        start_text = self.font_medium.render("PRESS SPACE TO START", True, NEON_GREEN)
        self.screen.blit(start_text, (SCREEN_WIDTH // 2 - start_text.get_width() // 2, SCREEN_HEIGHT - 100))
        
        pygame.display.flip()
        
    def draw_game_over(self):
        self.screen.fill(DARK_BG)
        
        game_over_text = self.font_large.render("GAME OVER", True, RED)
        self.screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, 100))
        
        final_score = self.font_medium.render(f"Final Score: {self.score}", True, YELLOW)
        self.screen.blit(final_score, (SCREEN_WIDTH // 2 - final_score.get_width() // 2, 250))
        
        wave_reached = self.font_medium.render(f"Wave Reached: {self.wave}", True, NEON_PINK)
        self.screen.blit(wave_reached, (SCREEN_WIDTH // 2 - wave_reached.get_width() // 2, 350))
        
        restart_text = self.font_medium.render("PRESS SPACE TO RESTART", True, NEON_GREEN)
        self.screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, 500))
        
        pygame.display.flip()
        
    def reset_game(self):
        self.score = 0
        self.wave = 1
        self.game_time = 0
        self.spawn_timer = 0
        self.spawn_rate = 40
        self.slow_effect = 0
        
        self.all_sprites.empty()
        self.obstacles.empty()
        self.powerups.empty()
        
        self.player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100)
        self.all_sprites.add(self.player)
        
        self.state = GameState.PLAYING
        
    def run(self):
        running = True
        
        print("[v0] Gesture Guardian starting...")
        print("[v0] Camera initialized. Make sure to allow camera access.")
        print("[v0] Use arrow keys or hand gestures to play!")
        
        while running:
            ret, frame = self.cap.read()
            
            if ret:
                frame = cv2.flip(frame, 1)
                gesture = self.detect_hand_gesture(frame)
            else:
                gesture = None
                
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        if self.state == GameState.MENU:
                            self.state = GameState.PLAYING
                        elif self.state == GameState.GAME_OVER:
                            self.reset_game()
                    if event.key == pygame.K_p:
                        if self.state == GameState.PLAYING:
                            self.state = GameState.PAUSED
                        elif self.state == GameState.PAUSED:
                            self.state = GameState.PLAYING
                    if event.key == pygame.K_ESCAPE:
                        running = False
                        
            if self.state == GameState.MENU:
                self.draw_menu()
            elif self.state == GameState.PLAYING:
                self.handle_input(gesture)
                self.update_game()
                self.draw_game()
            elif self.state == GameState.GAME_OVER:
                self.draw_game_over()
                
            self.clock.tick(60)
            
        self.cap.release()
        pygame.quit()
        print("[v0] Game closed successfully!")

if __name__ == "__main__":
    game = GestureGuardian()
    game.run()