import pygame
import random
import tkinter as tk
from tkinter import colorchooser
import asyncio

from lightsimul.main import *
from lightslib.LightsController import LightsController

controller = LightsController()

# Grid origin starts below the toolbar
GRID_SIZE = 20
WIDTH = 600
HEIGHT = 650
FPS = 60
toolbar_height = 50  # Height of the toolbar
grid_origin = (0, toolbar_height)  # Start the grid below the toolbar

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

def reset_grid():
    global grid
    grid = [["FE" for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]

async def send_config():
    global grid
    await controller.drawFrame(grid)

async def handle_toolbar_click(pos):
    # Check if the click was within a button's area
    if 0 <= pos[1] <= toolbar_height:  # Click is within the toolbar's height
        if 10 <= pos[0] <= 110:  # Button 1 (e.g., Reset Grid)
            reset_grid()
        elif 120 <= pos[0] <= 220:  # Button 2 (e.g., another action)
            await send_config()

def draw_rounded_rect(screen, color, rect, radius=10):
    """Draw a rectangle with rounded corners"""
    x, y, width, height = rect
    pygame.draw.rect(screen, color, (x + radius, y, width - 2 * radius, height))
    pygame.draw.rect(screen, color, (x, y + radius, width, height - 2 * radius))
    pygame.draw.circle(screen, color, (x + radius, y + radius), radius)
    pygame.draw.circle(screen, color, (x + width - radius, y + radius), radius)
    pygame.draw.circle(screen, color, (x + radius, y + height - radius), radius)
    pygame.draw.circle(screen, color, (x + width - radius, y + height - radius), radius)

def draw_toolbar(screen, mouse_pos):
    # Draw the toolbar background
    pygame.draw.rect(screen, (100, 100, 100), (0, 0, WIDTH, toolbar_height))  # Background of toolbar
    
    # Draw buttons with rounded corners
    button_color = (200, 0, 0)
    hover_color = (255, 50, 50)
    
    button1_rect = pygame.Rect(10, 10, 100, 30)
    button2_rect = pygame.Rect(120, 10, 100, 30)
    
    if button1_rect.collidepoint(mouse_pos):
        draw_rounded_rect(screen, hover_color, button1_rect)
    else:
        draw_rounded_rect(screen, button_color, button1_rect)

    if button2_rect.collidepoint(mouse_pos):
        draw_rounded_rect(screen, hover_color, button2_rect)
    else:
        draw_rounded_rect(screen, (0, 200, 0), button2_rect)
    
    # Add text labels on buttons, centered
    font = pygame.font.Font(None, 24)
    
    # Button 1 text
    text = font.render("Reset Grid", True, (255, 255, 255))
    text_rect = text.get_rect(center=button1_rect.center)  # Center the text
    screen.blit(text, text_rect)

    # Button 2 text
    text = font.render("Send Config", True, (255, 255, 255))
    text_rect = text.get_rect(center=button2_rect.center)  # Center the text
    screen.blit(text, text_rect)

async def main():
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
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.pos[1] <= toolbar_height:
                    await handle_toolbar_click(event.pos)  # Handle toolbar button clicks
                else:
                    bulb_pos = handle_click(event.pos, grid_origin)
                    print(bulb_pos)
                    bulb_clicked(bulb_pos)
        
        # Clear screen
        screen.fill((30, 30, 30)) # Dark gray bg color
        
        # Draw toolbar with hover effect
        draw_toolbar(screen, mouse_pos)

        # Draw updated grid
        draw_grid(screen, grid, grid_origin)
        
        # Update the display
        pygame.display.flip()
        
        # Cap the frame rate
        clock.tick(FPS)
    
    pygame.quit()

asyncio.run(main())
