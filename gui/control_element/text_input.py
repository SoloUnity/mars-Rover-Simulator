import pygame

class TextInput:
    def __init__(self, font, x, y, w, h, text_color="white", bg_color=(65, 71, 82), border_color=(100, 100, 100), active_color="orange"):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = bg_color
        self.text_color = text_color
        self.border_color = border_color
        self.active_color = active_color
        self.font = font
        self.text = ""
        self.active = False
        self.enabled = False

    def enable(self):
        self.enabled = True
    
    def disable(self):
        self.enabled = False

    def set_text(self, text: str):
        self.text = text

    def update(self, events):
        if not self.enabled:
            return
        
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.active = self.rect.collidepoint(event.pos)
            elif event.type == pygame.KEYDOWN and self.active:
                if event.key == pygame.K_RETURN:
                    self.active = False
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode

    def draw(self, surface):
        pygame.draw.rect(surface, self.active_color if self.active else self.border_color, self.rect, 2)
        txt_surf = self.font.render(self.text, True, self.text_color)
        surface.blit(txt_surf, (self.rect.x + 5, self.rect.y + 3))
