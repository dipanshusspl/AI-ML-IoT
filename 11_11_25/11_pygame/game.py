import pygame
import sys

# Initialize pygame
pygame.init()

# Create a window
screen = pygame.display.set_mode((600, 400))
pygame.display.set_caption("My First Pygame Window")

# Colors
BLUE = (0, 150, 255)
WHITE = (255, 255, 255)

# Circle position
x, y = 300, 200

# Game loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # Move circle with arrow keys
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        x -= 5
    if keys[pygame.K_RIGHT]:
        x += 5
    if keys[pygame.K_UP]:
        y -= 5
    if keys[pygame.K_DOWN]:
        y += 5

    # Fill background
    screen.fill(WHITE)

    # Draw circle
    pygame.draw.circle(screen, BLUE, (x, y), 30)

    # Update display
    pygame.display.flip()
