import sys

import pygame
import pygame._sdl2
import threading

from gui.control_element.bounding_box import BoundingBox
from gui.control_element.button import Button
from gui.control_element.drop_down import DropDown, DropDownItem
from gui.control_element.edit_rover import EditRover
from gui.control_element.load_delete_popup import LDPopupWindow
from gui.control_element.loading_display import draw_loading_screen
from gui.control_element.stats_display import StatsDisplay
from utils.paths import REGULAR, get_image, get_text_file
from gui.control_element.map_view import MapView
from gui.control_element.popup_window import PopupWindow
from gui.states.tab_manager import TabManager
from gui.temp_project import Project
from gui.rover_manager import RoverManager
from src.ai_algos.AStar import AStar
from src.ai_algos.MapHandler import MapHandler
# from src.ai_algos.Rover import Rover
from src.util.dem_to_matrix import dem_to_matrix, get_window_for_path
from src.util.matrix_to_maze_map import matrix_to_maze_map
from src.util.matrix_to_topo_map import matrix_to_topo_map
from src.ai_algos.AStar import AStar
from models.rover import Rover, create_rover
from models.project import save_project, delete_project
import time
import gc

# from models.project import Project
# support resize

# constants for UI
WHITE = (255, 255, 255)
FONT = pygame.font.Font(REGULAR, 15)
LIGHT_GRAY = (155, 155, 155)
TAB_COLOR = (31, 30, 30)
SIMULATION_SCREEN_COLOR = (48, 48, 49)


class Simulation:
    def __init__(self, display, program_state_manager):
        self.display = display
        self.program_state_manager = program_state_manager
        self.sdl2_window = pygame._sdl2.video.Window.from_display_module()
        self.tab_manager = TabManager()
        self.projects = [None] * 5  # max 5 projects/tabs
        self.active_project = None  # Currently selected project
        self.fullscreen = False  # Tracks fullscreen state
        self.loading_lock = threading.Lock()  # IMPORTANT FOR THREADING (variable changes)
        self.is_loading = False
        # loading screen state
        self.loading_message = ""
        self.loading_current = 0
        self.loading_total = 1
        self.loading_start_time = None

        self.rover_to_display: Rover = None
        self.selected_rover: Rover = None
        self.rover_manager = RoverManager()

        # Initialize map area (x, y, width, height)
        self.map_x = 0
        self.map_y = 63
        self.map_width = (
            self.display.get_width()
        )  # Default value (adjust based on UI)
        self.map_height = (
            self.display.get_height() - 63
        )  # Default value (adjust based on UI)

        self.SIMULATION_WINDOW_X = 0
        self.SIMULATION_WINDOW_Y = 63
        self.SIMULATION_WINDOW_W = self.display.get_width()
        self.SIMULATION_WINDOW_H = self.display.get_height() - 63

        # MENU
        COLOR_MAIN_INACTIVE = (30, 33, 38)
        COLOR_MAIN_ACTIVE = (65, 71, 82)
        MENU_TEXT_COLOR = "white"
        MENU_BORDER_RADIUS = 3
        MENU_H = 25
        MENU_Y = 3

        # DROP_DOWNS
        DROP_DOWN_COLOR_OPTION_ACTIVE = (65, 71, 82)
        DROP_DOWN_COLOR_OPTION_INACTIVE = (30, 33, 38)

        PROJECT_OPTIONS = [
            "New Project",
            "Load Project",
            "Save Project",
            "Delete Project",
        ]

        # Temporary. TODO needs to upgrade button class
        TEMP_OPTION = [":D", "ehehe", "》:O", "來財， 來"]

        self.pressed_project_dropdown = False
        self.project_drop_down = DropDown(
            "Project",
            PROJECT_OPTIONS,
            self.on_select_project,
            COLOR_MAIN_INACTIVE,
            COLOR_MAIN_ACTIVE,
            DROP_DOWN_COLOR_OPTION_INACTIVE,
            DROP_DOWN_COLOR_OPTION_ACTIVE,
            FONT,
            MENU_TEXT_COLOR,
            MENU_BORDER_RADIUS,
            10,
            MENU_Y,
            55,
            MENU_H,
            150,
        )

        self.select_rover_drop_down = DropDown(
            "Select Rover",
            [],
            self.on_select_rover,
            COLOR_MAIN_ACTIVE,
            (13, 59, 66),
            DROP_DOWN_COLOR_OPTION_ACTIVE,
            (21, 97, 109),
            FONT,
            MENU_TEXT_COLOR,
            5,
            (self.display.get_width() - 342) / 2,
            MENU_Y,
            342,
            MENU_H,
            250,
            scroll_icon_actif=True,
            show_selected_as_title=True,
        )
        # display.get_width()/2 - 75

        # ICONS TOP
        ICON_W = 30
        CLOSE_ICON = pygame.image.load(get_image('icon_close.png'))
        # RESTORE_ICON = pygame.image.load(get_image('icon_restore.png'))
        MINIMIZE_ICON = pygame.image.load(get_image('icon_minimize.png'))

        self.add_rover_button = Button(
            "Add Rover",
            COLOR_MAIN_INACTIVE,
            COLOR_MAIN_ACTIVE,
            FONT,
            MENU_TEXT_COLOR,
            MENU_BORDER_RADIUS,
            75,
            MENU_Y,
            75,
            MENU_H,
        )

        self.help_button = Button(
            "Help",
            COLOR_MAIN_INACTIVE,
            COLOR_MAIN_ACTIVE,
            FONT,
            MENU_TEXT_COLOR,
            MENU_BORDER_RADIUS,
            155,
            MENU_Y,
            45,
            MENU_H,
        )
        self.show_help_popup = False
        
        self.stats_button = Button(
            "Path & Rover Statistics",
            COLOR_MAIN_INACTIVE,
            COLOR_MAIN_ACTIVE,
            FONT,
            MENU_TEXT_COLOR,
            MENU_BORDER_RADIUS,
            200,
            MENU_Y,
            170,
            MENU_H,
        )

        # Popup instance
        self.help_popup = PopupWindow(self.display, width=740, height=488, title="Mars Pathfinding Simulator Guide")
        self.load_popup = LDPopupWindow(self.display, width=740, height=488, title="Select which project to load:", on_confirm=self.handle_project_load )
        self.show_load_popup = False

        self.delete_popup = LDPopupWindow(self.display, width=740, height=488, title="Select which project to delete:", on_confirm=self.handle_delete_project)
        self.show_delete_popup = False

        self.save_popup = LDPopupWindow(self.display, width=740, height=240, title="Saved current project to database.", save_popup=True)
        self.show_save_popup = False

        # self.restore_window_button = Button("Restore", COLOR_MAIN_INACTIVE, COLOR_MAIN_ACTIVE, FONT, MENU_TEXT_COLOR, MENU_BORDER_RADIUS, display.get_width() - 75, MENU_Y, ICON_W, MENU_H, RESTORE_ICON, 0.7)

        # ICONS SIDE
        S_ICON_X = 3
        S_ICON_H = 25

        ERROR_ICON = pygame.image.load(get_image("icon_error.png"))
        SETTING_ICON = pygame.image.load(get_image("icon_setting.png"))
        VISIBILITY_ICON = pygame.image.load(get_image("icon_visibility.png"))

        # self.error_button = Button(
        #     "Error",
        #     COLOR_MAIN_INACTIVE,
        #     COLOR_MAIN_ACTIVE,
        #     FONT,
        #     MENU_TEXT_COLOR,
        #     MENU_BORDER_RADIUS,
        #     S_ICON_X,
        #     display.get_height() - 110,
        #     ICON_W,
        #     S_ICON_H,
        #     ERROR_ICON,
        #     0.8,
        # )

        # self.view_data_button = Button(
        #     "View",
        #     COLOR_MAIN_INACTIVE,
        #     COLOR_MAIN_ACTIVE,
        #     FONT,
        #     MENU_TEXT_COLOR,
        #     MENU_BORDER_RADIUS,
        #     S_ICON_X,
        #     display.get_height() - 75,
        #     ICON_W,
        #     S_ICON_H,
        #     VISIBILITY_ICON,
        #     0.8,
        # )

        # self.setting_button = Button("Setting", COLOR_MAIN_INACTIVE, COLOR_MAIN_ACTIVE, FONT, MENU_TEXT_COLOR, MENU_BORDER_RADIUS, S_ICON_X, display.get_height() - 40, ICON_W, S_ICON_H, SETTING_ICON, 0.8)


        self.drag = BoundingBox(self.display, self, 0, 63, self.display.get_width(), self.display.get_height() - 63, 3000)
        self.confirm_bb = Button("Confirm", COLOR_MAIN_INACTIVE, COLOR_MAIN_ACTIVE, FONT, MENU_TEXT_COLOR, MENU_BORDER_RADIUS, (display.get_width() - (70 + 70 + 70)) / 2, display.get_height() - 100, 70, 50)
        self.reset_bb = Button("Reset", COLOR_MAIN_INACTIVE, COLOR_MAIN_ACTIVE, FONT, MENU_TEXT_COLOR, MENU_BORDER_RADIUS, (display.get_width() - (70 + 70 + 70)) / 2 + 70 + 70, display.get_height() - 100, 70, 50)

        self.find_path_btn = Button("Find Path", COLOR_MAIN_INACTIVE, COLOR_MAIN_ACTIVE, FONT, MENU_TEXT_COLOR, MENU_BORDER_RADIUS, (display.get_width() - (70 + 70 + 70)) / 2, display.get_height() - 100, 70, 50)
        self.reset_path_btn = Button("Reset", COLOR_MAIN_INACTIVE, COLOR_MAIN_ACTIVE, FONT, MENU_TEXT_COLOR, MENU_BORDER_RADIUS, (display.get_width() - (70 + 70 + 70)) / 2 + 70 + 70, display.get_height() - 100, 70, 50)
                
        self.find_optimal_path_btn = Button("Find Optimal Path", COLOR_MAIN_INACTIVE, COLOR_MAIN_ACTIVE, FONT, MENU_TEXT_COLOR, MENU_BORDER_RADIUS, (display.get_width() - (140 + 10 + 140 + 10 + 70)) / 2, display.get_height() - 100, 140, 50)
        self.find_ordered_path_btn = Button("Find Ordered Path", COLOR_MAIN_INACTIVE, COLOR_MAIN_ACTIVE, FONT, MENU_TEXT_COLOR, MENU_BORDER_RADIUS, (display.get_width() - (140 + 10 + 140 + 10 + 70)) / 2 + 140 + 10, display.get_height() - 100, 140, 50)
        self.reset_pathfind_btn = Button("Reset", COLOR_MAIN_INACTIVE, COLOR_MAIN_ACTIVE, FONT, MENU_TEXT_COLOR, MENU_BORDER_RADIUS, (display.get_width() - (140 + 10 + 140 + 10 + 70)) / 2 + 140 + 10 + 140 + 10, display.get_height() - 100, 70, 50)

        self.add_rover_btn = Button("Add Rover", COLOR_MAIN_INACTIVE, COLOR_MAIN_ACTIVE, FONT, MENU_TEXT_COLOR, MENU_BORDER_RADIUS, (display.get_width() - 140) / 2, display.get_height() - 100, 100, 50)

        self.edit_rover_window = EditRover(display, self.rover_manager)
        self.stats_window = StatsDisplay(display)

    def draw_text(self, text, position, font, color=WHITE):
        text_surface = font.render(text, True, color)
        self.display.blit(text_surface, position)

    def reset_simulation_window(self):
        simulation_window = pygame.Rect(
            self.SIMULATION_WINDOW_X,
            self.SIMULATION_WINDOW_Y,
            self.SIMULATION_WINDOW_W,
            self.SIMULATION_WINDOW_H,
        )
        pygame.draw.rect(self.display, SIMULATION_SCREEN_COLOR, simulation_window)
        self.draw_text(
            "Create new project to start simulation +", (499, 342), FONT, LIGHT_GRAY
        )
        pygame.display.flip()  # Update the display

    def get_map_area(self):
        return (self.map_x, self.map_y, self.map_width, self.map_height)

    # tab methods
    def add_new_tab(self, project: Project = None):
        # Find the first available position in the tab list
        existing_positions = {
            tab.position for tab in filter(None, self.tab_manager.tabs)
        }  # Set of occupied positions
        new_position = 0  # Start from index 0

        # Find the first available index
        while new_position in existing_positions:
            new_position += 1
            
        if new_position >= len(self.tab_manager.tabs):
            print("No available tab slots.")
            return

         # Use the passed-in project or create a new one
        if project is not None:
            print("loading pre-existing project")
            new_project = Project(
                project_id=new_position,
                project_name=project.project_name,
                created_on=project.created_on,
                last_accessed=project.last_accessed,
                top_left_x=project.top_left_x,
                top_left_y=project.top_left_y,
                bottom_right_x=project.bottom_right_x,
                bottom_right_y=project.bottom_right_y,
                
            ) # Create a new project
            new_project.bounding_box = (new_project.top_left_x, new_project.top_left_y, new_project.bottom_right_x, new_project.bottom_right_y)
                                             
            new_project.map_view = MapView(
                self.display,
                self.SIMULATION_WINDOW_X,
                self.SIMULATION_WINDOW_Y,
                self.SIMULATION_WINDOW_W,
                self.SIMULATION_WINDOW_H,
            )
            self.active_project = new_project
            if (new_project.top_left_x is not None and
                new_project.top_left_y is not None and
                new_project.bottom_right_x is not None and
                new_project.bottom_right_y is not None and
                (new_project.top_left_x, new_project.top_left_y) != (0, 0) and
                (new_project.bottom_right_x, new_project.bottom_right_y) != (100, 100) and
                new_project.top_left_x < new_project.bottom_right_x and
                new_project.top_left_y < new_project.bottom_right_y):

                xy_top = (new_project.top_left_x, new_project.top_left_y)
                xy_bot = (new_project.bottom_right_x,new_project.bottom_right_y)

                new_project.map_view.calculate_zoom_pixels(xy_top, xy_bot)
                self.drag.reset()
                self.active_project.zoomed_in = True
                self.active_project.bounding_box_selected = True
        else:
            new_project = Project(project_id=new_position) # Create a new project
            self.active_project = new_project  # Update active project reference
            new_project.map_view = MapView(
            self.display,
            self.SIMULATION_WINDOW_X,
            self.SIMULATION_WINDOW_Y,
            self.SIMULATION_WINDOW_W,
            self.SIMULATION_WINDOW_H,
        )
        
        self.projects[new_position] = new_project
        self.tab_manager.add_tab(new_position, new_project)

        print("Switched to project " + str(new_position) + "by adding new tab")

        # Reset bounding box selection
        self.drag.start_coord = None
        self.drag.end_coord = None
        self.drag.dragging = False

    def close_tab(self, tab_id):
        #if(self.tab_manager.get_tab_by_id(tab_id).project in self.stats_window.stats):
        #    self.stats_window.stats.pop(self.tab_manager.get_tab_by_id(tab_id).project)
        self.tab_manager.remove_tab(tab_id)

    def switch_tab(self, tab_id):
        self.tab_manager.select_tab(tab_id)
        self.active_project = self.projects[tab_id]
        print("Switched to project " + str(tab_id) + " by click")

        # Reset bounding box selection
        # print("Resetting bounding box coords after switching tabs")
        self.drag.start_coord = None
        self.drag.end_coord = None
        self.drag.dragging = False

        # If the new project has a saved bounding box, restore it
        if self.active_project.bounding_box:
            x1, y1, x2, y2 = self.active_project.bounding_box
            print(x1, y1, x2, y2)
            if (x1, y1) != (x2, y2):  # Ensure it's a valid box
                self.drag.start_coord = (x1, y1)
                self.drag.end_coord = (x2, y2)
                print("Restoring:", self.drag.start_coord, self.drag.end_coord)
            else:
                print(
                    "Warning: Stored bounding box has identical start and end coordinates."
                )
                self.drag.start_coord = None
                self.drag.end_coord = None

    def draw_tabs(self):
        for tab in filter(None, self.tab_manager.tabs):
            tab.draw(self.display)

    def draw_window(self):
        if self.is_loading:  
            return
        SIMULATION_SCREEN_COLOR = (48, 48, 49)
        CREATE_PROJECT_X = 499

        simulation_window = pygame.Rect(
            self.SIMULATION_WINDOW_X,
            self.SIMULATION_WINDOW_Y,
            self.SIMULATION_WINDOW_W,
            self.SIMULATION_WINDOW_H,
        )
        pygame.draw.rect(self.display, SIMULATION_SCREEN_COLOR, simulation_window)

        self.draw_text(
            "Create new project to start simulation +",
            (CREATE_PROJECT_X, 342),
            FONT,
            LIGHT_GRAY,
        )
        pygame.draw.rect(
            self.display, TAB_COLOR, (0, 32, self.SIMULATION_WINDOW_W, 32)
        )  # tab
        pygame.draw.rect(
            self.display, WHITE, (0, 32, self.SIMULATION_WINDOW_W, 32), 1
        )  # tab border
        self.draw_tabs()  # Draw tab bar

        self.display_mars_full_map()

        # self.select_rover_drop_down.draw(self.display)
        if self.selected_rover:
            text_surface = FONT.render(f"Selected Rover: {self.selected_rover.name}", True, (200, 200, 200)) 
            text_rect = text_surface.get_rect(center=self.select_rover_drop_down.rect.center)  
            self.display.blit(text_surface, text_rect.topleft)   

        if self.active_project and self.active_project.bounding_box_selected:
            self.add_rover_button.disabled = False  # enable the button
            self.add_rover_button.draw(self.display)
        else:
            self.add_rover_button.disabled = True  # disable the button
            text_surface = FONT.render("Add Rover", True, (200, 200, 200)) 
            text_rect = text_surface.get_rect(center=self.add_rover_button.rect.center)  
            self.display.blit(text_surface, text_rect.topleft)   
            
            
        # Draw other buttons
        self.help_button.draw(self.display)
        # self.restore_window_button.draw(self.display)

        # self.error_button.draw(self.display)
        # self.view_data_button.draw(self.display)
        # self.setting_button.draw(self.display)

        if self.active_project and self.active_project.full_path:
            self.stats_button.disabled = False
            self.active_project.map_view.draw_path(
                self.active_project.full_path, color=(0, 87, 231), width=2
            )

            self.stats_button.draw(self.display)
            self.stats_window.draw(self.display, self.active_project)
        else:
            self.stats_button.disabled = True
            text_surface = FONT.render("Path & Rover Statistics", True, (200, 200, 200))
            text_rect = text_surface.get_rect(center=self.stats_button.rect.center)
            self.display.blit(text_surface, text_rect.topleft)  

        self.edit_rover_window.draw(self.display)

        self.project_drop_down.draw(self.display)

        # Draw bounding box selection
        # self.drag.draw()

    def on_select_project(self, project: DropDownItem):
        self.pressed_project_dropdown = True
        if project.name == "New Project":
            self.add_new_tab()
        elif project.name == "Load Project":
            self.show_load_popup = not self.show_load_popup  # Toggle the popup visibility
            if self.show_load_popup:
                self.load_popup.show()
            else:
                self.help_popup.hide()
        elif project.name == "Save Project":
            if self.active_project:
                self.show_save_popup = not self.show_save_popup  # Toggle the popup visibility
                if self.show_save_popup:
                    self.save_popup.show()
                else:
                    self.save_popup.hide()
                if self.active_project.bounding_box:
                    (self.active_project.top_left_x, \
                    self.active_project.top_left_y, \
                    self.active_project.bottom_right_x, \
                    self.active_project.bottom_right_y) = self.active_project.bounding_box
                save_project(self.active_project)
                print(f"Saved project with bb: {self.active_project.top_left_x},{self.active_project.top_left_y},{self.active_project.bottom_right_x},{self.active_project.bottom_right_y}")
            # save and show confirmation popup
        elif project.name == "Delete Project":
            self.show_delete_popup = not self.show_delete_popup
            if self.show_delete_popup:
                self.delete_popup.show()
            else:
                self.delete_popup.hide()

    def run(self, events):
        # Pass events to the TabManager
        self.tab_manager.handle_event(events)
        self.tab_manager.draw(self.display)
        
        # Check loading state *before* processing other UI events for the frameß
        with self.loading_lock:
            is_currently_loading = self.is_loading

        if is_currently_loading:
            # Read the current state safely
            message, current, total, start_time = self.get_loading_state()
            # Draw loading screen directly onto the main display surface
            draw_loading_screen(self.display, message, current=current, total=total, start_time=start_time)
            return  # Skip the rest of the simulation drawing/updates

        self.display.fill((30,33,38))

        # Project Dragdown Logic
        self.project_drop_down.update(events)

        current_project = self.active_project   

        # Process UI events
        self.select_rover_drop_down.update(events)
        self.add_rover_button.update(events)
        self.help_button.update(events)
        # self.restore_window_button.update(events)
        # self.setting_button.update(events)
        # self.error_button.update(events)
        #self.view_data_button.update(events)
        self.stats_button.update(events)

        if self.add_rover_button.is_clicked:
            self.edit_rover_window.active = True
            self.add_rover_button.is_clicked = False

        if self.stats_button.is_clicked :
            self.stats_window.active = True

        edit_rover_return = self.edit_rover_window.update(events)

        if edit_rover_return:
            self.rover_to_display, isNew, saveToDB = edit_rover_return
    
            if isNew:
                self.rover_manager.add_rover(self.rover_to_display)
                option = DropDownItem(self.rover_to_display.rover_id, self.rover_to_display.name)
                self.select_rover_drop_down.add_option(option)
                if saveToDB:
                    create_rover(self.rover_to_display, -1)

            self.selected_rover = self.rover_to_display
            self.rover_to_display = None

        self.stats_window.update(events)

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Help Button Click Handling
                if self.help_button.rect.collidepoint(event.pos):
                    self.show_help_popup = not self.show_help_popup
                    if self.show_help_popup:
                        self.help_popup.show(get_text_file("../text_files/help_desc.txt"))
                    else:
                        self.help_popup.hide()
                    continue # Skip to next event

               
                if not self.pressed_project_dropdown:
                    # prevents pressing tab0 when pressing dropdown
                    for tab in filter(None, self.tab_manager.tabs):
                        if tab.check_click(event.pos) == "select":
                            self.switch_tab(tab.tab_id)
                        elif tab.check_click(event.pos) == "close":
                            self.close_tab(tab.tab_id)
                            print("Closed tab:", tab.tab_id)
                            if self.tab_manager.active_tab_index is not None:
                                print(
                                    "Switching to this tab after closing tab",
                                    self.tab_manager.active_tab_index,
                                )
                                self.switch_tab(self.tab_manager.active_tab_index)
                            else:
                                print("no more tabs")
                                self.active_project = None
                                print(self.projects)
                                self.reset_simulation_window()

                # Add marker when zoomed in
                if current_project and current_project.zoomed_in:
                    mpos = pygame.mouse.get_pos()

                    button_list = [
                        self.confirm_bb,
                        self.reset_bb,
                        self.find_path_btn,
                        self.reset_path_btn,
                        self.find_optimal_path_btn,
                        self.find_ordered_path_btn,
                        self.add_rover_button,
                        self.help_button,
                        # self.restore_window_button,
                        # self.error_button,
                        # self.view_data_button,
                        # self.setting_button,
                        self.edit_rover_window.confirm_button,
                        self.edit_rover_window.close_button,
                        self.reset_pathfind_btn,
                        self.stats_window.close_button,
                    ]

                    if all(not (btn.drawn and btn.rect.collidepoint(mpos)) for btn in button_list):
                        if (self.selected_rover and 
                            not self.edit_rover_window.active and
                            not self.pressed_project_dropdown and
                            not self.show_help_popup and
                            not self.show_load_popup and
                            not self.show_delete_popup and
                            not self.show_save_popup and
                            current_project.map_view.is_within_map(mpos)
                        ):
                            current_project.map_view.add_marker(mpos)

            # if event.type == pygame.VIDEORESIZE:
            #     self.screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)

            if self.show_help_popup:
                self.help_popup.handle_event(event)
                if not self.help_popup.visible:
                    self.show_help_popup = False

            if self.show_load_popup:
                self.load_popup.handle_event(event)
                if not self.load_popup.visible:
                    self.show_load_popup = False

            if self.show_delete_popup:
                self.delete_popup.handle_event(event)
                if not self.delete_popup.visible:
                    self.show_delete_popup = False
            
            if self.show_save_popup:
                self.save_popup.handle_event(event)
                if not self.save_popup.visible:
                    self.show_save_popup = False
                
            if current_project and not current_project.bounding_box_selected:
                if not self.drag.dragging:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_LEFT:
                            current_project.map_view.handle_scroll(100)
                        if event.key == pygame.K_RIGHT:
                            current_project.map_view.handle_scroll(-100)
                coords = current_project.map_view.draw()
                self.drag.update(events, coords)

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.drag.active and not current_project.selection_made:
                        coords = self.drag.get_bounds()
                        if coords is not None:
                            current_project.start_selection(coords)

                elif event.type == pygame.MOUSEMOTION and current_project.selecting_box:
                    if not current_project.selection_made:
                        coords = self.drag.get_bounds()
                        if (
                            coords is not None
                            and coords != current_project.bounding_box
                        ):
                            current_project.update_selection(coords)

                elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    if (
                        current_project.selecting_box
                        and not current_project.selection_made
                    ):
                        if self.drag.start_coord != self.drag.end_coord:
                            current_project.selection_made = True
                        else:
                            print(
                                "Invalid selection: start and end coordinates are the same."
                            )

        self.confirm_bb.update(events)
        self.reset_bb.update(events)
        self.find_optimal_path_btn.update(events)
        self.find_ordered_path_btn.update(events)
        self.reset_pathfind_btn.update(events)
        self.find_path_btn.update(events)
        self.reset_path_btn.update(events)
        self.add_rover_btn.update(events)

        if (self.find_optimal_path_btn.is_clicked or self.find_ordered_path_btn.is_clicked or
            self.reset_pathfind_btn.is_clicked or self.find_path_btn.is_clicked or self.reset_path_btn.is_clicked) :
            self.stats_window.reset()

        if self.confirm_bb.is_clicked and current_project.selection_made:
            current_project.finalize_selection()
            print(
                f"Bounding box set: {current_project.project_id, current_project.bounding_box}"
            )
            current_project.selection_made = False

            xy_top, xy_bot = self.drag.get_bounds()
            self.active_project.map_view.calculate_zoom_pixels(xy_top, xy_bot)
            self.drag.reset()
            self.active_project.zoomed_in = True
            self.confirm_bb.is_clicked = False 

        elif self.reset_bb.is_clicked and current_project.selection_made:
            self.active_project.selection_made = False
            self.active_project.bounding_box = None
            self.drag.start_coord = None
            self.drag.end_coord = None
            self.drag.dragging = False
            self.reset_bb.is_clicked = False

        self.draw_window()
        
        if self.show_help_popup:
            self.help_popup.draw()
        
        if self.show_load_popup:
            self.load_popup.draw()

        if self.show_delete_popup:
            self.delete_popup.draw()

        if self.show_save_popup:
            self.save_popup.draw()



        if self.edit_rover_window.active:
            self.hide_path_buttons()
        else:

            # hide all buttons by default
            self.hide_all_buttons()
            self.add_rover_btn.erase()

            num_markers = 0
            if current_project and current_project.map_view:
                num_markers = len(current_project.map_view.get_markers())

            # draw bounding box buttons
            if current_project and current_project.selection_made:
                self.reset_bb.draw(self.display)
                self.confirm_bb.draw(self.display)
            elif current_project and current_project.bounding_box_selected:
                if not self.selected_rover:
                    # show Add Rover button if no rover is selected and bounding box is set
                    self.add_rover_btn.draw(self.display)
                    if self.add_rover_btn.is_clicked:
                        self.edit_rover_window.active = True
                        self.add_rover_btn.is_clicked = False
                elif not current_project.pathfinding_active:
                    # Show pathfinding buttons if a rover is selected
                    if num_markers == 2:
                        self.find_path_btn.draw(self.display)
                        self.reset_path_btn.draw(self.display)
                        self.hide_selection_buttons()
                    elif num_markers > 2:
                        self.find_optimal_path_btn.draw(self.display)
                        self.find_ordered_path_btn.draw(self.display)

                        if current_project.full_path or num_markers > 0:
                            self.reset_pathfind_btn.draw(self.display)

            # Handle pathfinding button clicks
            if current_project and not current_project.selection_made and self.selected_rover and not current_project.pathfinding_active and current_project.bounding_box_selected:
                if num_markers == 2:
                    if self.find_path_btn.is_clicked:
                        current_project.pathfinding_active = True
                        threading.Thread(target=self.findPath, args=(current_project.map_view.get_markers(), True), daemon=True).start()
                        self.find_path_btn.is_clicked = False
                    if self.reset_path_btn.is_clicked:
                        self.reset_markers_and_path(current_project)
                        self.reset_path_btn.is_clicked = False
                elif num_markers > 2:
                    if self.find_optimal_path_btn.is_clicked:
                        current_project.pathfinding_active = True
                        threading.Thread(target=self.findPath, args=(current_project.map_view.get_markers(), False), daemon=True).start()
                        self.find_optimal_path_btn.is_clicked = False
                    if self.find_ordered_path_btn.is_clicked:
                        current_project.pathfinding_active = True
                        threading.Thread(target=self.findPath, args=(current_project.map_view.get_markers(), True), daemon=True).start()
                        self.find_ordered_path_btn.is_clicked = False
                    if self.reset_pathfind_btn.is_clicked:
                        # check if the button should be active before processing click
                        if current_project.full_path or num_markers > 0:
                            self.reset_markers_and_path(current_project)
                            self.reset_pathfind_btn.is_clicked = False
                        else:
                            self.reset_pathfind_btn.is_clicked = False


        self.pressed_project_dropdown = False

    def on_select_rover(self, rover: DropDownItem):
        pass
        # print(rover.id)
        # self.selected_rover = get_rover_by_id(rover.id)
        # print(self.selected_rover.description)
        
    def display_mars_full_map(self):
        if self.active_project:
            # self.active_project.map_view.draw_start_screen()
            coords = self.active_project.map_view.draw()
            if not self.active_project.bounding_box_selected:
                self.drag.draw(coords)

    def findPath(self, markers, ordered: bool = False):
        # this is for threading
        with self.loading_lock:
            self.is_loading = True
            self.loading_start_time = pygame.time.get_ticks()
        tif_file = "Mars_HRSC_MOLA_BlendDEM_Global_200mp_v2.tif"

        # reading callback
        def terrain_reading_progress(current, total):
            self.update_loading_state(message="Reading Terrain Data", current=current, total=total)

        # intial state before using the callback
        # should be a backup, not usually needed
        self.update_loading_state(message="Reading Terrain Data", current=0, total=1)

        start_pt, rows, cols, path_indices = get_window_for_path(tif_file, markers, 100)

        matrix, _ = dem_to_matrix(
            tif_file,
            start_point=start_pt,
            max_rows=rows,
            max_cols=cols,
            progress_callback=terrain_reading_progress
        )

        # map gen callback
        def map_generation_progress(current, total):
            self.update_loading_state(message="Generating Map", current=current, total=total)

        # intial state before using the callback
        # should be a backup, not usually needed
        self.update_loading_state(message="Generating Map", current=0, total=1)

        map = matrix_to_topo_map(matrix, progress_callback=map_generation_progress)

        print("NUM NODES:", len(map[0]) * len(map))

        mH = MapHandler(map)
        astar = AStar(self.selected_rover.get_heuristics())

        locations = [mH.getLocationAt(r, c) for r, c in path_indices]

        full_path = []
        path_calculation_successful = False
        num_locations = len(locations)

        if num_locations == 0:
            print("No markers provided for pathfinding.")
            path_calculation_successful = False
        elif num_locations == 1:
            print("path is just the start point")
            full_path = [locations[0]]
            path_calculation_successful = True
        elif num_locations == 2:
            print(f"Finding path from {locations[0].printLoc()} to {locations[1].printLoc()}")
            # two-point path calc state
            self.update_loading_state(message="Calculating Path", current=0, total=1)
            # Call goTo directly for two points
            full_path = astar.goTo(locations[0], locations[1], self.selected_rover, mH)
            if full_path:
                self.update_loading_state(current=1)  # Mark as complete
                path_calculation_successful = True
            else:
                print("No path found")
                path_calculation_successful = False
        else:  # path visiting more than 2 points
            start_loc = locations[0]
            visit_locs = locations[1:]
            print(f"Finding path starting at {start_loc.printLoc()} and visiting {len(visit_locs)} other locations.")

            def visit_all_progress_callback(current, total):
                self.update_loading_state(message="Calculating Path Segments", current=current, total=total)

            full_path = astar.visitAll(start_loc, visit_locs, self.selected_rover, mH, progress_callback=visit_all_progress_callback, ordered=ordered)
            if len(full_path) > 1:
                path_calculation_successful = True
            else:
                print(f"Pathfinding failed or could not visit all locations.")
                path_calculation_successful = False

        self.stats_window.set_data(full_path, self.selected_rover, mH, self.active_project)

        if path_calculation_successful:
            reduced_path = full_path[::10]
            print("Full path calculation complete")
            print(f"Path length: {len(reduced_path)} steps")
            self.active_project.full_path = reduced_path
            time.sleep(0.5)  # delay to let the user see that the calculations are done
        else:
            print("Path calculation failed or incomplete.")

        # update state to indicate loading is finished
        with self.loading_lock:
            self.is_loading = False
            self.loading_start_time = None
        if self.active_project:
            self.active_project.pathfinding_active = False
        
        map.clear()
        full_path.clear()

    # Helper functions
    def get_size(self):
        return self.width, self.height
    
    def handle_project_load(self, project: Project):
        print(f"Simulation: Loading project {project.project_id}")
        self.current_project = project
        self.add_new_tab(project)

    def handle_delete_project(self, project: Project):
        print(f"Simulation: Deleting project {project.project_id} from database")
        delete_project(project)
    
    # Buttons for pathfinding
    def reset_markers_and_path(self, project):
        if project and project.map_view:
            project.map_view.reset_markers()
            project.full_path = []

    def hide_path_buttons(self):
        for btn in [self.find_path_btn, self.reset_path_btn, self.find_optimal_path_btn, 
                    self.find_ordered_path_btn, self.reset_pathfind_btn]:
            btn.erase()

    def hide_selection_buttons(self):
        self.reset_bb.erase()
        self.confirm_bb.erase()
        
    def hide_all_buttons(self):
        self.hide_selection_buttons()
        self.hide_path_buttons()
    
    # updates loading state variables
    def update_loading_state(self, message=None, current=None, total=None):
        with self.loading_lock:
            if message is not None:
                self.loading_message = message
            if current is not None:
                self.loading_current = current
            if total is not None:
                self.loading_total = total

    # reads loading state variables
    def get_loading_state(self):
        with self.loading_lock:
            return (
                self.loading_message,
                self.loading_current,
                self.loading_total,
                self.loading_start_time,
            )