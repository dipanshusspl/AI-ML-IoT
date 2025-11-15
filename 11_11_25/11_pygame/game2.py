import pygame
import random
import sys

# Initialize pygame
pygame.init()

# Game window setup
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("🚗 Dodge the Blocks!")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED   = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE  = (0, 150, 255)

# Clock for FPS
clock = pygame.time.Clock()

# Player setup
player_size = 50
player_x = WIDTH // 2
player_y = HEIGHT - player_size - 10
player_speed = 10

# Block setup
block_size = 50
block_list = []
block_speed = 5

# Score setup
score = 0
font = pygame.font.SysFont("comicsansms", 36)

# Sounds (optional)
pygame.mixer.init()
try:
    beep = pygame.mixer.Sound(pygame.mixer.get_init() and pygame.mixer.Sound)
except Exception:
    beep = None

def drop_blocks(block_list):
    # Create new falling blocks at random positions
    delay = random.random()
    if len(block_list) < 10 and delay < 0.1:
        x_pos = random.randint(0, WIDTH - block_size)
        y_pos = 0
        block_list.append([x_pos, y_pos])

def draw_blocks(block_list):
    for block in block_list:
        pygame.draw.rect(screen, RED, (block[0], block[1], block_size, block_size))

def update_block_positions(block_list, score):
    # Move blocks down the screen
    for block in block_list[:]:
        if block[1] >= 0 and block[1] < HEIGHT:
            block[1] += block_speed
        else:
            block_list.remove(block)
            score += 1
    return score

def collision_check(block_list, player_x, player_y):
    for block in block_list:
        if (
            block[0] < player_x < block[0] + block_size
            or block[0] < player_x + player_size < block[0] + block_size
        ):
            if (
                block[1] < player_y < block[1] + block_size
                or block[1] < player_y + player_size < block[1] + block_size
            ):
                return True
    return False

# Main game loop
running = True
while running:
    screen.fill(BLACK)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # Key press movement
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and player_x > 0:
        player_x -= player_speed
    if keys[pygame.K_RIGHT] and player_x < WIDTH - player_size:
        player_x += player_speed

    # Drop and move blocks
    drop_blocks(block_list)
    score = update_block_positions(block_list, score)
    draw_blocks(block_list)

    # Draw player
    pygame.draw.rect(screen, BLUE, (player_x, player_y, player_size, player_size))

    # Collision
    if collision_check(block_list, player_x, player_y):
        pygame.draw.rect(screen, RED, (player_x, player_y, player_size, player_size))
        game_over_text = font.render("💥 Game Over!", True, (255, 255, 0))
        screen.blit(game_over_text, (WIDTH // 2 - 100, HEIGHT // 2 - 30))
        pygame.display.update()
        pygame.time.wait(2000)
        running = False
        continue

    # Increase difficulty over time
    if score % 20 == 0 and score != 0:
        block_speed = min(block_speed + 0.01, 15)

    # Show score
    score_text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (10, 10))

    pygame.display.update()
    clock.tick(30)
