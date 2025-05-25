import pygame

class Button:
    def __init__(self, name, color_main_inactive, color_main_active, font, text_color, border_radius, x, y, w, h, icon=None, icon_scaling=None, maintain_click=False):
        self.name = name
        self.color_main_inactive = color_main_inactive
        self.color_main_active = color_main_active
        self.font = font
        self.text_color = text_color
        self.rect = pygame.Rect(x, y, w, h)
        self.border_radius = border_radius
        self.icon = icon
        self.icon_scaling = icon_scaling
        self.drawn = False
        self.is_hovered = False
        self.is_clicked = False
        self.maintain_click = maintain_click
        self.disabled = False
    
    def set_icon(self, icon):
        self.icon = icon

    def draw(self, display):
        color = self.color_main_active if self.is_clicked or self.is_hovered else self.color_main_inactive
        pygame.draw.rect(display, color, self.rect, 0, self.border_radius)

        if self.icon:
            icon_width, icon_height = self.icon.get_size()
            scale_factor = min(self.rect.width / icon_width, self.rect.height / icon_height)
            new_width = int(icon_width * scale_factor)
            new_height = int(icon_height * scale_factor)
            if self.icon_scaling:
                new_width = new_width * self.icon_scaling
                new_height = new_height * self.icon_scaling
            resized_icon = pygame.transform.scale(self.icon, (new_width, new_height))
            icon_rect = resized_icon.get_rect(center=self.rect.center)
            display.blit(resized_icon, icon_rect)
        elif self.name:
            text_surface = self.font.render(self.name, True, self.text_color)
            text_rect = text_surface.get_rect(center=self.rect.center)
            display.blit(text_surface, text_rect)

        self.drawn = True
    
    def erase(self):
        self.drawn = False

    def update(self, event_list):
        if not self.drawn:
            return
        
        if not self.disabled:
        
            mpos = pygame.mouse.get_pos()
            self.is_hovered = self.rect.collidepoint(mpos)

            for event in event_list:
                if self.is_hovered and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.maintain_click:
                        self.is_clicked = not self.is_clicked
                    else:
                        self.is_clicked = True

                if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    if not self.maintain_click:
                        self.is_clicked = False
