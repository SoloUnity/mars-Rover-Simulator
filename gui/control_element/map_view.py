import pygame
from utils.paths import REGULAR, get_image
from src.util.dem_to_matrix import dem_to_matrix

pygame.init()

# Constants for UI
TEXT_COLOR = (0, 0, 0)
ERROR_COLOR = (255, 0, 0)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
OFF_WHITE = (217,217,217)
WHITE = (255, 255, 255)
LOGIN_BLUE = (8, 158, 222)
# 8536, 4268
# 1440, 720

class MapView:
    def __init__(self, display, x, y, width, height):
        self.display = display
        self.font = pygame.font.Font(REGULAR, 18)
        self.number_font = pygame.font.Font(REGULAR, 12)
        self.display_offset_x, self.display_offset_y = x, y
        
        self.offset_x, self.offset_y = 0, 0
        self.display_w, self.display_h = width, height
        self.img_width, self.img_height = 1440, 720

        self.marker_icon = pygame.image.load("gui/images/icon_arrow_down.png")
        self.marker_icon = pygame.transform.scale(self.marker_icon, (15, 15))
        self.markers = []  
        self.max_num_markers = 5 
        
        self.static_surface = pygame.Surface((self.display_w, self.display_h))
        self.draw_start_screen()
        
    def get_markers(self):
        """Returns the list of coordinates where markers are placed"""
        return [(lat, lon) for x, y, lat, lon in self.markers]

    def draw_text(self, text, position, color=TEXT_COLOR):
        """Draw text on the screen at a given position with a specified color."""
        text_surface = self.font.render(text, True, color)
        self.display.blit(text_surface, position)
    
    def latlon_to_screen(self, latlon):
        """Convert a (lat, lon) pair into screen‐pixel coordinates of the display."""
        lat, lon = latlon

        # 1. Map to pixel within the *scaled* image
        img_x = ((lon + 180) / 360) * self.img_width
        img_y = ((90 - lat) / 180) * self.img_height

        # 2. Account for pan/offset and the MapView’s position on the window
        screen_x = img_x + self.offset_x + self.display_offset_x
        screen_y = img_y + self.offset_y + self.display_offset_y

        return (int(screen_x), int(screen_y))

    def draw_path(self, path_locs, color=(255,0,0), width=2):
        """
        Given a list of Location objects (with .lat, .lon), or a list of (lat,lon) tuples,
        draw a continuous line between them.
        """
        # build the screen‐pixel list
        pts = []
        for loc in path_locs:
            if hasattr(loc, 'lat') and hasattr(loc, 'lon'):
                latlon = (loc.lat, loc.lon)
            else:
                latlon = loc  # assume it's already a (lat,lon) tuple
            
            screen_pos = self.latlon_to_screen(latlon)
            if screen_pos not in pts:
                pts.append(screen_pos)
        
        # draw a connected line
        if len(pts) >= 2:
            pygame.draw.lines(self.display, color, False, pts, width)

    def draw_start_screen(self):
        bg = pygame.image.load('gui/images/mars.jpg')
        # print(f"Offset X: {self.offset_x}, Offset Y: {self.offset_y}")
        # print(f"Image Size: {self.img_width}x{self.img_height}")


        # Scale the image based on the dynamically updated size
        bg = pygame.transform.scale(bg, (int(self.img_width), int(self.img_height)))

        # Clear the static surface
        self.static_surface.fill(BLACK)

        # Blit the scaled image with the current offset
        self.static_surface.blit(bg, (self.offset_x, self.offset_y))

    def is_within_map(self, pos):
        """Return True if pos is inside this MapView's displayed rectangle."""
        mx, my = pos
        return (
            self.display_offset_x <= mx < self.display_offset_x + self.display_w and
            self.display_offset_y <= my < self.display_offset_y + self.display_h
        )

    def handle_scroll(self, dx):
        new_offset_x = self.offset_x + dx

        if self.display_w - new_offset_x > self.img_width:
            self.offset_x = -(self.img_width - self.display_w)
        elif new_offset_x > 0:
            self.offset_x = 0
        else:
            self.offset_x = new_offset_x

        # Redraw after scrolling
        self.draw_start_screen()
    
    def get_lat_lon(self, pos):
        img_x = pos[0] - self.offset_x - self.display_offset_x
        img_y = pos[1] - self.offset_y - self.display_offset_y

        lat = 90 - (img_y / self.img_height) * 180
        lon = (img_x / self.img_width) * 360 - 180

        return lat, lon

    def add_marker(self, pos):
        if len(self.markers) >= self.max_num_markers:
            return
        
        x = pos[0] - self.marker_icon.get_width() / 2
        y = pos[1] - self.marker_icon.get_height()
           
        lat, lon = self.get_lat_lon((pos[0], pos[1]))
        self.markers.append((x, y, lat, lon))

    def reset_markers(self):
        self.markers = []

    def draw(self):
        self.display.blit(self.static_surface, (self.display_offset_x, self.display_offset_y))

        # Define circle properties
        circle_radius = 8
        vertical_gap = 2 # Gap between top of icon and bottom of circle

        for index, (x, y, _, _) in enumerate(self.markers, start=1):
            # Draw the original marker icon
            self.display.blit(self.marker_icon, (x, y))

            # Calculate circle center position (above the icon)
            icon_width = self.marker_icon.get_width()
            circle_center_x = x + icon_width / 2
            circle_center_y = y - circle_radius - vertical_gap 
            circle_center = (int(circle_center_x), int(circle_center_y))

            # Draw the white circle
            pygame.draw.circle(self.display, WHITE, circle_center, circle_radius)

            # Prepare the number text
            num_text = str(index)
            text_surface = self.number_font.render(num_text, True, BLACK)
            
            # Center the text inside the circle
            # Adjusting y slightly up and left for visual centering
            text_rect = text_surface.get_rect(center=(circle_center[0] - 1, circle_center[1] - 1)) 

            # Draw the number text
            self.display.blit(text_surface, text_rect)

        mouse_pos = pygame.mouse.get_pos()
        
        img_x = mouse_pos[0] - self.offset_x - self.display_offset_x
        img_y = mouse_pos[1] - self.offset_y - self.display_offset_y

        lat = 90 - (img_y / self.img_height) * 180
        lon = (img_x / self.img_width) * 360 - 180

        # Update coords text bottom right
        text_surface = self.font.render(f"{lat}, {lon}", True, OFF_WHITE, TEXT_COLOR)
        self.display.blit(text_surface, (self.display.get_width() - text_surface.get_width(), self.display.get_height() - text_surface.get_height()))

        return (float('%.3f'%lat), float('%.3f'%lon))

    def calculate_zoom_pixels(self, screen_start: tuple, screen_end: tuple):
        orig_w, orig_h = 8536, 4268

        # 1) Convert screen‐space clicks → map‐pane space
        sx1 = screen_start[0] - self.display_offset_x
        sy1 = screen_start[1] - self.display_offset_y
        sx2 = screen_end[0]   - self.display_offset_x
        sy2 = screen_end[1]   - self.display_offset_y

        # 2) Compute the inverse of the current scale
        current_scale = self.img_width / orig_w
        inv_scale     = 1.0 / current_scale

        # 3) Unproject to full‑map pixels
        img_x1 = (sx1 - self.offset_x) * inv_scale
        img_y1 = (sy1 - self.offset_y) * inv_scale
        img_x2 = (sx2 - self.offset_x) * inv_scale
        img_y2 = (sy2 - self.offset_y) * inv_scale

        # 4) Build the image‐space bounding box
        left, right = sorted((img_x1, img_x2))
        top,  bottom= sorted((img_y1, img_y2))
        bw = max(right - left, 1)
        bh = max(bottom - top, 1)

        # 5) New scale so that box fills the map pane:
        scale_x  = self.display_w / bw
        scale_y  = self.display_h / bh
        new_scale= min(scale_x, scale_y)

        # 6) Update the on‐screen size of the full map
        self.img_width  = round(orig_w * new_scale)
        self.img_height = round(orig_h * new_scale)

        # 7) Figure out where that box’s top‐left lands under new_scale
        left_s = left * new_scale
        top_s  = top  * new_scale
        bw_s   = bw   * new_scale
        bh_s   = bh   * new_scale

        # 8) Center the box *inside* the pane
        self.offset_x = round((self.display_w - bw_s) / 2 - left_s)
        self.offset_y = round((self.display_h - bh_s) / 2 - top_s)

        # 9) Redraw
        self.draw_start_screen()


    def calculate_zoom(self, start_lat_long, end_lat_long):
        start_lat, start_lon = start_lat_long
        end_lat, end_lon = end_lat_long
        print(f"Start: ({start_lat}, {start_lon}), End: ({end_lat}, {end_lon})")

        if end_lat is None or end_lon is None:
            # Reset to default view
            self.offset_x, self.offset_y = 0, 0
            self.img_width, self.img_height = 1440, 720  # Reset image size
            self.draw_start_screen()
            return

        # Convert lat/lon to pixel coordinates using full image resolution
        def latlon_to_pixels(lat, lon, img_width, img_height):
            x = ((lon + 180) / 360) * img_width
            y = ((90 - lat) / 180) * img_height
            return x, y

        top_left_x, top_left_y = latlon_to_pixels(start_lat, start_lon, 8536, 4268)
        bot_right_x, bot_right_y = latlon_to_pixels(end_lat, end_lon, 8536, 4268)

        # Calculate the size of the bounding box
        bbox_width_orig = abs(bot_right_x - top_left_x)
        bbox_height_orig = abs(bot_right_y - top_left_y)

        # Compute new scale so that the bounding box fills the MapView display area
        scale_x = self.display_w / bbox_width_orig
        scale_y = self.display_h / bbox_height_orig
        new_scale = min(scale_x, scale_y) # Keep the aspect ratio correct

        # Update the full image dimensions
        self.img_width = 8536 * new_scale
        self.img_height = 4268 * new_scale

        # Compute new bounding box positions in the scaled image
        new_top_left_x = top_left_x * new_scale
        new_top_left_y = top_left_y * new_scale
        new_bot_right_x = bot_right_x * new_scale
        new_bot_right_y = bot_right_y * new_scale

        # Compute offsets to center the bounding box correctly
        bbox_width_scaled = new_bot_right_x - new_top_left_x
        bbox_height_scaled = new_bot_right_y - new_top_left_y

        self.offset_x = (self.display_w - bbox_width_scaled) / 2 - new_top_left_x
        self.offset_y = (self.display_h - bbox_height_scaled) / 2 - new_top_left_y

        # # Set the offsets so that the top-left of the bounding box aligns with the MapView's top-left corner
        # self.offset_x = -top_left_x * new_scale + self.offset_x
        # self.offset_y = -top_left_y * new_scale + self.offset_y

        self.draw_start_screen()


    
        
