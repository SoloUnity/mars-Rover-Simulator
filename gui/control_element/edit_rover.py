import pygame
from gui.control_element.button import Button
from gui.control_element.drop_down import DropDown, DropDownItem
from gui.control_element.text_input import TextInput
from gui.control_element.slider import Slider
from gui.control_element.checkbox import Checkbox
from gui.rover_manager import RoverManager
from models import rover, presets
from models.rover import Rover
from utils.paths import REGULAR, get_image, get_text_file
from src.ai_algos.heuristics import *
from gui.utils import wrap_text
from typing import Callable

class EditRover:
    def __init__(self, display, rover_manager: RoverManager):

        # Edit Rover Window Fields
        self.display = display
        self.rover: Rover = None
        self.rover_manager = rover_manager
        self.rover_manager.register_listener(self.rover_manager_event)
        self.is_new_rover = False

        self.active = False  # Whether the popup is active
        self.prev_active = False
        self.font_20 = pygame.font.Font(REGULAR, 20)
        self.font_15 = pygame.font.Font(REGULAR, 15)
        self.font_14 = pygame.font.Font(REGULAR, 14)
        self.font_10 = pygame.font.Font(REGULAR, 12) 
        self.error_message = None

        self.distance_method = None

        self.dist_val = 0

        self.as_val = 0
        self.lap_val = 0
        self.se_val = 0
        self.ee_val = 0
        self.le_val = 0

        self.heuristic_offset_y = 20

        self.rover_attributes = {}
        if self.rover:
            for attr, value in vars(self.rover).items():
                self.rover_attributes[attr] = str(value)  # Store as strings

        # Windows dimensions
        algo_rect_width = 400
        rov_rect_width = 600
        box_height = 600
        spacing = 10  # Space between the boxes
        total_width = algo_rect_width + rov_rect_width + spacing

        # Calculate x positions to center both windows
        start_x = (display.get_width() - total_width) // 2

        # Define rectangles for the two windows
        self.algorithm_rect = pygame.Rect(start_x, (display.get_height() - box_height) // 2, algo_rect_width, box_height)
        self.rover_rect = pygame.Rect(start_x + algo_rect_width + spacing, (display.get_height() - box_height) // 2, rov_rect_width, box_height)


        # Setting the  for UI elements
        # COLOR_UI_INACTIVE = (30,33,38)
        COLOR_UI_INACTIVE = (65, 71, 82)
        COLOR_UI_ACTIVE = "orange"
        TEXT_COLOR = "white"
        BORDER_RADIUS = 3
        UI_H = 20
        UI_W = 150
        FONT = pygame.font.Font(REGULAR, 12)
        
        # Special case for smaller open/close
        ICON_W = 25
        CLOSE_ICON = pygame.image.load(get_image('icon_close.png'))
        CONFIRM_ICON = pygame.image.load(get_image('icon_error.png'))
        
        ########## Top Title Bar #############3

        self.close_button = Button("Close", COLOR_UI_INACTIVE, COLOR_UI_ACTIVE, FONT, TEXT_COLOR, BORDER_RADIUS, self.algorithm_rect.x + self.algorithm_rect.width - 40, self.algorithm_rect.y + 5, ICON_W, UI_H, CLOSE_ICON, 0.8)
        self.confirm_button = Button("Confirm", COLOR_UI_INACTIVE, COLOR_UI_ACTIVE, FONT, TEXT_COLOR, BORDER_RADIUS, self.algorithm_rect.x + self.algorithm_rect.width - 100, self.algorithm_rect.y + self.algorithm_rect.height - 30, 80, UI_H)
        
        rover_name_text = self.font_10.render("Rover Name:", True, "white")
        display.blit(rover_name_text, (self.algorithm_rect.x + 9, self.confirm_button.rect.y + 3))
        self.name_input = TextInput(FONT, self.algorithm_rect.x + rover_name_text.get_width() + 15, self.confirm_button.rect.y, 150, 20)

        self.save_checkbox = Checkbox(self.confirm_button.rect.x, self.confirm_button.rect.y - self.confirm_button.rect.height, 15, FONT, label="Save to DB")

        
        ####### Rover Selection Section ##########

        ROVER_OPTIONS = ["Curiosity","Perseverance", "Lunokhod1", "Lunokhod2"]
        self.rover_drop_down = DropDown("Presets", ROVER_OPTIONS, self.on_select_rover, COLOR_UI_INACTIVE, COLOR_UI_ACTIVE, COLOR_UI_INACTIVE, COLOR_UI_ACTIVE,FONT, TEXT_COLOR, 5, self.algorithm_rect.x + 30, self.algorithm_rect.y + 70, UI_W, UI_H, 150, scroll_icon_actif=True, show_selected_as_title=True)

        options = []
        for r in self.rover_manager.get_rovers():
            options.append(DropDownItem(r.rover_id, r.name))
        self.existing_rovers: list[Rover] = options
        self.exisiting_rovers_dropdown = DropDown("Rovers", self.existing_rovers, self.on_select_existing_rover, COLOR_UI_INACTIVE, COLOR_UI_ACTIVE, COLOR_UI_INACTIVE, COLOR_UI_ACTIVE,FONT, TEXT_COLOR, 5, self.algorithm_rect.x + 230, self.algorithm_rect.y + 70, UI_W, UI_H, 150, scroll_icon_actif=True, show_selected_as_title=True)

        ####### Heuristics Selection Section ##########

        SLIDER_X = self.algorithm_rect.x + 200

        DISTANCE_OPTIONS = ["Euclidean","Manhattan","Geographical"]
        self.distance_dropdown = DropDown("Distance", DISTANCE_OPTIONS, self.on_select_distance, COLOR_UI_INACTIVE, COLOR_UI_ACTIVE, COLOR_UI_INACTIVE, COLOR_UI_ACTIVE, FONT, TEXT_COLOR, 5, self.algorithm_rect.x + 30, self.algorithm_rect.y + 210, UI_W, UI_H, 150, scroll_icon_actif=True, show_selected_as_title=True)
        self.dist_slider = Slider(0.01, COLOR_UI_INACTIVE, TEXT_COLOR, COLOR_UI_ACTIVE, SLIDER_X, self.algorithm_rect.y + 210, 100, 15)    

        self.AS_slider = Slider(0.01, COLOR_UI_INACTIVE, TEXT_COLOR, COLOR_UI_ACTIVE, SLIDER_X, self.algorithm_rect.y + 260 + self.heuristic_offset_y, 100, 15)
        self.SE_slider = Slider(0.01, COLOR_UI_INACTIVE, TEXT_COLOR, COLOR_UI_ACTIVE, SLIDER_X, self.algorithm_rect.y + 280 + self.heuristic_offset_y, 100, 15)
        self.EE_slider = Slider(0.01, COLOR_UI_INACTIVE, TEXT_COLOR, COLOR_UI_ACTIVE, SLIDER_X, self.algorithm_rect.y + 300 + self.heuristic_offset_y, 100, 15)
        self.LE_slider = Slider(0.01, COLOR_UI_INACTIVE, TEXT_COLOR, COLOR_UI_ACTIVE, SLIDER_X, self.algorithm_rect.y + 320 + self.heuristic_offset_y, 100, 15)

        self.h_to_slider_map: dict[str, Slider] = {
            "euclidean_distance_h": self.dist_slider,
            "manhattan_distance_h": self.dist_slider,
            "geographical_distance_h": self.dist_slider,
            "stable_altitude_h": self.AS_slider,
            "has_sunlight_obstacle_h": self.SE_slider,
            "energy_for_slope_h": self.EE_slider,
            "low_altitude_h": self.LE_slider
        }

        self.dist_to_option: dict[str, str] = {
            "euclidean_distance_h": "Euclidean",
            "manhattan_distance_h": "Manhattan",
            "geographical_distance_h": "Geographical"
        }

################# Helper Functions ############################

    def toggle_popup(self):
        self.active = not self.active
    
    def load_preset(self, rover_name):
        match rover_name:
            case "Curiosity":
                return presets.create_curiosity()
            case "Perseverance":
                return presets.create_perseverance()
            case "Lunokhod2":
                return presets.create_lunokhod2()
            case "Lunokhod1":
                return presets.create_lunokhod1()
            case "Custom":
                new_rover = Rover()
                return new_rover
            
    def set_rover_attributes(self, rover: Rover=None):
        """Updates the displayed attributes when a new rover is selected."""
        excluded = ["heuristics", "distance_method"]
        if rover:
            self.rover = rover  # Set the new rover
        if self.rover:
            self.rover_attributes = {attr: str(value) for attr, value in vars(self.rover).items() if attr not in excluded}
            self.name_input.set_text(self.rover.name)
        else:
            self.rover_attributes = {}  # Clear attributes if no rover is set
    
    def set_heuristic_sliders(self, heuristics: list[tuple[float, callable]]):
        for value, h in heuristics:
            self.h_to_slider_map[h.__name__].set_value(value)

    def set_dist_dropdown(self, dist_fn):
        title = self.dist_to_option[dist_fn.__name__]
        self.distance_dropdown.set_title(title)

    def rover_manager_event(self, event_name):
        if event_name != "add_rover":
            return
        
        self.existing_rovers = self.rover_manager.get_rovers()
        options = []
        for r in self.existing_rovers:
            options.append(DropDownItem(r.rover_id, r.name))

        self.exisiting_rovers_dropdown.set_options(options)

    def set_distance_method(self, distance_name):
        match distance_name:
            case "Euclidean":
                self.distance_method = euclidean_distance_h
            case "Manhattan":
                self.distance_method = manhattan_distance_h
            case "Geographical":
                self.distance_method = geographical_distance_h

    def get_distance_method(self):
        name = self.distance_dropdown.name
        if name == "Euclidean":
            return euclidean_distance_h
        elif name == "Geographical":
            return geographical_distance_h
        return manhattan_distance_h

    def get_heuristics(self):
        h = [
            (self.dist_val, self.distance_method),
            (self.as_val, stable_altitude_h),
            (self.se_val, has_sunlight_obstacle_h),
            (self.ee_val, energy_for_slope_h),
            (self.le_val, low_altitude_h)
        ]
        
        return [(w, fn) for w, fn in h if w != 0]
    
    def reset(self, keep_dropdown=None):
        """Resets all fields to their default values."""
        self.rover = None
        self.distance_method = None
        self.error_message = None
        
        # Reset heuristic values
        self.dist_val = 0
        self.as_val = 0
        self.lap_val = 0
        self.se_val = 0
        self.ee_val = 0
        self.le_val = 0

        # Reset rover attributes
        self.rover_attributes = {}
        self.name_input.set_text("")

        # Reset UI elements
        self.distance_dropdown.reset()
        if not keep_dropdown or keep_dropdown != "presets":
            self.rover_drop_down.reset()  # No rover selected
        if not keep_dropdown or keep_dropdown != "existing":
            self.exisiting_rovers_dropdown.reset()
        self.dist_slider.reset()
        self.AS_slider.reset()
        self.SE_slider.reset()
        self.EE_slider.reset()
        self.LE_slider.reset()
        self.save_checkbox.checked = False
    
    # Check for the presence of all field and more before being able to press confirm
    def get_error_message(self):
        if not self.rover:
            return "You must select a rover"
        
        if not self.distance_method:
            return "You must select a Main Distance Method"

        if self.dist_val == 0 :
            return "The weight for the distance method must be positive"
        
        return ""
    
    def on_select_rover(self, rover: DropDownItem):
        self.reset("presets")
        preload_rover = self.load_preset(rover.name)
        # self.rover_manager.add_rover(preload_rover)
        self.set_rover_attributes(preload_rover)  # Update displayed attributes
        self.is_new_rover = True

        self.distance_dropdown.enable()
        self.dist_slider.enable()
        self.AS_slider.enable()
        self.EE_slider.enable()
        self.LE_slider.enable()
        self.SE_slider.enable()
        self.name_input.enable()
        self.save_checkbox.enable()

    def on_select_existing_rover(self, roverItem: DropDownItem):
        self.reset("existing")
        rover = self.rover_manager.get_rover_by_id(roverItem.id)
        self.set_rover_attributes(rover)
        
        self.distance_dropdown.disable()
        self.dist_slider.disable()
        self.AS_slider.disable()
        self.EE_slider.disable()
        self.LE_slider.disable()
        self.SE_slider.disable()
        self.name_input.disable()
        self.save_checkbox.disable()

        self.set_heuristic_sliders(rover.get_heuristics())

        dist_method_fn = rover.get_distance_method()
        self.set_dist_dropdown(dist_method_fn)
        self.set_distance_method(self.dist_to_option[dist_method_fn.__name__])
        self.is_new_rover = False

    def on_select_distance(self, distance: DropDownItem):
        self.set_distance_method(distance.name)

    def update(self, events):
        if not self.active:
            return
        
        # If the popup just got activated, reset all values
        if not self.prev_active and self.active:
            self.reset()
        
        self.save_checkbox.update(events)
        self.name_input.update(events)
        self.close_button.update(events)
        self.confirm_button.update(events)
        self.dist_val = self.dist_slider.update(events)
        self.as_val = self.AS_slider.update(events)
        self.se_val = self.SE_slider.update(events)
        self.ee_val = self.EE_slider.update(events)  
        self.le_val = self.LE_slider.update(events)      

        self.rover_drop_down.update(events)
        self.exisiting_rovers_dropdown.update(events)
        self.distance_dropdown.update(events)
        
        if self.close_button.is_clicked:
            self.close_button.is_clicked = False
            self.active = False

        if self.confirm_button.is_clicked:
            self.confirm_button.is_clicked = False
            error_message = self.get_error_message()
            if error_message:
                self.error_message = error_message
                return
            
            self.active = False
            self.prev_active = False

            h = self.get_heuristics()
            d = self.get_distance_method()
            self.rover.set_heuristics(h)
            self.rover.set_distance_method(d)
            self.rover.name = self.name_input.text
            return self.rover, self.is_new_rover, self.save_checkbox.checked

        self.prev_active = self.active



################# Operation Functions ############################


    def draw(self, display):
        """Draws the popup window with both boxes."""
        if not self.active:
            return

        # Draw thick main popup box
        pygame.draw.rect(display, (30,33,38), self.algorithm_rect, border_radius=2)  
        pygame.draw.rect(display, (65, 71, 82), self.algorithm_rect, 1,border_radius=2)

        # Draw lean side box
        pygame.draw.rect(display, (30,33,38), self.rover_rect,border_radius=2)
        pygame.draw.rect(display, (65, 71, 82), self.rover_rect, 1, border_radius=2)


        #Horizontal lines
        #Title Bar
        pygame.draw.line(display, (65, 71, 82), (self.algorithm_rect.x, self.algorithm_rect.y + 30), (self.algorithm_rect.x + self.algorithm_rect.w, self.algorithm_rect.y + 30), 1)

        #Rover Bar
        pygame.draw.line(display, (65, 71, 82), (self.algorithm_rect.x, self.algorithm_rect.y + 135), (self.algorithm_rect.x + self.algorithm_rect.w, self.algorithm_rect.y + 135), 1)

        #Algorithm Bar
        pygame.draw.line(display, (65, 71, 82), (self.algorithm_rect.x, self.algorithm_rect.y + self.algorithm_rect.h - 60), (self.algorithm_rect.x + self.algorithm_rect.w, self.algorithm_rect.y + self.algorithm_rect.h - 60), 1)

        TEXT_TITLE = self.font_15.render("Rover Settings", True, "white")  
        display.blit(TEXT_TITLE, (self.algorithm_rect.x + 9, self.algorithm_rect.y + 5)) 

        TEXT_ROVER_SELECTION = self.font_20.render("Create Rover", True, "white")  
        display.blit(TEXT_ROVER_SELECTION, (self.algorithm_rect.x + 30, self.algorithm_rect.y + 40)) 

        TEXT_ROVER_SELECTION = self.font_20.render("Existing Rovers", True, "white")  
        display.blit(TEXT_ROVER_SELECTION, (self.algorithm_rect.x + 230, self.algorithm_rect.y + 40)) 

        rover_name_text = self.font_10.render("Rover Name:", True, "white")
        display.blit(rover_name_text, (self.algorithm_rect.x + 9, self.confirm_button.rect.y + 3))

        x_offset = self.rover_rect.x + 20
        y_offset = self.rover_rect.y + 20
        line_width = 500
        
        for attr, value in self.rover_attributes.items():
            text = f"{attr}: {value}"
            lines = wrap_text(text, self.font_15, line_width)

            # render each wrapped line
            for line in lines:
                surf = self.font_14.render(line, True, pygame.Color('white'))
                display.blit(surf, (x_offset, y_offset))
                y_offset += self.font_14.get_linesize()

            # add spacing before the next attribute block
            y_offset += 25 - self.font_15.get_linesize()

        self.save_checkbox.draw(self.display)
        self.close_button.draw(self.display)
        self.confirm_button.draw(self.display)
        self.name_input.draw(self.display)

        x = self.algorithm_rect.x + 30

        # Section Headers Display
        heuristics_text = self.font_20.render("Heuristics", True, "white")  
        display.blit(heuristics_text, (x, self.algorithm_rect.y + 150))

        distance_astar_calc_text = self.font_15.render("Main Distance Method", True, "white")
        display.blit(distance_astar_calc_text, (x, self.algorithm_rect.y + 180))
        
        self.rover_drop_down.draw(self.display)
        self.exisiting_rovers_dropdown.draw(self.display)
        
        y = self.algorithm_rect.y + 250 + self.heuristic_offset_y
        self.dist_slider.draw(self.display)
        val_text = self.font_15.render(str(self.dist_val), True, "white")
        display.blit(val_text, (self.dist_slider.rect.x + 110, self.dist_slider.rect.y))
    
        other_heuristics = [
            {
                "name": "Altitude Stability",
                "slider": self.AS_slider,
                "value": self.as_val 
            },
            {
                "name": "Solar Exposure",
                "slider": self.SE_slider,
                "value": self.se_val
            },
            {
                "name": "Energy Efficiency",
                "slider": self.EE_slider,
                "value": self.ee_val 
            },
            {
                "name": "Low altitude",
                "slider": self.LE_slider,
                "value": self.le_val 
            }
        ]
        
        y = self.algorithm_rect.y + 260 + self.heuristic_offset_y
        self.draw_sliders(display, other_heuristics, x, y)

        self.distance_dropdown.draw(display)
        
        if hasattr(self, 'error_message') and self.error_message:
            y_offset = self.algorithm_rect.y + 450
            lines = wrap_text(self.error_message, self.font_15, 300)
            for line in lines:
                surf = self.font_15.render(line, True, pygame.Color('orange'))
                display.blit(surf, (self.algorithm_rect.x + 40, y_offset))
                y_offset += self.font_15.get_linesize()

    def draw_sliders(self, display, heuristics, x, y, x_offset=110, y_offset=20):
        for heuristic in heuristics:
            name_text = self.font_10.render(heuristic["name"], True, "white")
            display.blit(name_text, (x, y))
            
            slider = heuristic["slider"]
            slider.draw(self.display)
            val_text = self.font_15.render(str(heuristic["value"]), True, "white")
            display.blit(val_text, (slider.rect.x + x_offset, y))
            
            y += y_offset