import pygame
from utils.paths import REGULAR
from gui.control_element.button import Button
from gui.control_element.drop_down import DropDown, DropDownItem
from models import rover, presets
from models.rover import Rover
from models.project import get_all_projects
from models.rover import get_rovers_by_project
from models.project import Project
class LDPopupWindow:
    def __init__(self, screen, width=400, height=300, title="Popup", on_confirm = None, save_popup=False):  # Store the callback
        """Initialize the popup window."""
        self.screen = screen
        self.width = width
        self.height = height
        self.title = title
        self.on_confirm = on_confirm  # Store the callback
        self.save_popup = save_popup

        # Popup rectangle
        self.popup_rect = pygame.Rect(
            (screen.get_width() - width) // 2,
            (screen.get_height() - height) // 2,
            width,
            height
        )

        # Close button rectangle
        self.close_rect = pygame.Rect(self.popup_rect.right - 30, self.popup_rect.top + 10, 20, 20)

        # Colors
        self.BACKGROUND_COLOR = (36, 36, 36)
        self.BORDER_COLOR = (50, 50, 50)
        self.CLOSE_COLOR = (200, 50, 50)
        self.SCROLLBAR_COLOR = (150, 150, 150)
        self.SCROLLBAR_TRACK_COLOR = (200, 200, 200)
        self.TEXT_COLOR = (255, 255, 255)
        self.DIM_COLOR = (0, 0, 0, 150)

        # Fonts
        self.title_font = pygame.font.Font(REGULAR, 32) 
        self.subtitle_font = pygame.font.Font(REGULAR, 24)
        self.body_font = pygame.font.Font(REGULAR, 18) 

        COLOR_UI_INACTIVE = (65, 71, 82)
        COLOR_UI_ACTIVE = "orange"
        TEXT_COLOR = "white"
        BORDER_RADIUS = 3
        FONT = pygame.font.Font(REGULAR, 12)
        UI_H = 20
        UI_W = 150

        # State
        self.visible = False

        # Example projects list
        # self.projects: list[Project] = get_all_projects()
        # self.project_list: str = []
        # for p in self.projects:
        #     self.project_list.append(p.project_id)
        
        # if len(self.project_list) == 0:
        #     self.projects = ["None"]
        # print(self.project_list)

        self.project_list = get_all_projects()
        options = [p.project_id for p in self.project_list]

        # Create dropdown
        self.project_drop_down = DropDown(
            name="Select a project...",
            options=options,
            on_select_callback=self.on_select_project,
            color_main_inactive=(65, 71, 82),
            color_main_active=(85, 91, 102),
            color_option_inactive=(65, 71, 82),
            color_option_active=(120, 130, 140),
            font=self.body_font,
            text_color=pygame.Color("white"),
            border_radius=5,
            x=self.popup_rect.x + 20,
            y=self.popup_rect.y + 80,
            w=500,
            h=40,
            option_w=500,
            scroll_icon_actif=True,
            show_selected_as_title=True
        )

        self.confirm_button = Button(
        name="Confirm",
        color_main_inactive=(65, 71, 82),
        color_main_active=(85, 91, 102),
        font=self.body_font,
        text_color=pygame.Color("white"),
        border_radius=5,
        x=self.popup_rect.centerx - 60,
        y=self.popup_rect.bottom - 60,
        w=120,
        h=35,
        maintain_click=False  # unless you want it to stay "clicked"
        )

        self.selected_project: Project = None
        self.rover_info_lines = []
        self.bounding_box = None


    def show(self, file_path=None):
        """Show the popup window and load content if a file is provided."""
        self.refresh_project_list()
        if file_path:
            self.load_content(file_path)
        self.scroll_position = 0  # Reset scroll
        self.visible = True

    def hide(self):
        """Hide the popup window."""
        self.visible = False

    def on_select_project(self, project: DropDownItem):
        for p in self.project_list:
            if p.project_id == project.id:
                self.selected_project = p
                break
        
        if self.selected_project.top_left_x != None:
            self.bounding_box = (self.selected_project.top_left_x,
                                self.selected_project.top_left_y,
                                self.selected_project.bottom_right_x,
                                    self.selected_project.bottom_right_y)
        else:
            self.bounding_box = None

        # Get rover info for selected project
        rovers = get_rovers_by_project(self.selected_project.project_id)
        if len(rovers) > 0:
            for i,r in enumerate(rovers):
                self.rover_info_lines = [
                    f"{i+1}. Rover Name: {r.name}",
                    f"   Max Incline: {r.max_incline}",
                    f"   Power Source: {r.power_source}"
                    # f"Status: {rover_obj.status}"
                ]
        else:
            self.rover_info_lines = ["No rover info available"] 

    def handle_event(self, event):
        """Handle events for the popup window."""
        if not self.visible:
            return

        # Let dropdown process the event
        selected_index = self.project_drop_down.update([event])

        # if selected_index >= 0:
        #     self.selected_project = self.projects[selected_index]
            
        #     if self.selected_project.top_left_x != None:
        #         self.bounding_box = (self.selected_project.top_left_x,
        #                              self.selected_project.top_left_y,
        #                                self.selected_project.bottom_right_x,
        #                                  self.selected_project.bottom_right_y)
        #     else:
        #         self.bounding_box = None

        #     # Get rover info for selected project
        #     rovers = get_rovers_by_project(self.selected_project.project_id)
        #     if len(rovers) > 0:
        #         for i,r in enumerate(rovers):
        #             self.rover_info_lines = [
        #                 f"{i+1}. Rover Name: {r.name}",
        #                 f"   Max Incline: {r.max_incline}",
        #                 f"   Power Source: {r.power_source}"
        #                 # f"Status: {rover_obj.status}"
        #             ]
        #     else:
        #         self.rover_info_lines = ["No rover info available"]

        # Handle popup close
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if self.close_rect.collidepoint(event.pos):
                    self.hide()

        # Confirm button hover & click
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()[0]

        self.confirm_button.is_hovered = self.confirm_button.rect.collidepoint(mouse_pos)

        if self.save_popup and self.confirm_button.is_hovered and mouse_pressed:
            self.hide()
            self.confirm_button.is_clicked = True
        else:
            self.confirm_button.is_clicked = False

        if self.selected_project is not None and self.confirm_button.is_hovered and mouse_pressed:
            if not self.confirm_button.is_clicked:
                print(f"Confirmed project: {self.selected_project}")
                if self.on_confirm and self.selected_project:
                    self.on_confirm(self.selected_project)
                self.hide()
                self.confirm_button.is_clicked = True
        else:
            self.confirm_button.is_clicked = False
                

    def draw(self):
        """Draw the popup window."""
        if not self.visible:
            return

        # Dim background
        dim_surface = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        dim_surface.fill(self.DIM_COLOR)
        self.screen.blit(dim_surface, (0, 0))

        # Popup box
        pygame.draw.rect(self.screen, self.BACKGROUND_COLOR, self.popup_rect)
        pygame.draw.rect(self.screen, self.BORDER_COLOR, self.popup_rect, width=2)

        # Recalculate close button
        self.close_rect = pygame.Rect(self.popup_rect.right - 30, self.popup_rect.top + 10, 20, 20)
        pygame.draw.circle(self.screen, self.CLOSE_COLOR, self.close_rect.center, 10)

        # Title
        title_surface = self.title_font.render(self.title, True, self.TEXT_COLOR)
        self.screen.blit(title_surface, (self.popup_rect.x + 20, self.popup_rect.y + 10))

        if not self.save_popup:
            if self.bounding_box:
                x = self.popup_rect.x + 23
                y = self.popup_rect.y + 140  # Adjust if needed

                bb_text_surface = self.body_font.render(f"Bounding box coordinates:", True, self.TEXT_COLOR)
                self.screen.blit(bb_text_surface, (x, y))
                y += 35  # Space between lines
                bb_text_surface = self.body_font.render(f"Top left x: {self.bounding_box[0]}", True, self.TEXT_COLOR)
                self.screen.blit(bb_text_surface, (x, y))
                y += 25  # Space between lines
                bb_text_surface = self.body_font.render(f"Top left y: {self.bounding_box[1]}", True, self.TEXT_COLOR)
                self.screen.blit(bb_text_surface, (x, y))
                y += 25  # Space between lines
                bb_text_surface = self.body_font.render(f"Bottom right x: {self.bounding_box[2]}", True, self.TEXT_COLOR)
                self.screen.blit(bb_text_surface, (x, y))
                y += 25  # Space between lines
                bb_text_surface = self.body_font.render(f"Bottom right y: {self.bounding_box[3]}", True, self.TEXT_COLOR)
                self.screen.blit(bb_text_surface, (x, y))
                y += 25  # Space between lines
            
            else: 
                x = self.popup_rect.x + 23
                y = self.popup_rect.y + 140  # Adjust if needed

                bb_text_surface = self.body_font.render(f"No bounding box set.", True, self.TEXT_COLOR)
                self.screen.blit(bb_text_surface, (x, y))

            if self.rover_info_lines:
                x = self.popup_rect.x + 330
                y = self.popup_rect.y + 140  # Adjust if needed

                text_surface = self.body_font.render("Rover(s):", True, self.TEXT_COLOR)
                self.screen.blit(text_surface, (x, y))
                y += 35 

                for line in self.rover_info_lines:
                    text_surface = self.body_font.render(line, True, self.TEXT_COLOR)
                    self.screen.blit(text_surface, (x, y))
                    y += 25  # Space between lines
            
            else:
                x = self.popup_rect.x + 330
                y = self.popup_rect.y + 140  # Adjust if needed

                text_surface = self.body_font.render("No rovers added yet.", True, self.TEXT_COLOR)
                self.screen.blit(text_surface, (x, y))

        if not self.save_popup:
            self.project_drop_down.draw(self.screen)
        self.confirm_button.draw(self.screen)

        # Draw confirm button
        is_enabled = self.selected_project is not None or self.save_popup
        button_color = (
            self.confirm_button.color_main_active if self.confirm_button.is_hovered else self.confirm_button.color_main_inactive
        ) if is_enabled else (50, 50, 50)
        # button_color = self.confirm_button.color_main_active if self.confirm_button.is_hovered else self.confirm_button.color_main_inactive
        pygame.draw.rect(self.screen, button_color, self.confirm_button.rect, border_radius=self.confirm_button.border_radius)

        # Draw button text
        button_text = self.confirm_button.font.render(self.confirm_button.name, True, self.confirm_button.text_color)
        text_rect = button_text.get_rect(center=self.confirm_button.rect.center)
        self.screen.blit(button_text, text_rect)

    def refresh_project_list(self):
        """Refresh the dropdown with updated projects from the database."""
        self.project_list = get_all_projects()

        # Re-initialize the dropdown with new project list
        options = []
        for p in self.project_list:
            options.append(DropDownItem(p.project_id, p.project_name or p.project_id))
        self.project_drop_down.set_options(options)
        self.project_drop_down.name = "Select a project..."
        self.selected_project = None
        self.rover_info_lines = []
        self.bounding_box = None

     