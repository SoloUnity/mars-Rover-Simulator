from gui.tab import Tab 
from models.project import Project

class TabManager:
    def __init__(self):
        self.tabs = [None] * 5 # max 5 tabs
        self.active_tab_index = None  

    def add_tab(self, position, project=None):
        if project == None:
            new_project = Project(position)  #create a new project
            new_tab = Tab(new_project, tab_id=position, position=position)
        else:
            new_tab = Tab(project,tab_id=position, position=position)
        self.tabs[position] = new_tab
        self.active_tab_index = position
        self.select_tab(new_tab.tab_id)  

    def handle_event(self, events):
        for event in events:  
            for tab in filter(None, self.tabs):  
                tab.handle_event(event)

    def draw(self, screen):
        for tab in filter(None, self.tabs):
            tab.draw(screen)

    def remove_tab(self, tab_id):
        if not self.tabs:
            return  

        tab_index = next((i for i, tab in enumerate(self.tabs) if tab and tab.tab_id == tab_id), None)

        if tab_index is None:
            return  # Tab ID not found
        self.tabs[tab_index] = None  

        print("Removing tab:", tab_index)
        print("Active tab index before removal:", self.active_tab_index)
      
        if self.active_tab_index == tab_index:
            new_index = None

            for i in range(tab_index - 1, -1, -1):
                if self.tabs[i] is not None:
                    new_index = i
                    break

            if new_index is None:
                for i in range(tab_index + 1, len(self.tabs)):
                    if self.tabs[i] is not None:
                        new_index = i
                        break

            self.active_tab_index = new_index

        print("Tabs after removal:", self.tabs)
        print("Active tab after removal:", self.active_tab_index)

        # """Remove a tab by its ID."""
        # self.tabs = [tab for tab in self.tabs if tab.tab_id != tab_id]

        # # Adjust active tab index if necessary
        # if self.active_tab_index is not None:
        #     if self.active_tab_index >= len(self.tabs):
        #         self.active_tab_index = len(self.tabs) - 1  # Set to last tab
        #     if len(self.tabs) == 0:
        #         self.active_tab_index = None  # No tabs left

        # print(self.tabs)

    def select_tab(self, tab_id):
        for index, tab in enumerate(filter(None, self.tabs)):
            tab.is_selected = (tab.tab_id == tab_id)  # Only the selected tab is set to True
            if tab.tab_id == tab_id:
                self.active_tab_index = tab_id
        print("Selected tab using select_tab: ", self.active_tab_index)
        return

    def get_active_tab(self):
        if self.active_tab_index is not None and 0 <= self.active_tab_index < len(self.tabs):
            return self.tabs[self.active_tab_index]
        return None  # No active tab

    def get_tab_by_id(self, tab_id):
        for tab in self.tabs:
            if tab.tab_id == tab_id:
                return tab
        return None


