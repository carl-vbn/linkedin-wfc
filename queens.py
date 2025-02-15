import pygame
from common.grid import Grid, State
from common.ui import Button, make_ui
import common.symbols as symbols
import sys

class EmptyState(State):
    def __init__(self):
        super().__init__('EMPTY', symbols.EMPTY)

    def is_possible(self, grid, cell_x, cell_y):
        # Check if all other cells of this color are empty
        this_cell = grid.cells[cell_x][cell_y]
        cell_color = this_cell.bg_col
        all_empty = True
        for cell in grid.iter_cells():
            if cell == this_cell:
                continue

            if cell.bg_col == cell_color and not cell.must_be(self.name):
                all_empty = False
                break

        if all_empty:
            return False

        return True

class CrownState(State):
    def __init__(self):
        super().__init__('QUEEN', symbols.CROWN)

    def is_possible(self, grid, cell_x, cell_y):
        # Check if there is a queen in the same row or column
        for x in range(grid.width):
            if x != cell_x and grid.must_be(x, cell_y, self.name):
                return False
        
        for y in range(grid.height):
            if y != cell_y and grid.must_be(cell_x, y, self.name):
                return False
            
        # Check if there is a queen in the 8 cells around this cell
        for x in range(cell_x - 1, cell_x + 2):
            for y in range(cell_y - 1, cell_y + 2):
                if x == cell_x and y == cell_y:
                    continue
                
                if grid.must_be(x, y, self.name):
                    return False

        # Check if there is a queen on a cell with the same color
        this_cell = grid.cells[cell_x][cell_y]
        cell_color = this_cell.bg_col
        for cell in grid.iter_cells():
            if cell == this_cell:
                continue

            if cell.bg_col == cell_color and cell.must_be(self.name):
                return False
            
        return True


CROWN = CrownState()
EMPTY = EmptyState()

class QueensGrid(Grid):
    def __init__(self, width, height):
        super().__init__(width, height, 80, (200, 200, 200), (100, 100, 100), [CROWN, EMPTY])
        self.paint_color = None

    def clone(self):
        copy = QueensGrid(self.width, self.height)

        copy.is_original = False

        for x in range(self.width):
            for y in range(self.height):
                copy.cells[x][y].states = [state for state in self.cells[x][y].states]
                copy.cells[x][y].bg_col = self.cells[x][y].bg_col
        
        return copy
    
    def set_paint_color(self, color):
        self.paint_color = color
        self.edit_mode = None

    def set_edit_mode(self, mode):
        self.edit_mode = mode
        self.paint_color = None
    
    def on_cell_click(self, x, y, keyboard):
        if self.paint_color is not None:
            self.cells[x][y].bg_col = self.paint_color

        elif self.edit_mode == 'CROWNS':
            self.cells[x][y].states = [CROWN]

        elif self.edit_mode == 'EMPTY':
            self.cells[x][y].states = [EMPTY]

        return super().on_cell_click(x, y, keyboard)

GRID_SIZE = 9

# Initialize Pygame
pygame.init()

# Set up display
WIDTH, HEIGHT = 80 * GRID_SIZE + 320, 80 * GRID_SIZE
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("LinkedIn WFC")

queens_grid = QueensGrid(GRID_SIZE, GRID_SIZE)

queens_colors = {
    'RED': (255, 0, 0),
    'BLUE': (0, 0, 255),
    'GREEN': (0, 255, 0),
    'YELLOW': (255, 255, 0),
    'PURPLE': (255, 0, 255),
    'ORANGE': (255, 165, 0),
    'CYAN': (0, 255, 255),
    'PINK': (255, 192, 203),
    'BROWN': (165, 42, 42),
}

if len(sys.argv) == 2:
    x, y = 0, 0
    color_list = list(queens_colors.values())
    with open('configs/queens/'+sys.argv[1], 'r') as f:
        for line in f:
            for col_idx in line.split():
                queens_grid.cells[x][y].bg_col = color_list[int(col_idx)]
                x += 1
            x = 0
            y += 1

# UI
ui = make_ui(
    Button(GRID_SIZE * 80 + 20, 460, 280, 40, "Solve", (100, 200, 100), queens_grid.update_superpositions),
    Button(GRID_SIZE * 80 + 20, 500, 280, 40, "Reset", (100, 100, 100), queens_grid.reset),
    Button(GRID_SIZE * 80 + 20, 400, 140, 40, "Crown", (200, 200, 100), lambda: queens_grid.set_edit_mode('CROWNS')),
    Button(GRID_SIZE * 80 + 160, 400, 140, 40, "Empty", (100, 100, 200), lambda: queens_grid.set_edit_mode('EMPTY')),
    *[Button(GRID_SIZE * 80 + 20, 20 + 40 * i, 280, 40, color, queens_colors[color], lambda color=color: queens_grid.set_paint_color(queens_colors[color])) for i, color in enumerate(queens_colors)]
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
            queens_grid.on_click(*mouse_pos, keyboard)
            ui.on_click(mouse_pos)

    if keyboard[pygame.K_r]:
        queens_grid.update_superpositions()
    
    # Fill screen with a color (optional)
    screen.fill((30, 30, 30))
    queens_grid.draw(screen)
    ui.draw(screen, mouse_pos)
    
    # Update display
    pygame.display.flip()

# Quit Pygame
pygame.quit()
