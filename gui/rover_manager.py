# Noah Lepage
from models.rover import Rover, get_all_rovers

class RoverManager():
    def __init__(self):
        self.selected_rover: Rover = None
        self.rovers: list[Rover] = get_all_rovers()

        self.event_listeners: list[callable] = []

    def call_event(self, name):
        for fn in self.event_listeners:
            fn(name)

    def register_listener(self, fn: callable):
        self.event_listeners.append(fn)

    def add_rover(self, rover: Rover):
        self.rovers.append(rover)
        self.call_event("add_rover")
    
    def get_rovers(self):
        return self.rovers.copy()
    
    def get_rover_by_id(self, id: str):
        for r in self.rovers:
            if r.rover_id == id:
                return r