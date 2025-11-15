import pygame
import random
import math
from enum import Enum

pygame.init()

# Screen dimensions
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 700
FPS = 60

# Colors
COLOR_BG = (10, 20, 40)
COLOR_GRASS = (20, 120, 40)
COLOR_PITCH = (180, 160, 100)
COLOR_WHITE = (255, 255, 255)
COLOR_RED = (220, 50, 50)
COLOR_YELLOW = (255, 220, 0)
COLOR_GREEN = (50, 220, 100)
COLOR_BLUE = (100, 180, 255)
COLOR_GOLD = (255, 215, 0)
COLOR_PURPLE = (200, 100, 255)

class GameState(Enum):
    MENU = 1
    PLAYING = 2
    BATTING_READY = 3
    BALL_IN_FLIGHT = 4
    HIT_RESULT = 5
    GAME_OVER = 6

class Ball:
    def __init__(self, start_x, start_y):
        self.x = start_x
        self.y = start_y
        self.radius = 8
        self.velocity_x = 0
        self.velocity_y = 0
        self.spin = 0

    def update(self):
        self.x += self.velocity_x
        self.y += self.velocity_y
        self.spin += 2

    def draw(self, screen):
        # Draw ball with shading
        pygame.draw.circle(screen, (200, 50, 50), (int(self.x), int(self.y)), self.radius)
        # Seam effect
        offset = math.sin(math.radians(self.spin)) * 2
        pygame.draw.line(screen, (100, 100, 100), 
                        (int(self.x - 8), int(self.y + offset)), 
                        (int(self.x + 8), int(self.y - offset)), 2)

class Batsman:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 15
        self.height = 50
        self.bat_angle = -30
        self.swinging = False
        self.swing_progress = 0

    def update(self):
        if self.swinging:
            self.swing_progress += 8
            self.bat_angle = -30 + (self.swing_progress / 100) * 120
            if self.swing_progress >= 100:
                self.swinging = False

    def swing_bat(self):
        self.swinging = True
        self.swing_progress = 0
        self.bat_angle = -30

    def draw(self, screen):
        # Draw batsman body
        pygame.draw.ellipse(screen, COLOR_YELLOW, (self.x - 8, self.y - 15, 16, 20))
        # Head
        pygame.draw.circle(screen, COLOR_YELLOW, (int(self.x), int(self.y - 20)), 6)
        # Legs
        pygame.draw.line(screen, COLOR_WHITE, (int(self.x - 4), int(self.y + 5)), 
                        (int(self.x - 6), int(self.y + 20)), 3)
        pygame.draw.line(screen, COLOR_WHITE, (int(self.x + 4), int(self.y + 5)), 
                        (int(self.x + 6), int(self.y + 20)), 3)
        
        # Draw bat
        bat_length = 50
        angle_rad = math.radians(self.bat_angle)
        bat_end_x = self.x + bat_length * math.cos(angle_rad)
        bat_end_y = self.y + bat_length * math.sin(angle_rad)
        pygame.draw.line(screen, COLOR_WHITE, (self.x, self.y), 
                        (bat_end_x, bat_end_y), 8)

    def get_bat_position(self):
        angle_rad = math.radians(self.bat_angle)
        bat_length = 50
        return (self.x + bat_length * math.cos(angle_rad), 
                self.y + bat_length * math.sin(angle_rad))

class Bowler:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.bowling_progress = 0
        self.is_bowling = False

    def start_bowling(self):
        self.is_bowling = True
        self.bowling_progress = 0

    def update(self):
        if self.is_bowling and self.bowling_progress < 100:
            self.bowling_progress += 6
        if self.bowling_progress >= 100:
            self.is_bowling = False

    def draw(self, screen):
        progress = self.bowling_progress / 100 if self.is_bowling else 0
        
        # Body
        body_x = self.x - 30 + (progress * 40)
        pygame.draw.ellipse(screen, COLOR_BLUE, (body_x - 8, self.y - 20, 16, 25))
        
        # Head
        pygame.draw.circle(screen, COLOR_BLUE, (int(body_x), int(self.y - 25)), 6)
        
        # Bowling arm - animated
        arm_angle = -45 + (progress * 180)
        arm_rad = math.radians(arm_angle)
        arm_end_x = body_x + 30 * math.cos(arm_rad)
        arm_end_y = self.y - 15 + 30 * math.sin(arm_rad)
        pygame.draw.line(screen, COLOR_BLUE, (body_x, self.y - 15), 
                        (arm_end_x, arm_end_y), 5)
        
        # Legs
        leg_offset = 15 + (progress * 20)
        pygame.draw.line(screen, COLOR_WHITE, (body_x - 4, self.y + 5), 
                        (body_x - 6 - leg_offset, self.y + 25), 3)

class CricketGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Cricket Master - Timing is Everything")
        self.clock = pygame.time.Clock()
        self.font_large = pygame.font.Font(None, 72)
        self.font_medium = pygame.font.Font(None, 48)
        self.font_small = pygame.font.Font(None, 32)
        self.font_tiny = pygame.font.Font(None, 24)
        
        self.state = GameState.MENU
        self.reset_game()

    def reset_game(self):
        self.batsman = Batsman(SCREEN_WIDTH - 150, SCREEN_HEIGHT - 100)
        self.bowler = Bowler(150, SCREEN_HEIGHT - 150)
        self.ball = None
        self.score = 0
        self.wickets = 0
        self.balls_faced = 0
        self.last_runs = 0
        self.result_timer = 0
        self.difficulty = 1.0
        self.state = GameState.BATTING_READY
        self.next_bowl()

    def next_bowl(self):
        self.balls_faced += 1
        self.state = GameState.BATTING_READY
        self.last_runs = 0
        self.result_timer = 0
        self.difficulty = 1.0 + (self.balls_faced // 6) * 0.1
        self.bowler.start_bowling()

    def bowl_ball(self):
        self.ball = Ball(self.bowler.x + 50, self.bowler.y - 20)
        ball_speed = 8 + self.difficulty
        self.ball.velocity_x = ball_speed
        self.ball.velocity_y = 2
        self.state = GameState.BALL_IN_FLIGHT

    def check_bat_ball_collision(self):
        if not self.ball:
            return False
        
        bat_x, bat_y = self.batsman.get_bat_position()
        dx = self.ball.x - bat_x
        dy = self.ball.y - bat_y
        distance = math.sqrt(dx**2 + dy**2)
        
        return distance < 25

    def calculate_runs(self, timing_quality):
        """Calculate runs based on timing quality (0-1, where 1 is perfect)"""
        if timing_quality < 0.3:
            return 0
        elif timing_quality < 0.5:
            return 1
        elif timing_quality < 0.65:
            return 2
        elif timing_quality < 0.8:
            return 3
        elif timing_quality < 0.9:
            return 4
        else:
            return 6

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if event.type == pygame.KEYDOWN:
                if self.state == GameState.MENU:
                    if event.key == pygame.K_SPACE:
                        self.reset_game()
                
                elif self.state == GameState.BATTING_READY:
                    if event.key == pygame.K_SPACE:
                        self.bowl_ball()
                
                elif self.state == GameState.BALL_IN_FLIGHT:
                    if event.key == pygame.K_SPACE:
                        # Player attempts to hit
                        if self.check_bat_ball_collision():
                            # Calculate timing quality based on ball position
                            # Perfect timing when ball is at center of screen
                            distance_from_center = abs(self.ball.x - (SCREEN_WIDTH * 0.6))
                            timing_quality = max(0, 1 - (distance_from_center / 300))
                            
                            self.last_runs = self.calculate_runs(timing_quality)
                            self.score += self.last_runs
                            self.batsman.swing_bat()
                            
                            # Ball goes away
                            self.ball.velocity_x = -5
                            self.ball.velocity_y = -8
                            
                            self.state = GameState.HIT_RESULT
                            self.result_timer = 60
                        else:
                            # Missed
                            self.last_runs = 0
                            self.batsman.swing_bat()
                            self.state = GameState.HIT_RESULT
                            self.result_timer = 60
                
                elif self.state == GameState.HIT_RESULT:
                    if event.key == pygame.K_SPACE:
                        if self.balls_faced >= 20:
                            self.state = GameState.GAME_OVER
                        else:
                            self.next_bowl()
                
                elif self.state == GameState.GAME_OVER:
                    if event.key == pygame.K_SPACE:
                        self.reset_game()
        
        return True

    def update(self):
        if self.state == GameState.BALL_IN_FLIGHT:
            self.bowler.update()
            self.ball.update()
            self.batsman.update()
        
        elif self.state == GameState.BATTING_READY:
            self.bowler.update()
            if self.bowler.bowling_progress >= 70:
                if not self.ball:
                    self.bowl_ball()

    def draw_pitch(self):
        # Background
        self.screen.fill(COLOR_BG)
        
        # Grass
        pygame.draw.rect(self.screen, COLOR_GRASS, (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
        
        # Cricket pitch
        pitch_y = SCREEN_HEIGHT - 120
        pygame.draw.rect(self.screen, COLOR_PITCH, (100, pitch_y - 5, SCREEN_WIDTH - 200, 80))
        
        # Crease lines
        pygame.draw.line(self.screen, COLOR_WHITE, (100, pitch_y), 
                        (SCREEN_WIDTH - 100, pitch_y), 2)
        pygame.draw.line(self.screen, COLOR_WHITE, (100, pitch_y + 75), 
                        (SCREEN_WIDTH - 100, pitch_y + 75), 2)
        
        # Stumps (wickets)
        stump_x = SCREEN_WIDTH - 150
        stump_y = pitch_y - 40
        for i in range(3):
            pygame.draw.line(self.screen, COLOR_WHITE, 
                            (stump_x - 10 + i * 10, stump_y), 
                            (stump_x - 10 + i * 10, stump_y + 35), 3)
        pygame.draw.line(self.screen, COLOR_WHITE, 
                        (stump_x - 15, stump_y + 35), 
                        (stump_x + 15, stump_y + 35), 2)

    def draw_ui(self):
        # Score board
        score_text = self.font_large.render(f"Score: {self.score}", True, COLOR_GOLD)
        self.screen.blit(score_text, (20, 20))
        
        # Balls faced
        balls_text = self.font_small.render(f"Balls: {self.balls_faced}/20", True, COLOR_BLUE)
        self.screen.blit(balls_text, (20, 100))
        
        # Difficulty indicator
        difficulty_text = self.font_tiny.render(f"Pace: {self.difficulty:.1f}x", True, COLOR_PURPLE)
        self.screen.blit(difficulty_text, (20, 150))

    def draw(self):
        self.draw_pitch()
        
        if self.state == GameState.MENU:
            title = self.font_large.render("CRICKET MASTER", True, COLOR_GOLD)
            subtitle = self.font_medium.render("Timing is Everything", True, COLOR_BLUE)
            instruction = self.font_small.render("Press SPACE to start", True, COLOR_WHITE)
            
            self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 150))
            self.screen.blit(subtitle, (SCREEN_WIDTH // 2 - subtitle.get_width() // 2, 250))
            self.screen.blit(instruction, (SCREEN_WIDTH // 2 - instruction.get_width() // 2, 400))
        
        else:
            self.bowler.draw(self.screen)
            self.batsman.draw(self.screen)
            
            if self.ball:
                self.ball.draw(self.screen)
            
            self.draw_ui()
            
            # Timing indicator
            if self.state == GameState.BALL_IN_FLIGHT:
                indicator_width = 200
                indicator_x = SCREEN_WIDTH // 2 - indicator_width // 2
                pygame.draw.rect(self.screen, COLOR_WHITE, 
                               (indicator_x, SCREEN_HEIGHT - 50, indicator_width, 30), 2)
                
                # Green zone for perfect timing
                green_start = indicator_x + 80
                green_width = 40
                pygame.draw.rect(self.screen, COLOR_GREEN, 
                               (green_start, SCREEN_HEIGHT - 50, green_width, 30))
                
                # Ball position indicator
                ball_relative = (self.ball.x - 100) / (SCREEN_WIDTH - 200)
                indicator_pos = indicator_x + indicator_width * ball_relative
                pygame.draw.rect(self.screen, COLOR_YELLOW, 
                               (indicator_pos - 5, SCREEN_HEIGHT - 50, 10, 30))
                
                press_text = self.font_tiny.render("SPACE to hit", True, COLOR_YELLOW)
                self.screen.blit(press_text, (SCREEN_WIDTH // 2 - press_text.get_width() // 2, 
                                            SCREEN_HEIGHT - 85))
            
            elif self.state == GameState.HIT_RESULT:
                if self.last_runs == 0:
                    result_text = self.font_medium.render("MISS! 0 RUNS", True, COLOR_RED)
                elif self.last_runs == 1:
                    result_text = self.font_medium.render("Single! +1", True, COLOR_BLUE)
                elif self.last_runs == 2:
                    result_text = self.font_medium.render("Two! +2", True, COLOR_BLUE)
                elif self.last_runs == 3:
                    result_text = self.font_medium.render("Three! +3", True, COLOR_GREEN)
                elif self.last_runs == 4:
                    result_text = self.font_medium.render("FOUR! +4", True, COLOR_GOLD)
                else:
                    result_text = self.font_large.render("SIX! +6", True, COLOR_GOLD)
                
                self.screen.blit(result_text, (SCREEN_WIDTH // 2 - result_text.get_width() // 2, 300))
                
                next_text = self.font_small.render("Press SPACE for next ball", True, COLOR_WHITE)
                self.screen.blit(next_text, (SCREEN_WIDTH // 2 - next_text.get_width() // 2, 380))
            
            elif self.state == GameState.BATTING_READY:
                ready_text = self.font_medium.render("Ready to face the bowler?", True, COLOR_BLUE)
                self.screen.blit(ready_text, (SCREEN_WIDTH // 2 - ready_text.get_width() // 2, 300))
                
                press_text = self.font_small.render("Press SPACE to bowl", True, COLOR_WHITE)
                self.screen.blit(press_text, (SCREEN_WIDTH // 2 - press_text.get_width() // 2, 380))
            
            elif self.state == GameState.GAME_OVER:
                game_over_text = self.font_large.render("GAME OVER", True, COLOR_RED)
                final_score = self.font_medium.render(f"Final Score: {self.score}", True, COLOR_GOLD)
                play_again = self.font_small.render("Press SPACE to play again", True, COLOR_WHITE)
                
                self.screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, 200))
                self.screen.blit(final_score, (SCREEN_WIDTH // 2 - final_score.get_width() // 2, 300))
                self.screen.blit(play_again, (SCREEN_WIDTH // 2 - play_again.get_width() // 2, 400))
        
        pygame.display.flip()

    def run(self):
        running = True
        while running:
            running = self.handle_input()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()

if __name__ == "__main__":
    game = CricketGame()
    game.run()
