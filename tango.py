import pygame
from common.grid import Grid, State
import common.symbols as symbols

class TangoState(State):
    def __init__(self, name, symbol, other_name):
        super().__init__(name, symbol)
        self.other_name = other_name

    def is_possible(self, grid, cell_x, cell_y):
        in_row = grid.must_be(cell_x - 1, cell_y, self.name) and grid.must_be(cell_x + 1, cell_y, self.name)
        in_row = in_row or grid.must_be(cell_x - 2, cell_y, self.name) and grid.must_be(cell_x - 1, cell_y, self.name)
        in_row = in_row or grid.must_be(cell_x + 1, cell_y, self.name) and grid.must_be(cell_x + 2, cell_y, self.name)
        in_col = grid.must_be(cell_x, cell_y - 1, self.name) and grid.must_be(cell_x, cell_y + 1, self.name)
        in_col = in_col or grid.must_be(cell_x, cell_y - 2, self.name) and grid.must_be(cell_x, cell_y - 1, self.name)
        in_col = in_col or grid.must_be(cell_x, cell_y + 1, self.name) and grid.must_be(cell_x, cell_y + 2, self.name)

        # Count the number of times this state appears and the number of times the other state appears in the row and column
        min_row_count = 0
        max_row_count = 0
        for cell in grid.iter_row(cell_y):
            if cell == grid.cells[cell_x][cell_y]:
                continue

            if cell.can_be(self.name):
                max_row_count += 1

            if cell.must_be(self.name):
                min_row_count += 1

        if min_row_count >= 3:
            return False
        
        min_col_count = 0
        max_col_count = 0
        for cell in grid.iter_col(cell_x):
            if cell == grid.cells[cell_x][cell_y]:
                continue

            if cell.can_be(self.name):
                max_col_count += 1

            if cell.must_be(self.name):
                min_col_count += 1
        
        if min_col_count >= 3:
            return False
        
        # Check equality constraints
        for (x1, y1), (x2, y2) in grid.equals:
            if (x1, y1) == (cell_x, cell_y):
                if grid.must_be(x2, y2, self.other_name):
                    return False
            elif (x2, y2) == (cell_x, cell_y):
                if grid.must_be(x1, y1, self.other_name):
                    return False
                
        # Check opposite constraints
        for (x1, y1), (x2, y2) in grid.opposites:
            if (x1, y1) == (cell_x, cell_y):
                if grid.must_be(x2, y2, self.name):
                    return False
            elif (x2, y2) == (cell_x, cell_y):
                if grid.must_be(x1, y1, self.name):
                    return False

        return not in_row and not in_col

SUN = TangoState("SUN", symbols.SUN, "MOON")
MOON = TangoState("MOON", symbols.MOON, "SUN")

class TangoGrid(Grid):
    def __init__(self, width, height):
        super().__init__(width, height, 80, (200, 200, 200), (100, 100, 100), [SUN, MOON])
        self.equals = [] # ((x1, y1), (x2, y2)) pairs of cells that must be the same
        self.opposites = [] # ((x1, y1), (x2, y2)) pairs of cells that must be different

        self.edit_mode = None 
        self.cell_a = None

    def on_cell_click(self, x, y, keyboard):
        if keyboard[pygame.K_LSHIFT]:
            self.cells[x][y].update(self, x, y)
        else:
            if self.edit_mode == "SUN":
                self.cells[x][y].states = [SUN]
            elif self.edit_mode == "MOON":
                self.cells[x][y].states = [MOON]
            elif self.edit_mode == "EQUALS_A":
                self.cell_a = (x, y)
                self.edit_mode = "EQUALS_B"
            elif self.edit_mode == "EQUALS_B":
                self.equals.append((self.cell_a, (x, y)))
                self.cell_a = None
                self.edit_mode = None
            elif self.edit_mode == "OPPOSITE_A":
                self.cell_a = (x, y)
                self.edit_mode = "OPPOSITE_B"
            elif self.edit_mode == "OPPOSITE_B":
                self.opposites.append((self.cell_a, (x, y)))
                self.cell_a = None
                self.edit_mode = None


    def draw(self, screen):
        super().draw(screen)

        # Draw green dot between equal-constrained cells
        for (x1, y1), (x2, y2) in self.equals:
            center_1 = self.get_cell_center(x1, y1)
            center_2 = self.get_cell_center(x2, y2)
            average = ((center_1[0] + center_2[0]) // 2, (center_1[1] + center_2[1]) // 2)

            pygame.draw.circle(screen, (0, 255, 0), average, 5)

        # Draw a red dot between opposite-constrained cells
        for (x1, y1), (x2, y2) in self.opposites:
            center_1 = self.get_cell_center(x1, y1)
            center_2 = self.get_cell_center(x2, y2)
            average = ((center_1[0] + center_2[0]) // 2, (center_1[1] + center_2[1]) // 2)

            pygame.draw.circle(screen, (255, 0, 0), average, 5)

        # Draw a border around the selected cell
        if self.cell_a:
            x, y = self.cell_a
            pygame.draw.rect(screen, (0, 255, 0), (x * self.cell_size, y * self.cell_size, self.cell_size, self.cell_size), 3)

    def clone(self):
        copy = TangoGrid(self.width, self.height)
        copy.equals = [pair for pair in self.equals]
        copy.opposites = [pair for pair in self.opposites]

        copy.is_original = False

        for x in range(self.width):
            for y in range(self.height):
                copy.cells[x][y].states = [state for state in self.cells[x][y].states]
        
        return copy