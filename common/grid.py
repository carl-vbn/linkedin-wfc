import pygame

class State:
    def __init__(self, name, symbol):
        self.name = name
        self.symbol = symbol
    
    def is_possible(self, grid, cell_x, cell_y):
        raise NotImplementedError()

class Cell:
    def __init__(self, bg_col, border_col, possible_states=None):
        self.bg_col = bg_col
        self.border_col = border_col
        self.states = [s for s in possible_states] if possible_states else []

    def update(self, grid, cell_x, cell_y):
        updated = False

        for i in range(len(self.states)-1, -1, -1): # Iterate backwards to allow for removal
            if not self.states[i].is_possible(grid, cell_x, cell_y):
                self.states.pop(i)
                updated = True

        return updated

    def collapse(self, state_index):
        self.states = [self.states[state_index]]

    def draw(self, screen, x, y, cell_size):
        # Border
        pygame.draw.rect(screen, self.border_col, (x, y, cell_size, cell_size))

        # Content
        solved_col = (min(255, self.bg_col[0] + 50), min(255, self.bg_col[1] + 50), min(255, self.bg_col[2] + 50))
        pygame.draw.rect(screen, solved_col if len(self.states) == 1 else self.bg_col, (x + 1, y + 1, cell_size - 2, cell_size - 2))
        
        for possible_state in self.states:
            possible_state.symbol.draw(screen, x, y, cell_size)

    def can_be(self, state_name):
        for state in self.states:
            if state.name == state_name:
                return True
        return False
    
    def must_be(self, state_name):
        if len(self.states) == 1:
            return self.states[0].name == state_name
        
        return False

class Grid:
    def __init__(self, width, height, cell_size, bg_col, border_col, possible_states=None):
        self.width = width
        self.height = height
        self.cell_size = cell_size
        self.bg_col = bg_col
        self.border_col = border_col
        self.possible_states = possible_states
        self.cells = [[Cell(bg_col, border_col, possible_states) for _ in range(height)] for _ in range(width)]

        self.is_original = True

    def reset(self):
        for x in range(self.width):
            for y in range(self.height):
                self.cells[x][y].states = [s for s in self.possible_states]
                self.cells[x][y].bg_col = self.bg_col

    def draw(self, screen):
        for x in range(self.width):
            for y in range(self.height):
                self.cells[x][y].draw(screen, x * self.cell_size, y * self.cell_size, self.cell_size)

    def get_cell_coords(self, mouse_x, mouse_y):
        x = mouse_x // self.cell_size
        y = mouse_y // self.cell_size

        if 0 <= x < self.width and 0 <= y < self.height:
            return x, y
        else:
            return None
        
    def on_cell_click(self, x, y, keyboard):
        pass
        
    def on_click(self, mouse_x, mouse_y, keyboard):
        cell_coords = self.get_cell_coords(mouse_x, mouse_y)
        if cell_coords:
            self.on_cell_click(*cell_coords, keyboard)

    def iter_cells(self):
        for x in range(self.width):
            for y in range(self.height):
                yield self.cells[x][y]

    def iter_cell_coords(self):
        for x in range(self.width):
            for y in range(self.height):
                yield x, y

    def iter_col(self, x):
        for y in range(self.height):
            yield self.cells[x][y]

    def iter_row(self, y):
        for x in range(self.width):
            yield self.cells[x][y]
    
    def update_superpositions(self, recursion_depth=20):
        updated = True
        while updated:
            updated = False
            for x, y in self.iter_cell_coords():
                updated = updated or self.cells[x][y].update(self, x, y)

        if recursion_depth > 0:
            # Pick the first cell with more than one possible state
            selected_cell_coords = None
            for x in range(self.width):
                for y in range(self.height):
                    if len(self.cells[x][y].states) > 1:
                        selected_cell_coords = (x, y)
                        break

            if selected_cell_coords:
                selected_cell = self.cells[selected_cell_coords[0]][selected_cell_coords[1]]

                for state_index in range(len(selected_cell.states)):
                    test_grid = self.clone()
                    test_grid.collapse(*selected_cell_coords, state_index, update=False)
                    test_grid.update_superpositions(recursion_depth - 1)
                    if test_grid.has_contradiction():
                        # Remove this state from the superposition
                        selected_cell.states.pop(state_index)
                        
                        self.update_superpositions(recursion_depth - 1)
                        break

    def collapse(self, x, y, state_index, update=False):
        self.cells[x][y].collapse(state_index)

        if update:
            self.update_superpositions()
    
    def can_be(self, x, y, state_name):
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return False
        
        return self.cells[x][y].can_be(state_name)
    
    def must_be(self, x, y, state_name):
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return False
        
        return self.cells[x][y].must_be(state_name)
    
    def get_cell_center(self, x, y):
        return (x + 0.5) * self.cell_size, (y + 0.5) * self.cell_size
    
    def clone(self):
        grid = Grid(self.width, self.height, self.cell_size, self.bg_col, self.border_col)
        for x in range(self.width):
            for y in range(self.height):
                grid.cells[x][y].states = [state for state in self.cells[x][y].states]

        grid.is_original = False
        
        return grid

    def has_contradiction(self):
        for x in range(self.width):
            for y in range(self.height):
                if len(self.cells[x][y].states) == 0:
                    return True
            
        return False