#Author Mathilde Peruzzo

import pygame
from gui.control_element.button import Button
from gui.control_element.drop_down import DropDown
from gui.control_element.slider import Slider
from utils.paths import REGULAR, get_image, get_text_file
from models.rover import Rover
from src.statistics.statistics import *
from src.ai_algos.distances import *

class StatsDisplay :
    def __init__(self, display, path = None, rover = None, mapHandler=None):
        self.display = display

        self.stats = {}

        self.active = False
        self.font_20 = pygame.font.Font(REGULAR, 20)
        self.font_15 = pygame.font.Font(REGULAR, 15) 
        self.font_10 = pygame.font.Font(REGULAR, 12)

        box_width = 500
        box_height = 370
        start_x = (display.get_width() - box_width) // 2
        start_y = (display.get_height() - box_height) // 2
        self.rect = pygame.Rect(start_x, start_y, box_width, box_height)

        BORDER_RADIUS = 3
        UI_H = 20
        UI_W = 150
        FONT = pygame.font.Font(REGULAR, 12)
        CLOSE_ICON = pygame.image.load(get_image('icon_close.png'))
        self.close_button = Button("Close", (65, 71, 82), "orange", FONT, "white", \
                BORDER_RADIUS, self.rect.x + self.rect.width - 40, self.rect.y + 5, 25, UI_H, CLOSE_ICON, 0.8)

    def toggle_popup(self):
            self.active = not self.active

    def draw(self, display, project):
        if not self.active or project not in self.stats:
            return
        
        pygame.draw.rect(display, (30,33,38), self.rect, border_radius=2)  
        pygame.draw.rect(display, (65, 71, 82), self.rect, 1,border_radius=2)

        self.close_button.draw(self.display)

        x_offset = self.rect.x + 20
        y_offset = 20
        y_offset = self.draw_rover_stats(display, x_offset,  y_offset, self.stats[project][0]) + 10
        self.draw_path_stats(display, x_offset, y_offset, project)

    def update(self, events):
        if not self.active:
            return
        
        self.close_button.update(events)

        if self.close_button.is_clicked:
            self.close_button.is_clicked = False
            self.active = False

    def reset(self) :
        self.active = False

    def set_data(self, path, rover, mapHandler, project) :
        path_length_e = path_length(path, euclidean_distance)
        path_length_g = path_length(path, geographical_distance)

        path_avg_alt = path_avg_altitude(path)
        path_avg_alt_chng = path_avg_altitude_change(path)
        path_sun_exp = path_solar_exposure(path, mapHandler)
        path_en = path_energy(path, rover)

        path_time = path_length_e / (1000 * rover.top_speed)

        self.stats[project] = [rover, path_length_e, path_length_g, path_avg_alt, \
                                path_avg_alt_chng, path_en, path_sun_exp, path_time]

    def draw_rover_stats(self, display, x_offset, y_offset, rover) :
        text = self.font_15.render("Rover Statistics", True, "white")
        display.blit(text, (x_offset, self.rect.y + y_offset))
        y_offset += 25

        text = self.font_10.render("Name : {n}".format(n=rover.name), True, "white")
        display.blit(text, (x_offset, self.rect.y + y_offset))
        y_offset += 20

        text = self.font_10.render("Max incline = {mi} °".format(mi=rover.max_incline), True, "white")
        display.blit(text, (x_offset, self.rect.y + y_offset))
        y_offset += 20

        text = self.font_10.render("Low slope energy = {e} kWh".format(e=rover.lowSlopeEnergy), True, "white")
        display.blit(text, (x_offset, self.rect.y + y_offset))
        y_offset += 20

        text = self.font_10.render("Mid slope energy = {e} kWh".format(e=rover.midSlopeEnergy), True, "white")
        display.blit(text, (x_offset, self.rect.y + y_offset))
        y_offset += 20

        text = self.font_10.render("High slope energy = {e} kWh".format(e=rover.highSlopeEnergy), True, "white")
        display.blit(text, (x_offset, self.rect.y + y_offset))
        y_offset += 20

        text = self.font_10.render("Top speed = {s} km/h".format(s=rover.highSlopeEnergy), True, "white")
        display.blit(text, (x_offset, self.rect.y + y_offset))
        y_offset += 20

        return y_offset

    def draw_path_stats(self, display, x_offset,  y_offset, project) :
        text = self.font_15.render("Path Statistics", True, "white")
        display.blit(text, (x_offset, self.rect.y + y_offset))
        y_offset += 25

        text = self.font_10.render("Path length = {l:.2f} meters  using euclidean distance".format(l=self.stats[project][1]), True, "white")
        display.blit(text, (x_offset, self.rect.y + y_offset))
        y_offset += 20

        text = self.font_10.render("Path length = {l:.2f} meters  using geographical distance".format(l=self.stats[project][2]), True, "white")
        display.blit(text, (x_offset, self.rect.y + y_offset))
        y_offset += 20

        text = self.font_10.render("Average altitude = {a:.2f} meters".format(a=self.stats[project][3]), True, "white")
        display.blit(text, (x_offset, self.rect.y + y_offset))
        y_offset += 20

        text = self.font_10.render("Average altitude variation between data points = {c:.2f} meters".format(c=self.stats[project][4]), True, "white")
        display.blit(text, (x_offset, self.rect.y + y_offset))
        y_offset += 20

        text = self.font_10.render("Energy consumption = {e:.2f} kWh".format(e=self.stats[project][5]), True, "white")
        display.blit(text, (x_offset, self.rect.y + y_offset))
        y_offset += 20

        text = self.font_10.render("Solar exposure = {s:.2f} %".format(s=self.stats[project][6]), True, "white")
        display.blit(text, (x_offset, self.rect.y + y_offset))
        y_offset += 20

        text = self.font_10.render("Minimum time required = {t:.2f} hours".format(t=self.stats[project][7]), True, "white")
        display.blit(text, (x_offset, self.rect.y + y_offset))
