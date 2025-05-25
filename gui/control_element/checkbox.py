import pygame

class Checkbox:
    def __init__(self, x, y, size, font, label="Checkbox", checked=False,
                 box_color=(65, 71, 82), border_color="white", check_color="orange", text_color="white"):
        self.rect = pygame.Rect(x, y, size, size)
        self.checked = checked
        self.font = font
        self.label = label
        self.box_color = box_color
        self.border_color = border_color
        self.check_color = check_color
        self.text_color = text_color
        self.enabled = True

    def enable(self):
        self.enabled = True

    def disable(self):
        self.enabled = False

    def update(self, events):
        if not self.enabled:
            return
        
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.rect.collidepoint(event.pos):
                    self.checked = not self.checked

    def draw(self, surface):
        # Draw box
        pygame.draw.rect(surface, self.box_color, self.rect)
        pygame.draw.rect(surface, self.border_color, self.rect, 2)

        # Draw checkmark if checked
        if self.checked:
            pygame.draw.line(surface, self.check_color, (self.rect.left+4, self.rect.centery),
                             (self.rect.centerx, self.rect.bottom-4), 2)
            pygame.draw.line(surface, self.check_color, (self.rect.centerx, self.rect.bottom-4),
                             (self.rect.right-4, self.rect.top+4), 2)

        # Draw label
        text_surf = self.font.render(self.label, True, self.text_color)
        surface.blit(text_surf, (self.rect.right + 8, self.rect.y - 2))
