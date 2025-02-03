import pygame
from tango import TangoGrid
from common.ui import Button, make_ui

# Initialize Pygame
pygame.init()

# Set up display
WIDTH, HEIGHT = 800, 80 * 6
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("LinkedIn WFC")

tango_grid = TangoGrid(6, 6)

# UI
ui = make_ui(
    Button(500, 380, 280, 40, "Solve", (100, 200, 100), tango_grid.update_superpositions),
    Button(500, 420, 280, 40, "Reset", (100, 100, 100), tango_grid.reset),
    Button(500, 20, 140, 40, "Place Sun", (200, 200, 100), lambda: setattr(tango_grid, "edit_mode", "SUN")),
    Button(640, 20, 140, 40, "Place Moon", (100, 100, 200), lambda: setattr(tango_grid, "edit_mode", "MOON")),
    Button(500, 100, 280, 40, "Add equality constraint", (100, 200, 200), lambda: setattr(tango_grid, "edit_mode", "EQUALS_A")),
    Button(500, 140, 280, 40, "Add opposite constraint", (200, 100, 200), lambda: setattr(tango_grid, "edit_mode", "OPPOSITE_A")),
    Button(500, 180, 280, 40, "Remove constraints", (200, 100, 100), lambda: setattr(tango_grid, "equals", []) or setattr(tango_grid, "opposites", []))
)

# Main loop
running = True
while running:
    keyboard = pygame.key.get_pressed()
    mouse_pos = pygame.mouse.get_pos()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            tango_grid.on_click(*mouse_pos, keyboard)
            ui.on_click(mouse_pos)

    if keyboard[pygame.K_r]:
        tango_grid.update_superpositions()
    
    # Fill screen with a color (optional)
    screen.fill((30, 30, 30))
    tango_grid.draw(screen)
    ui.draw(screen, mouse_pos)
    
    # Update display
    pygame.display.flip()

# Quit Pygame
pygame.quit()
