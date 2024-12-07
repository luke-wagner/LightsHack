import pygame
import random
import tkinter as tk
from tkinter import colorchooser

# Constants
GRID_SIZE = 20
CELL_SIZE = 30
WIDTH = GRID_SIZE * CELL_SIZE
HEIGHT = GRID_SIZE * CELL_SIZE
FPS = 30

# Create the initial 2D array (20x20) with random 2-digit hex values
grid = [[f"{random.randint(0, 255):02X}" for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
grid_origin = (0,0) # Default to 0,0 but this can be changed from outside this module

# Function to interpolate between two colors
def interpolate_color(start_color, end_color, fraction):
    return tuple(
        int(start + (end - start) * fraction)
        for start, end in zip(start_color, end_color)
    )

# Function to map 2-digit value to RGB based on the new color data points
def hex_to_rgb(hex_value):
    try:
        value = int(hex_value, 16)  # Convert 2-digit hex to integer
    except ValueError:
        return (0, 0, 0)  # Default to off if invalid input

    # Special cases
    if value == 0xFE:  # "off"
        return (0, 0, 0)
    elif value == 0xFF:  # "white"
        return (255, 255, 255)

    # Data points for mapping
    data_points = {
        0x00: (255, 0, 0), 0x07: (252, 136, 59), 0x10: (251, 250, 110),
        0x17: (218, 240, 91), 0x20: (178, 240, 83), 0x27: (139, 243, 69),
        0x30: (18, 245, 79), 0x37: (0, 247, 78), 0x40: (0, 255, 182),
        0x47: (0, 255, 255), 0x50: (0, 196, 250), 0x57: (0, 174, 254),
        0x60: (0, 137, 251), 0x67: (0, 117, 253), 0x70: (0, 64, 253),
        0x77: (0, 1, 255), 0x80: (91, 0, 255), 0x87: (103, 0, 255),
        0x90: (146, 0, 255), 0x97: (164, 0, 254), 0xA0: (190, 0, 254),
        0xA7: (255, 0, 253), 0xB0: (255, 0, 191), 0xB7: (255, 80, 14),
        0xC0: (250, 198, 85), 0xC7: (245, 237, 91), 0xD0: (203, 236, 83),
        0xD7: (168, 239, 93), 0xE0: (106, 242, 95), 0xE7: (14, 245, 93),
        0xF0: (0, 249, 85), 0xF7: (0, 242, 211), 0xFC: (0, 234, 243),
        0xFD: (252, 181, 141), 0xFE: (0, 0, 0), 0xFF: (255, 255, 255),
    }

    # Find the two closest data points
    keys = sorted(data_points.keys())
    for i in range(len(keys) - 1):
        if keys[i] <= value <= keys[i + 1]:
            start_key, end_key = keys[i], keys[i + 1]
            start_color, end_color = data_points[start_key], data_points[end_key]
            fraction = (value - start_key) / (end_key - start_key)
            return interpolate_color(start_color, end_color, fraction)

    return (0, 0, 0)  # Fallback for unexpected cases

# Function to find the closest 2-digit hex value for an RGB color
def rgb_to_hex(color_code):
    r, g, b = color_code

    # Special cases
    if (r, g, b) == (0, 0, 0):  # "off"
        return "FE"
    elif (r, g, b) == (255, 255, 255):  # "white"
        return "FF"

    # Data points for reverse mapping
    data_points = {
        0x00: (255, 0, 0), 0x07: (252, 136, 59), 0x10: (251, 250, 110),
        0x17: (218, 240, 91), 0x20: (178, 240, 83), 0x27: (139, 243, 69),
        0x30: (18, 245, 79), 0x37: (0, 247, 78), 0x40: (0, 255, 182),
        0x47: (0, 255, 255), 0x50: (0, 196, 250), 0x57: (0, 174, 254),
        0x60: (0, 137, 251), 0x67: (0, 117, 253), 0x70: (0, 64, 253),
        0x77: (0, 1, 255), 0x80: (91, 0, 255), 0x87: (103, 0, 255),
        0x90: (146, 0, 255), 0x97: (164, 0, 254), 0xA0: (190, 0, 254),
        0xA7: (255, 0, 253), 0xB0: (255, 0, 191), 0xB7: (255, 80, 14),
        0xC0: (250, 198, 85), 0xC7: (245, 237, 91), 0xD0: (203, 236, 83),
        0xD7: (168, 239, 93), 0xE0: (106, 242, 95), 0xE7: (14, 245, 93),
        0xF0: (0, 249, 85), 0xF7: (0, 242, 211), 0xFC: (0, 234, 243),
        0xFD: (252, 181, 141), 0xFE: (0, 0, 0), 0xFF: (255, 255, 255),
    }

    # Find the closest match
    closest_key = min(data_points, key=lambda k: sum((a - b) ** 2 for a, b in zip(data_points[k], color_code)))
    return f"{closest_key:02X}"

# Function to draw the grid with circles
def draw_grid(surface, grid, gridOrigin):
    for row_idx, row in enumerate(grid):
        for col_idx, hex_value in enumerate(row):
            rgb_color = hex_to_rgb(hex_value)  # Convert 2-digit hex to RGB
            # Calculate the center of the circle
            center_x = row_idx * CELL_SIZE + CELL_SIZE // 2 + gridOrigin[0]
            center_y = col_idx * CELL_SIZE + CELL_SIZE // 2 + gridOrigin[1]
            radius = CELL_SIZE // 2 - 2  # Adjust for spacing
            pygame.draw.circle(surface, rgb_color, (center_x, center_y), radius)

# Function to handle click events
def handle_click(pos, gridOrigin):
    col = (pos[0] - gridOrigin[0]) // CELL_SIZE
    row = (pos[1] - gridOrigin[1]) // CELL_SIZE
    if 0 <= row < GRID_SIZE and 0 <= col < GRID_SIZE:
        return (col, row)
    else:
        return None

def run_simul():
    global pygame

    # Initialize pygame
    pygame.init()
    
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
            elif event.type == pygame.MOUSEBUTTONDOWN:
                handle_click(event.pos, grid_origin)
                pass
        
        # Clear screen
        screen.fill((0, 0, 0))
        
        # Draw updated grid
        draw_grid(screen, grid, grid_origin)
        
        # Update the display
        pygame.display.flip()
        
        # Cap the frame rate
        clock.tick(FPS)
    
    pygame.quit()