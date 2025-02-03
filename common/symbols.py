import pygame

class Symbol:
    def __init__(self):
        pass

    def draw(self, screen, x, y, cell_size):
        pass

class ImageSymbol:
    def __init__(self, image):
        self.image = image

    def draw(self, screen, x, y, cell_size):
        screen.blit(self.image, (x + 8, y + 8))

# CROWN = Symbol()
# MOON = Symbol()
# SUN = Symbol()

CROWN = ImageSymbol(pygame.image.load("assets/crown.png"))
MOON = ImageSymbol(pygame.image.load("assets/moon.png"))
SUN = ImageSymbol(pygame.image.load("assets/sun.png"))