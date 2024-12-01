import pygame
import random
import tkinter as tk
from tkinter import colorchooser

from lightsimul.main import *

GRID_ORIGIN = (20,20)

# Function to handle click events
def bulb_clicked(bulb_pos):
    col = bulb_pos[0]
    row = bulb_pos[1]

    # Open color picker
    root = tk.Tk()
    root.withdraw()  # Hide the main Tkinter window
    color_code = colorchooser.askcolor(title="Choose a color")[0]  # Get RGB from color picker
    root.destroy()
    if color_code:
        # Convert RGB to 2-digit hex value
        new_hex = rgb_to_hex(color_code)
        grid[col][row] = new_hex

def main():
    global grid

    # Initialize pygame
    pygame.init()

    # Create the initial 2D array (20x20) with random 2-digit hex values
    grid = [[f"{random.randint(0, 255):02X}" for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
    
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
                bulb_pos = handle_click(event.pos, GRID_ORIGIN)
                print(bulb_pos)
                bulb_clicked(bulb_pos)
        
        # Clear screen
        screen.fill((0, 0, 0))
        
        # Draw updated grid
        draw_grid(screen, grid, GRID_ORIGIN)
        
        # Update the display
        pygame.display.flip()
        
        # Cap the frame rate
        clock.tick(FPS)
    
    pygame.quit()

main()