# Author: Gordon Ng

import pygame
from utils.paths import REGULAR

# Colours
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DIM_COLOR = (0, 0, 0, 180)
PROGRESS_BAR_COLOR = (0, 122, 204)
PROGRESS_BAR_BG_COLOR = (50, 50, 50)

# Fonts
pygame.font.init()
LOADING_FONT = pygame.font.Font(REGULAR, 20)
PROGRESS_FONT = pygame.font.Font(REGULAR, 16)
TIME_FONT = pygame.font.Font(REGULAR, 14)

def draw_loading_screen(display, message, current=None, total=None, start_time=None):

    center_x, center_y = display.get_rect().center
    content_width = 400 

    # Adjust height based on whether progress bar and time are shown
    content_height = 60
    has_progress = current is not None and total is not None and total > 0
    has_timer = start_time is not None

    if has_progress:
        content_height += 40  # Space for progress bar and its text
    if has_timer:
        content_height += 20  # Space for timer text

    # box for content
    bg_rect = pygame.Rect(0, 0, content_width, content_height)
    bg_rect.center = (center_x, center_y)
    pygame.draw.rect(display, (30, 30, 30), bg_rect, border_radius=5)
    pygame.draw.rect(display, (80, 80, 80), bg_rect, width=1, border_radius=5)

    # loading text
    text_surface = LOADING_FONT.render(message, True, WHITE)
    text_rect_in_box = text_surface.get_rect(centerx=bg_rect.centerx, top=bg_rect.top + 10)
    display.blit(text_surface, text_rect_in_box)

    # Progress Bar
    progress_bar_y = text_rect_in_box.bottom + 10
    progress_text_rect = None
    if has_progress:
        progress_bar_width = content_width - 40
        progress_bar_height = 20
        progress_bar_x = bg_rect.left + 20

        progress = min(1.0, max(0.0, current / total))
        filled_width = int(progress_bar_width * progress)

        pygame.draw.rect(display, PROGRESS_BAR_BG_COLOR, (progress_bar_x, progress_bar_y, progress_bar_width, progress_bar_height), border_radius=3)
        if filled_width > 0:
            pygame.draw.rect(display, PROGRESS_BAR_COLOR, (progress_bar_x, progress_bar_y, filled_width, progress_bar_height), border_radius=3)

        progress_text = f"{int(progress * 100)}% ({current}/{total})"
        progress_text_surface = PROGRESS_FONT.render(progress_text, True, WHITE)
        progress_text_rect = progress_text_surface.get_rect(centerx=bg_rect.centerx, top=progress_bar_y + progress_bar_height + 5)
        display.blit(progress_text_surface, progress_text_rect)

    # Elapsed Time
    if has_timer:
        elapsed_ticks = pygame.time.get_ticks() - start_time
        elapsed_seconds = elapsed_ticks / 1000.0
        time_text = f"Elapsed Time: {elapsed_seconds:.1f}s"
        time_surface = TIME_FONT.render(time_text, True, WHITE)

        time_text_top = (progress_text_rect.bottom + 5) if progress_text_rect else (text_rect_in_box.bottom + 10)
        time_rect = time_surface.get_rect(centerx=bg_rect.centerx, top=time_text_top)
        display.blit(time_surface, time_rect)
