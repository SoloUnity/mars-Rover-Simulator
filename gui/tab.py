import pygame
from utils.paths import REGULAR

class Tab:
    def __init__(self, project, tab_id, position, width=256, height=30):
        self.project = project
        self.tab_id = tab_id
        self.position = position
        self.width = width
        self.height = height
        self.is_selected = False
        self.is_editing = False 
        self.new_name = ""  
        self.last_click_time = 0  

        # Tab Rect
        self.rect = pygame.Rect((position * width), 33, width, height)

        # close button rect (small X button on the right side)
        self.x_size = 15  # Width & height of close button
        self.x_rect = pygame.Rect(self.rect.right - self.x_size - 3, self.rect.top + 8, self.x_size, self.x_size)

        #Colors
        self.COLOR_SELECTED = (70, 70, 70)
        self.COLOR_DEFAULT = (31, 30, 30)
        self.COLOR_TEXT = (255, 255, 255)
        self.COLOR_CLOSE = (200, 50, 50)  

        # Font
        self.font = pygame.font.Font(REGULAR, 15)
        self.name = project.project_name or f"Project {self.tab_id}"

    def draw(self, screen):
        color = self.COLOR_SELECTED if self.is_selected else self.COLOR_DEFAULT
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.line(screen, (255, 255, 255), (self.rect.right, self.rect.top), (self.rect.right, self.rect.bottom), 1) 
        pygame.draw.line(screen, (255, 255, 255), (self.rect.left, self.rect.top), (self.rect.left, self.rect.bottom), 1)  

        if self.is_editing:
            self.font.set_italic(True)
            text_surface = self.font.render(self.new_name, True, (30,144,255))  #blue text
            self.font.set_italic(False)
        else:
            #render tab name
            text_surface = self.font.render(self.name, True, self.COLOR_TEXT)
            self.project.project_name = self.name

        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect.topleft)

        # draw close button
        pygame.draw.rect(screen, self.COLOR_CLOSE, self.x_rect, border_radius=2)
        x_text = self.font.render("X", True, self.COLOR_TEXT)
        screen.blit(x_text, (self.x_rect.x + 2, self.x_rect.y - 1))  

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Check if the tab was clicked
            if self.rect.collidepoint(event.pos):
                current_time = pygame.time.get_ticks()
                if current_time - self.last_click_time < 500:
                    self.is_editing = True
                    self.new_name = self.name  
                self.last_click_time = current_time  

        if self.is_editing:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN: 
                    if self.new_name.strip() == "":
                        self.new_name = "Project" 
                    if len(self.new_name.strip()) > 20:
                        self.new_name = self.new_name.strip()[:18].strip()+"..."
                    self.name = self.new_name.strip()
                    self.is_editing = False
                elif event.key == pygame.K_ESCAPE: 
                    self.is_editing = False
                elif event.key == pygame.K_BACKSPACE:  
                    self.new_name = self.new_name[:-1]
                else:
                    self.new_name += event.unicode 

            if event.type == pygame.MOUSEBUTTONDOWN and not self.rect.collidepoint(event.pos):
                if self.new_name.strip() == "":
                    self.new_name = "Project"
                if len(self.new_name.strip()) > 20:
                    self.new_name = self.new_name.strip()[:18].strip()+"..."
                self.name = self.new_name.strip()
                self.is_editing = False

    ## Check if the tab or close button was clicked
    def check_click(self, mouse_pos):
        if self.x_rect.collidepoint(mouse_pos):
            return "close"  
        elif self.rect.collidepoint(mouse_pos):
            return "select"  
        return None  

