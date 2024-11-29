import pygame
import random

# Initialize pygame
pygame.init()

# Constants
GRID_SIZE = 20
CELL_SIZE = 30
WIDTH = GRID_SIZE * CELL_SIZE
HEIGHT = GRID_SIZE * CELL_SIZE
FPS = 30

# Create the initial 2D array (20x20) with random 2-digit hex values
grid = [[f"{random.randint(0, 255):02X}" for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]

# Function to convert 2-digit hex to RGB color
def hex_to_rgb(hex_value):
    try:
        intensity = int(hex_value, 16)  # Convert 2-digit hex to integer
    except:
        intensity = 0
    return (intensity, intensity, intensity)  # Use intensity for R, G, and B

# Function to draw the grid
def draw_grid(surface, grid):
    for row_idx, row in enumerate(grid):
        for col_idx, hex_value in enumerate(row):
            rgb_color = hex_to_rgb(hex_value)  # Convert 2-digit hex to RGB
            # Swap row_idx and col_idx for correct orientation
            rect = pygame.Rect(row_idx * CELL_SIZE, col_idx * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(surface, rgb_color, rect)

def main():
    global grid
    
    # Create the game window
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Dynamic Grid Color Display")
    
    # Main game loop
    running = True
    clock = pygame.time.Clock()
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        '''
        # Example update: Randomly change a grid cell every frame
        rand_row = random.randint(0, GRID_SIZE - 1)
        rand_col = random.randint(0, GRID_SIZE - 1)
        new_value = f"{random.randint(0, 255):02X}"  # Generate new 2-digit hex value
        grid[rand_row][rand_col] = new_value
        '''
        
        # Clear screen
        screen.fill((0, 0, 0))
        
        # Draw updated grid
        draw_grid(screen, grid)
        
        # Update the display
        pygame.display.flip()
        
        # Cap the frame rate
        clock.tick(FPS)
    
    pygame.quit()
