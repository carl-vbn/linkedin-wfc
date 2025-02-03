import pygame

class Button:
    def __init__(self, x, y, width, height, text, bg_color, action):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.bg_color = bg_color
        self.hover_color = (min(255, bg_color[0] + 50), min(255, bg_color[1] + 50), min(255, bg_color[2] + 50))
        self.text_color = (255, 255, 255)
        self.action = action

    def draw(self, screen, font, mouse_pos):
        hovered = self.rect.collidepoint(mouse_pos)
        pygame.draw.rect(screen, self.hover_color if hovered else self.bg_color, self.rect)
        text = font.render(self.text, True, self.text_color)
        text_rect = text.get_rect(center=self.rect.center)
        screen.blit(text, text_rect)
    
    def on_click(self, mouse_pos):
        if self.rect.collidepoint(mouse_pos):
            self.action()

class UI:
    def __init__(self):
        self.buttons = []
        self.font = pygame.font.Font(None, 32)

    def add_button(self, button):
        self.buttons.append(button)

    def draw(self, screen, mouse_pos):
        for button in self.buttons:
            button.draw(screen, self.font, mouse_pos)

    def on_click(self, mouse_pos):
        for button in self.buttons:
            button.on_click(mouse_pos)

def make_ui(*buttons):
    ui = UI()
    for button in buttons:
        ui.add_button(button)
    return ui