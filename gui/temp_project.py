import uuid
from datetime import datetime
from database.db import  get_connection
from gui.control_element.map_view import MapView
import sqlite3

class Project:
    def __init__(self, project_id=None, project_name=None, created_on=None, last_accessed=None, top_left_x=0.0,
        top_left_y=0.0,
        bottom_right_x=100.0,
        bottom_right_y=100.0,map_view=None):

        self.project_id = project_id or str(uuid.uuid4())
        self.project_name = project_name
        self.created_on = created_on or datetime.now()
        self.last_accessed = last_accessed or datetime.now()
        self.top_left_x = top_left_x
        self.top_left_y = top_left_y
        self.bottom_right_x = bottom_right_x
        self.bottom_right_y = bottom_right_y

        self.tab_id = None

        self.bounding_box_selected = False
        self.bounding_box = None  # Stores (x1, y1, x2, y2)
        self.selecting_box = False
        self.start_pos = None
        self.selection_made = False # When the bounding box has been determined but not confirmed
        self.relative_bounding_box = None
        self.zoomed_in = False
        self.pathfinding_active = False
        self.full_path = None

        self.rovers = None

        self.map_view = None

    def save():
        #if project exist in db, update
        #else create new project
        pass

    def delete():
        #if project exist in db, delete
        pass

    def start_selection(self, start_pos):
            self.selecting_box = True
            self.start_pos = start_pos

    def update_selection(self, current_pos):
        
        if self.selecting_box and self.start_pos is not None and current_pos is not None:
            self.bounding_box = (*self.start_pos, *current_pos)  # (x1, y1, x2, y2)
        else:
            print(f"Invalid selection: start_pos={self.start_pos}, current_pos={current_pos}")
        
    def finalize_selection(self):
        # check if start and end coord are not equal
        if self.bounding_box:
            self.bounding_box_selected = True
            self.selecting_box = False
            print(f"Final bounding box: {self.bounding_box}")  # Debugging
        else:
            print("Warning: No bounding box selected before finalizing!")

