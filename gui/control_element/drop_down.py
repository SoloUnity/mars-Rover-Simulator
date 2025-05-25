import pygame
from utils.paths import REGULAR, get_image
from typing import Callable

## TODO handle no initial option list，for select rover

class DropDownItem():
    def __init__(self, id: int, name: str):
        self.id = id
        self.name = name

class DropDown():
    def __init__(self, name, options: list[DropDownItem] | list[str], on_select_callback: Callable[[DropDownItem], None], color_main_inactive, color_main_active, color_option_inactive, color_option_active, font, text_color, border_radius: int, x: int, y: int, w: int, h: int, option_w: int, scroll_icon_actif = False, show_selected_as_title = False):
        self.initial_name = name
        self.name = self.initial_name

        self.enabled = True
        self.on_select_callback = on_select_callback

        # Convert string options to DropDownItem
        dropdown_options = self.format_options(options)

        self.options: list[DropDownItem] = dropdown_options
        self.font = font
        self.color_main_active = color_main_active
        self.color_main_inactive = color_main_inactive
        self.color_option_active = color_option_active
        self.color_option_inactive = color_option_inactive
        self.rect = pygame.Rect(x,y,w,h)
        self.border_radius = border_radius
        self.text_color = text_color
        self.option_w = option_w
        self.show_selected_as_title = show_selected_as_title

        self.menu_box_rect = pygame.Rect(x, y+h, option_w, len(options) * h + 6)
        self.option_toggled = False
        self.menu_active = False
        self.option_active = -1
        self.scroll_icon_actif = scroll_icon_actif

    def enable(self):
        self.enabled = True

    def disable(self):
        self.enabled = False

    def set_title(self, title):
        self.name = title

    def format_options(self, options):
        dropdown_options = []
        for i, option in enumerate(options):
            if type(option) == str:
                dropdown_options.append(DropDownItem(i, option))
            else:
                dropdown_options.append(option)
        return dropdown_options

    def set_options(self, options):
        self.options = self.format_options(options)
        self.compute_menu_box_rect()

    def add_option(self, option: DropDownItem | str, prepend: bool = False):
        if type(option) == str:
            option = DropDownItem(len(self.options), option)

        if prepend:
            self.options.insert(0, option)
        else:
            self.options.append(option)
        
        self.compute_menu_box_rect()
        
    def compute_menu_box_rect(self):
        self.menu_box_rect = pygame.Rect(self.rect.x, self.rect.y+self.rect.h, self.option_w, len(self.options) * self.rect.h + 6)


    def reset(self):
        self.name = self.initial_name    
    
    def draw(self, display):
        pygame.draw.rect(display, self.color_main_active if self.menu_active and self.enabled else self.color_main_inactive, self.rect, 0, self.border_radius)
        name = self.font.render(self.name, 1, self.text_color) 
        display.blit(name, name.get_rect(center = self.rect.center))

        if self.scroll_icon_actif:
            arrow_icon = pygame.image.load(get_image('icon_arrow_down.png'))
            icon_size = (self.rect.height // 2, self.rect.height // 2)  # Resize based on dropdown height
            arrow_icon = pygame.transform.scale(arrow_icon, icon_size)

            icon_rect = arrow_icon.get_rect(midright=(self.rect.right - 10, self.rect.centery))
            display.blit(arrow_icon, icon_rect.topleft)
        
        if self.option_toggled:

            pygame.draw.rect(display, self.color_main_inactive, self.menu_box_rect, 0, self.border_radius)

            rect = self.rect.copy()
            for i, option in enumerate(self.options):
                rect = self.rect.copy()
                rect.y += (i + 1) * self.rect.height + 3
                rect.width = self.option_w - 5/100*self.option_w
                rect.centerx = self.menu_box_rect.centerx

                pygame.draw.rect(display, self.color_option_active if i == self.option_active else self.color_main_inactive, rect, 0, self.border_radius)
                option_text = self.font.render(option.name, True, self.text_color)

                text_rect = option_text.get_rect()
                text_rect.left = rect.left + 4  
                text_rect.centery = rect.centery  

                display.blit(option_text, text_rect.topleft)  
                
    def set_position(self, x, y):
        self.rect.topleft = (x, y)
        self.menu_box_rect.topleft = (x, y + self.rect.height)

    def update(self, events):
        mpos = pygame.mouse.get_pos()
        self.menu_active = self.rect.collidepoint(mpos)
        
        self.option_active = -1
        for i in range(len(self.options)):
            rect = self.rect.copy()
            rect.y += (i+1) * self.rect.height + 3
            rect.width = self.option_w
            if rect.collidepoint(mpos):
                self.option_active = i
                break

        if not self.enabled:
            return

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.menu_active:
                    self.option_toggled = not self.option_toggled
                elif self.option_toggled:
                    if self.option_active >= 0:
                        self.option_toggled = False
                        if self.show_selected_as_title:
                            self.name = self.options[i].name
                        self.on_select_callback(self.options[i])
                    elif not self.menu_box_rect.collidepoint(mpos) and not self.rect.collidepoint(mpos):
                        self.option_toggled = False    
