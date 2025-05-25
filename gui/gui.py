from os import environ
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
import pygame
import sys
import os
from gui.states.login import Login
from gui.states.simulation import Simulation
from gui.states.state_manager import ProgramStateManager
from utils.paths import REGULAR, get_image

class Program:
    def __init__(self):
        self.FPS = 120
        self.SCREENWIDTH, self.SCREENHEIGHT = 1280, 720
        self.LOGIN_WIDTH = 600
        self.LOGIN_HEIGHT = 700
        os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"
        
        pygame.init()
        self.screen = pygame.display.set_mode((self.SCREENWIDTH, self.SCREENHEIGHT))
        pygame.display.set_caption('Mars Pathfinding Simulator')
        
        # Load and set the application icon
        app_icon = pygame.image.load(get_image('logo_icon.png'))
        pygame.display.set_icon(app_icon)

        self.FONT = pygame.font.Font(REGULAR, 18)
        
        self.clock = pygame.time.Clock()
        # self.programStateManager = ProgramStateManager('login')
        self.programStateManager = ProgramStateManager('simulation')
        self.login = Login(self.screen, self.programStateManager)
        self.simulation = Simulation(self.screen, self.programStateManager)

        # self.states = {'login': self.login, 'simulation': self.simulation}
        self.states = {'simulation': self.simulation}
        self.fullscreen = False

    def run(self):
        last_state = None # track last state to avoid unnecessary updates

        while True:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            current_state = self.programStateManager.get_state()
            

            if current_state != last_state:
                if current_state == 'simulation':
                    self.screen = pygame.display.set_mode((self.SCREENWIDTH, self.SCREENHEIGHT))
                # elif current_state == 'login':
                #     self.screen = pygame.display.set_mode((self.SCREENWIDTH, self.SCREENHEIGHT))

                last_state = current_state # Update last_state to prevent unnecessary updates

            self.states[current_state].run(events)
            pygame.display.update()
            self.clock.tick(self.FPS)
