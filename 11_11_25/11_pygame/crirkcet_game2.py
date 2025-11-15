import pygame
import cv2
import mediapipe as mp
import random
import math
import sys

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 1400, 800
FPS = 60

# Enhanced Colors
SKY_BLUE = (135, 206, 250)
SKY_GRADIENT_TOP = (70, 130, 180)
GRASS_GREEN = (50, 168, 82)
GRASS_DARK = (34, 139, 34)
PITCH_COLOR = (205, 170, 125)
PITCH_DARK = (160, 130, 90)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (220, 20, 60)
CRIMSON = (220, 20, 60)
YELLOW = (255, 223, 0)
GOLD = (255, 215, 0)
ORANGE = (255, 140, 0)
BROWN = (101, 67, 33)
LIGHT_BROWN = (139, 90, 43)
STADIUM_GRAY = (100, 100, 110)
CROWD_COLORS = [(180, 50, 50), (50, 100, 180), (50, 150, 50), (200, 200, 50)]

# Setup display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Cricket Master - Realistic Edition")
clock = pygame.time.Clock()

# Fonts
title_font = pygame.font.Font(None, 84)
score_font = pygame.font.Font(None, 56)
text_font = pygame.font.Font(None, 42)
small_font = pygame.font.Font(None, 28)

# MediaPipe setup
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7,
    max_num_hands=2
)

# Camera setup
try:
    cap = cv2.VideoCapture(0)
    camera_available = cap.isOpened()
except:
    camera_available = False

class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.vx = random.uniform(-3, 3)
        self.vy = random.uniform(-5, -2)
        self.life = 60
        self.color = color
        self.size = random.randint(3, 6)
    
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.2
        self.life -= 1
        
    def draw(self, screen):
        alpha = int(255 * (self.life / 60))
        s = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        pygame.draw.circle(s, (*self.color, alpha), (self.size, self.size), self.size)
        screen.blit(s, (int(self.x) - self.size, int(self.y) - self.size))

class Ball:
    def __init__(self):
        self.reset()
        self.particles = []
        
    def reset(self):
        self.x = WIDTH // 2
        self.y = 150
        self.radius = 14
        self.speed = random.uniform(5, 8)
        self.angle = random.uniform(-10, 10)
        self.is_moving = False
        self.bowled = False
        self.hit = False
        self.hit_power = 0
        self.hit_angle = 0
        self.trajectory = []
        self.gravity = 0.35
        self.vy = 0
        self.vx = 0
        self.rotation = 0
        self.spin = random.uniform(-5, 5)
        
    def bowl(self):
        self.bowled = True
        self.is_moving = True
        self.vy = self.speed
        self.vx = math.sin(math.radians(self.angle)) * 3
        
    def update(self):
        if self.is_moving:
            self.rotation += self.spin
            
            if not self.hit:
                # Ball moving towards batsman
                self.y += self.vy
                self.x += self.vx
                
                # Add slight curve
                self.vx += math.sin(math.radians(self.angle)) * 0.1
                
                # Check if ball reached batsman
                if self.y >= 600:
                    return "missed"
            else:
                # Ball was hit - create particles
                if random.random() < 0.3:
                    self.particles.append(Particle(self.x, self.y, YELLOW))
                
                self.trajectory.append((int(self.x), int(self.y)))
                self.vy += self.gravity
                self.x += self.vx
                self.y += self.vy
                
                # Air resistance
                self.vx *= 0.995
                
                # Check boundaries
                if self.y >= HEIGHT - 80 or self.x < 0 or self.x > WIDTH or self.y < -100:
                    return "scored"
        
        # Update particles
        self.particles = [p for p in self.particles if p.life > 0]
        for p in self.particles:
            p.update()
            
        return None
    
    def hit_ball(self, timing_quality):
        self.hit = True
        # Better timing = better shot
        base_power = 18
        power = timing_quality * base_power
        angle_variation = (1 - timing_quality) * 40
        self.hit_angle = random.uniform(-70 - angle_variation, -25 + angle_variation)
        
        self.vx = math.cos(math.radians(self.hit_angle)) * power
        self.vy = math.sin(math.radians(self.hit_angle)) * power
        self.hit_power = timing_quality
        self.spin = random.uniform(-15, 15)
        
        # Create impact particles
        for _ in range(15):
            self.particles.append(Particle(self.x, self.y, YELLOW))
        
    def draw(self, screen):
        # Draw trajectory with fade
        if len(self.trajectory) > 1:
            for i in range(len(self.trajectory) - 1):
                alpha = int(255 * (i / len(self.trajectory)))
                start = self.trajectory[i]
                end = self.trajectory[i + 1]
                s = pygame.Surface((abs(end[0] - start[0]) + 5, abs(end[1] - start[1]) + 5), pygame.SRCALPHA)
                color = (*GOLD, alpha)
                thickness = max(1, int(3 * (i / len(self.trajectory))))
                pygame.draw.line(screen, GOLD, start, end, thickness)
        
        # Draw particles
        for p in self.particles:
            p.draw(screen)
        
        # Draw ball with 3D effect
        pygame.draw.circle(screen, (100, 0, 0), (int(self.x + 2), int(self.y + 2)), self.radius)  # Shadow
        pygame.draw.circle(screen, CRIMSON, (int(self.x), int(self.y)), self.radius)
        
        # Shine effect
        shine_x = int(self.x - self.radius // 3)
        shine_y = int(self.y - self.radius // 3)
        pygame.draw.circle(screen, (255, 150, 150), (shine_x, shine_y), self.radius // 3)
        
        # Seam
        seam_offset = int(self.rotation) % 360
        if seam_offset < 180:
            start = (int(self.x - self.radius), int(self.y))
            end = (int(self.x + self.radius), int(self.y))
            pygame.draw.line(screen, WHITE, start, end, 2)

class Batsman:
    def __init__(self):
        self.x = WIDTH // 2
        self.y = 600
        self.width = 50
        self.height = 100
        self.bat_angle = 0
        self.is_swinging = False
        self.swing_timer = 0
        self.stance_offset = 0
        
    def swing(self):
        if not self.is_swinging:
            self.is_swinging = True
            self.swing_timer = 20
    
    def update(self):
        # Slight breathing animation
        self.stance_offset = math.sin(pygame.time.get_ticks() / 500) * 2
        
        if self.is_swinging:
            self.swing_timer -= 1
            progress = (20 - self.swing_timer) / 20
            self.bat_angle = -90 * math.sin(progress * math.pi)
            
            if self.swing_timer <= 0:
                self.is_swinging = False
                self.bat_angle = 0
    
    def draw(self, screen):
        y_pos = self.y + self.stance_offset
        
        # Shadow
        shadow_surf = pygame.Surface((80, 20), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow_surf, (0, 0, 0, 60), (0, 0, 80, 20))
        screen.blit(shadow_surf, (self.x - 40, y_pos + 80))
        
        # Legs with pads
        leg_color = WHITE
        pygame.draw.rect(screen, leg_color, (self.x - 18, y_pos + 50, 12, 35), border_radius=3)
        pygame.draw.rect(screen, leg_color, (self.x + 6, y_pos + 50, 12, 35), border_radius=3)
        
        # Shoes
        pygame.draw.ellipse(screen, BLACK, (self.x - 20, y_pos + 82, 16, 8))
        pygame.draw.ellipse(screen, BLACK, (self.x + 4, y_pos + 82, 16, 8))
        
        # Body with jersey
        jersey_color = (0, 100, 200)
        pygame.draw.rect(screen, jersey_color, (self.x - 15, y_pos + 15, 30, 40), border_radius=5)
        
        # Arms
        pygame.draw.circle(screen, (255, 220, 177), (self.x - 20, y_pos + 25), 8)
        pygame.draw.circle(screen, (255, 220, 177), (self.x + 20, y_pos + 25), 8)
        
        # Head with helmet
        pygame.draw.circle(screen, (255, 220, 177), (self.x, y_pos), 18)
        pygame.draw.arc(screen, (20, 50, 100), (self.x - 20, y_pos - 22, 40, 35), 0, math.pi, 5)
        pygame.draw.circle(screen, (50, 50, 50), (self.x, y_pos - 10), 3)  # Grill
        
        # Gloves
        pygame.draw.circle(screen, WHITE, (self.x + 25, y_pos + 35), 8)
        pygame.draw.circle(screen, WHITE, (self.x - 25, y_pos + 35), 8)
        
        # Draw bat with realistic colors
        bat_length = 85
        bat_width = 12
        
        bat_base_x = self.x + 35
        bat_base_y = y_pos + 30
        
        end_x = bat_base_x + math.cos(math.radians(self.bat_angle)) * bat_length
        end_y = bat_base_y + math.sin(math.radians(self.bat_angle)) * bat_length
        
        # Bat blade (willow)
        blade_color = (210, 180, 140)
        pygame.draw.line(screen, blade_color, (bat_base_x, bat_base_y), (end_x, end_y), bat_width + 2)
        
        # Handle (grip)
        handle_length = 25
        handle_x = bat_base_x - math.cos(math.radians(self.bat_angle)) * handle_length
        handle_y = bat_base_y - math.sin(math.radians(self.bat_angle)) * handle_length
        pygame.draw.line(screen, (80, 50, 20), (bat_base_x, bat_base_y), (handle_x, handle_y), 8)

class Bowler:
    def __init__(self):
        self.x = WIDTH // 2
        self.y = 120
        self.is_bowling = False
        self.bowl_timer = 0
        self.animation_frame = 0
        
    def bowl(self):
        if not self.is_bowling:
            self.is_bowling = True
            self.bowl_timer = 30
            self.animation_frame = 0
    
    def update(self):
        if self.is_bowling:
            self.bowl_timer -= 1
            self.animation_frame = 30 - self.bowl_timer
            if self.bowl_timer <= 0:
                self.is_bowling = False
                self.animation_frame = 0
    
    def draw(self, screen):
        # Calculate animation progress
        if self.is_bowling:
            progress = self.animation_frame / 30
            arm_angle = -180 * progress
            jump_height = math.sin(progress * math.pi) * 30
        else:
            arm_angle = 0
            jump_height = 0
        
        y_pos = self.y - jump_height
        
        # Shadow
        shadow_surf = pygame.Surface((70, 15), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow_surf, (0, 0, 0, 60), (0, 0, 70, 15))
        screen.blit(shadow_surf, (self.x - 35, self.y + 60))
        
        # Legs
        pygame.draw.rect(screen, WHITE, (self.x - 15, y_pos + 40, 10, 30), border_radius=3)
        pygame.draw.rect(screen, WHITE, (self.x + 5, y_pos + 40, 10, 30), border_radius=3)
        
        # Body with jersey
        jersey_color = (200, 50, 50)
        pygame.draw.rect(screen, jersey_color, (self.x - 12, y_pos + 10, 24, 35), border_radius=4)
        
        # Bowling arm
        arm_length = 35
        arm_x = self.x + math.cos(math.radians(arm_angle)) * arm_length
        arm_y = y_pos + 15 + math.sin(math.radians(arm_angle)) * arm_length
        pygame.draw.line(screen, (255, 220, 177), (self.x, y_pos + 15), (arm_x, arm_y), 8)
        pygame.draw.circle(screen, (255, 220, 177), (int(arm_x), int(arm_y)), 7)
        
        # Other arm
        pygame.draw.circle(screen, (255, 220, 177), (self.x - 15, y_pos + 20), 6)
        
        # Head
        pygame.draw.circle(screen, (255, 220, 177), (self.x, y_pos - 5), 15)
        
        # Cap
        pygame.draw.arc(screen, (50, 100, 50), (self.x - 18, y_pos - 22, 36, 30), 0, math.pi, 4)
        pygame.draw.line(screen, (50, 100, 50), (self.x - 10, y_pos - 5), (self.x + 25, y_pos - 5), 3)

class Stadium:
    def __init__(self):
        self.crowd_particles = []
        for _ in range(80):
            x = random.randint(0, WIDTH)
            y = random.randint(50, 250)
            color = random.choice(CROWD_COLORS)
            self.crowd_particles.append((x, y, color))
    
    def draw(self, screen):
        # Sky gradient
        for i in range(HEIGHT // 2):
            ratio = i / (HEIGHT // 2)
            color = (
                int(SKY_GRADIENT_TOP[0] + (SKY_BLUE[0] - SKY_GRADIENT_TOP[0]) * ratio),
                int(SKY_GRADIENT_TOP[1] + (SKY_BLUE[1] - SKY_GRADIENT_TOP[1]) * ratio),
                int(SKY_GRADIENT_TOP[2] + (SKY_BLUE[2] - SKY_GRADIENT_TOP[2]) * ratio)
            )
            pygame.draw.line(screen, color, (0, i), (WIDTH, i))
        
        # Stadium stands
        pygame.draw.rect(screen, STADIUM_GRAY, (0, 0, WIDTH, 280))
        pygame.draw.rect(screen, (80, 80, 90), (0, 250, WIDTH, 30))
        
        # Crowd (simplified)
        for x, y, color in self.crowd_particles:
            pygame.draw.circle(screen, color, (x, y), 4)
        
        # Stadium roof
        pygame.draw.polygon(screen, (70, 70, 80), [(0, 0), (WIDTH, 0), (WIDTH, 200), (0, 200)])
        
        # Floodlights
        for x in [150, WIDTH - 150]:
            pygame.draw.rect(screen, (200, 200, 200), (x - 10, 30, 20, 180))
            pygame.draw.circle(screen, YELLOW, (x, 60), 25)
            pygame.draw.circle(screen, (255, 255, 200), (x, 60), 18)
        
        # Ground
        ground_y = HEIGHT // 2 + 50
        pygame.draw.rect(screen, GRASS_GREEN, (0, ground_y, WIDTH, HEIGHT - ground_y))
        
        # Grass texture
        for i in range(50):
            x1 = random.randint(0, WIDTH)
            y1 = random.randint(ground_y, HEIGHT)
            pygame.draw.line(screen, GRASS_DARK, (x1, y1), (x1 + 2, y1 + 3), 1)
        
        # Cricket pitch
        pitch_x = WIDTH // 2 - 120
        pitch_y = 350
        pitch_width = 240
        pitch_height = 400
        
        # Pitch shadow
        pygame.draw.rect(screen, PITCH_DARK, (pitch_x + 5, pitch_y + 5, pitch_width, pitch_height), border_radius=10)
        pygame.draw.rect(screen, PITCH_COLOR, (pitch_x, pitch_y, pitch_width, pitch_height), border_radius=10)
        
        # Creases
        pygame.draw.line(screen, WHITE, (pitch_x, pitch_y + 50), (pitch_x + pitch_width, pitch_y + 50), 3)
        pygame.draw.line(screen, WHITE, (pitch_x, pitch_y + pitch_height - 50), (pitch_x + pitch_width, pitch_y + pitch_height - 50), 3)
        
        # Stumps
        self.draw_stumps(screen, WIDTH // 2, pitch_y + 40)
        self.draw_stumps(screen, WIDTH // 2, pitch_y + pitch_height - 40)
        
        # Boundary rope
        pygame.draw.circle(screen, WHITE, (WIDTH // 2, HEIGHT - 100), 500, 4)
        
    def draw_stumps(self, screen, x, y):
        stump_color = (220, 200, 150)
        bail_color = (200, 180, 130)
        
        # Three stumps
        for offset in [-15, 0, 15]:
            pygame.draw.rect(screen, BLACK, (x + offset - 2, y - 2, 4, 32))
            pygame.draw.rect(screen, stump_color, (x + offset - 1, y, 2, 30), border_radius=1)
        
        # Bails
        pygame.draw.line(screen, bail_color, (x - 16, y - 2), (x - 5, y - 2), 2)
        pygame.draw.line(screen, bail_color, (x + 5, y - 2), (x + 16, y - 2), 2)

class Game:
    def __init__(self):
        self.score = 0
        self.balls_faced = 0
        self.wickets = 0
        self.max_wickets = 3
        self.state = "menu"
        self.ball = Ball()
        self.batsman = Batsman()
        self.bowler = Bowler()
        self.stadium = Stadium()
        self.message = ""
        self.message_timer = 0
        self.combo = 0
        self.best_score = 0
        self.can_bowl = True
        self.gesture_cooldown = 0
        
    def show_message(self, text, duration=80):
        self.message = text
        self.message_timer = duration
        
    def calculate_runs(self, timing_quality):
        if timing_quality >= 0.9:
            self.combo += 1
            return 6
        elif timing_quality >= 0.75:
            self.combo += 1
            return 4
        elif timing_quality >= 0.5:
            self.combo = 0
            return 2
        else:
            self.combo = 0
            return 1
    
    def update(self):
        if self.state == "playing":
            self.batsman.update()
            self.bowler.update()
            
            if self.gesture_cooldown > 0:
                self.gesture_cooldown -= 1
            
            if self.message_timer > 0:
                self.message_timer -= 1
            
            result = self.ball.update()
            
            if result == "missed":
                self.wickets += 1
                self.balls_faced += 1
                self.combo = 0
                self.show_message("BOWLED! Wicket Lost!", 120)
                
                if self.wickets >= self.max_wickets:
                    self.state = "game_over"
                    if self.score > self.best_score:
                        self.best_score = self.score
                else:
                    self.ball.reset()
                    self.can_bowl = True
                    
            elif result == "scored":
                timing = self.ball.hit_power
                runs = self.calculate_runs(timing)
                self.score += runs
                self.balls_faced += 1
                
                if runs == 6:
                    self.show_message(f"🏏 MAXIMUM! What a shot! Combo: {self.combo}", 120)
                elif runs == 4:
                    self.show_message(f"🎯 FOUR! Brilliant timing! Combo: {self.combo}", 100)
                else:
                    self.show_message(f"{runs} Run{'s' if runs > 1 else ''}! Keep going!", 80)
                
                self.ball.reset()
                self.can_bowl = True
    
    def handle_swing(self):
        if self.state == "playing" and self.ball.is_moving and not self.ball.hit and self.gesture_cooldown == 0:
            distance = abs(self.ball.y - self.batsman.y)
            perfect_distance = 40
            
            if distance <= perfect_distance:
                timing_quality = 1.0 - (distance / perfect_distance) * 0.4
            else:
                timing_quality = max(0.3, 1.0 - (distance / 120))
            
            self.ball.hit_ball(timing_quality)
            self.batsman.swing()
            self.gesture_cooldown = 30
    
    def handle_bowl(self):
        if self.state == "playing" and self.can_bowl and not self.ball.is_moving and self.gesture_cooldown == 0:
            self.ball.bowl()
            self.bowler.bowl()
            self.can_bowl = False
            self.gesture_cooldown = 30
    
    def draw(self, screen):
        self.stadium.draw(screen)
        
        if self.state == "menu":
            self.draw_menu(screen)
        elif self.state == "playing":
            self.draw_playing(screen)
        elif self.state == "game_over":
            self.draw_game_over(screen)
    
    def draw_menu(self, screen):
        # Semi-transparent overlay
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))
        
        title = title_font.render("CRICKET MASTER", True, GOLD)
        title_rect = title.get_rect(center=(WIDTH // 2, 120))
        
        # Title shadow
        shadow = title_font.render("CRICKET MASTER", True, BLACK)
        screen.blit(shadow, (title_rect.x + 4, title_rect.y + 4))
        screen.blit(title, title_rect)
        
        subtitle = text_font.render("Realistic Edition", True, WHITE)
        screen.blit(subtitle, (WIDTH // 2 - 100, 200))
        
        instructions = [
            "🎮 CONTROLS:",
            "",
            "👐 OPEN PALM - Bowl the ball",
            "👍 THUMBS UP - Hit the ball",
            "✌️ VICTORY SIGN - Hit the ball",
            "",
            "KEYBOARD:",
            "SPACE - Bowl  |  UP ARROW - Hit",
            "",
            "⚡ TIMING IS EVERYTHING!",
            "Perfect: 6 runs | Great: 4 runs | Good: 2 runs",
            "",
            "Press SPACE to Start Playing"
        ]
        
        y = 280
        for line in instructions:
            if "Press SPACE" in line:
                text = score_font.render(line, True, GOLD)
            elif line.startswith("🎮") or line.startswith("⚡"):
                text = text_font.render(line, True, ORANGE)
            elif line == "":
                y += 10
                continue
            else:
                text = small_font.render(line, True, WHITE)
            
            text_rect = text.get_rect(center=(WIDTH // 2, y))
            screen.blit(text, text_rect)
            y += 40
    
    def draw_playing(self, screen):
        # Draw game elements
        self.bowler.draw(screen)
        self.ball.draw(screen)
        self.batsman.draw(screen)
        
        # Score panel background
        panel = pygame.Surface((300, 180), pygame.SRCALPHA)
        panel.fill((0, 0, 0, 180))
        screen.blit(panel, (20, 20))
        
        # Score display
        score_text = score_font.render(f"SCORE: {self.score}", True, GOLD)
        screen.blit(score_text, (40, 35))
        
        wickets_text = text_font.render(f"Wickets: {self.wickets}/{self.max_wickets}", True, RED)
        screen.blit(wickets_text, (40, 90))
        
        balls_text = text_font.render(f"Balls: {self.balls_faced}", True, WHITE)
        screen.blit(balls_text, (40, 135))
        
        # Combo display
        if self.combo > 1:
            combo_surface = pygame.Surface((300, 80), pygame.SRCALPHA)
            combo_surface.fill((255, 140, 0, 200))
            screen.blit(combo_surface, (WIDTH // 2 - 150, 30))
            
            combo_text = score_font.render(f"COMBO x{self.combo}!", True, WHITE)
            combo_rect = combo_text.get_rect(center=(WIDTH // 2, 70))
            screen.blit(combo_text, combo_rect)
        
        # Message display
        if self.message_timer > 0:
            msg_color = GOLD if ("MAXIMUM" in self.message or "FOUR" in self.message) else WHITE
            msg_bg_color = ORANGE if ("MAXIMUM" in self.message or "FOUR" in self.message) else RED
            
            msg_text = score_font.render(self.message, True, msg_color)
            msg_rect = msg_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 100))
            
            padding = 30
            bg_surface = pygame.Surface((msg_rect.width + padding * 2, msg_rect.height + padding * 2), pygame.SRCALPHA)
            bg_surface.fill((*msg_bg_color, 200))
            bg_rect = bg_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 100))
            
            screen.blit(bg_surface, bg_rect)
            pygame.draw.rect(screen, msg_color, bg_rect, 4, border_radius=10)
            screen.blit(msg_text, msg_rect)
        
        # Instructions
        if self.can_bowl and not self.ball.is_moving:
            inst_bg = pygame.Surface((350, 50), pygame.SRCALPHA)
            inst_bg.fill((0, 100, 0, 200))
            screen.blit(inst_bg, (WIDTH // 2 - 175, HEIGHT - 60))
            
            inst_text = text_font.render("👐 Open Palm or SPACE to Bowl", True, WHITE)
            inst_rect = inst_text.get_rect(center=(WIDTH // 2, HEIGHT - 35))
            screen.blit(inst_text, inst_rect)
    
    def draw_game_over(self, screen):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))
        
        title = title_font.render("MATCH OVER", True, RED)
        title_rect = title.get_rect(center=(WIDTH // 2, 150))
        screen.blit(title, title_rect)
        
        # Stats panel
        panel = pygame.Surface((600, 400), pygame.SRCALPHA)
        panel.fill((20, 20, 40, 230))
        screen.blit(panel, (WIDTH // 2 - 300, 250))
        pygame.draw.rect(screen, GOLD, (WIDTH // 2 - 300, 250, 600, 400), 3, border_radius=15)
        
        stats = [
            ("Final Score:", f"{self.score}", GOLD),
            ("Best Score:", f"{self.best_score}", YELLOW),
            ("Balls Faced:", f"{self.balls_faced}", WHITE),
            ("Strike Rate:", f"{int((self.score / max(1, self.balls_faced)) * 100)}", WHITE)
        ]
        
        y = 290
        for label, value, color in stats:
            label_text = text_font.render(label, True, WHITE)
            value_text = score_font.render(value, True, color)
            screen.blit(label_text, (WIDTH // 2 - 250, y))
            screen.blit(value_text, (WIDTH // 2 + 50, y - 5))
            y += 80
        
        restart = score_font.render("Press SPACE to Play Again", True, GOLD)
        restart_rect = restart.get_rect(center=(WIDTH // 2, 580))
        screen.blit(restart, restart_rect)
        
        menu = text_font.render("Press ESC for Menu", True, WHITE)
        menu_rect = menu.get_rect(center=(WIDTH // 2, 650))
        screen.blit(menu, menu_rect)

def detect_hand_gesture(frame):
    """
    Returns: 'open_palm', 'thumbs_up', 'victory', or None
    """
    if frame is None:
        return None
    
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(frame_rgb)
    
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            # Get all finger tip and joint positions
            thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
            thumb_ip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_IP]
            
            index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
            index_pip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_PIP]
            index_mcp = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_MCP]
            
            middle_tip = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
            middle_pip = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_PIP]
            
            ring_tip = hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_TIP]
            ring_pip = hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_PIP]
            
            pinky_tip = hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_TIP]
            pinky_pip = hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_PIP]
            
            wrist = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST]
            
            # Check if fingers are extended
            index_extended = index_tip.y < index_pip.y
            middle_extended = middle_tip.y < middle_pip.y
            ring_extended = ring_tip.y < ring_pip.y
            pinky_extended = pinky_tip.y < pinky_pip.y
            thumb_extended = thumb_tip.x > thumb_ip.x or thumb_tip.x < thumb_ip.x  # Thumb direction varies
            
            # OPEN PALM: All fingers extended
            if index_extended and middle_extended and ring_extended and pinky_extended:
                return 'open_palm'
            
            # THUMBS UP: Thumb up, other fingers folded
            thumb_up = thumb_tip.y < thumb_ip.y < wrist.y
            fingers_down = (index_tip.y > index_pip.y and 
                          middle_tip.y > middle_pip.y and
                          ring_tip.y > ring_pip.y and
                          pinky_tip.y > pinky_pip.y)
            
            if thumb_up and fingers_down:
                return 'thumbs_up'
            
            # VICTORY SIGN: Index and middle extended, others folded
            if (index_extended and middle_extended and 
                not ring_extended and not pinky_extended):
                # Check if index and middle are separated (V shape)
                finger_distance = abs(index_tip.x - middle_tip.x)
                if finger_distance > 0.03:  # Threshold for separation
                    return 'victory'
    
    return None

# Main game loop
def main():
    game = Game()
    running = True
    last_gesture = None
    
    print("🏏 Cricket Master - Realistic Edition")
    print("=" * 50)
    print("Camera Controls:")
    print("  👐 Open Palm - Bowl the ball")
    print("  👍 Thumbs Up - Hit the ball")
    print("  ✌️  Victory Sign - Hit the ball")
    print("\nKeyboard Controls:")
    print("  SPACE - Bowl")
    print("  UP ARROW - Hit")
    print("  ESC - Exit/Menu")
    print("=" * 50)
    
    while running:
        clock.tick(FPS)
        
        # Camera input for gesture detection
        frame = None
        current_gesture = None
        
        if camera_available:
            ret, frame = cap.read()
            if ret:
                frame = cv2.flip(frame, 1)
                current_gesture = detect_hand_gesture(frame)
                
                # Detect gesture changes (edge detection)
                if current_gesture and current_gesture != last_gesture:
                    if current_gesture == 'open_palm':
                        game.handle_bowl()
                    elif current_gesture in ['thumbs_up', 'victory']:
                        game.handle_swing()
                
                last_gesture = current_gesture
                
                # Optional: Show camera feed with gesture overlay
                if frame is not None:
                    display_frame = cv2.resize(frame, (200, 150))
                    display_frame = cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB)
                    
                    # Add gesture indicator
                    if current_gesture:
                        gesture_text = current_gesture.replace('_', ' ').title()
                        cv2.putText(display_frame, gesture_text, (10, 30), 
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                    
                    # Convert to pygame surface and display
                    cam_surface = pygame.surfarray.make_surface(display_frame.swapaxes(0, 1))
                    screen.blit(cam_surface, (WIDTH - 220, 20))
        
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if game.state == "game_over":
                        game = Game()
                    else:
                        running = False
                
                if event.key == pygame.K_SPACE:
                    if game.state == "menu":
                        game.state = "playing"
                    elif game.state == "playing":
                        game.handle_bowl()
                    elif game.state == "game_over":
                        game = Game()
                        game.state = "playing"
                
                if event.key == pygame.K_UP:
                    game.handle_swing()
        
        # Update and draw
        game.update()
        game.draw(screen)
        
        pygame.display.flip()
    
    # Cleanup
    if camera_available:
        cap.release()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()