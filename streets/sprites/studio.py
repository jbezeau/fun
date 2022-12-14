import pickle
import pygame
from pygame import image
import colours
import sheets

# important measurements
SPRITE_SIZE = (8, 16)
EDITOR_PIXEL = 16
EDITOR_SIZE = (128, 256)
SHEET_SIZE = (1280, 960)
PAINT_SIZE = (80, 32)
STATUS_SIZE = (1280, 32)

# UI colours
COLOUR_KEY = (128, 128, 128)
STATUS_GREEN = (32, 128, 32)
STATUS_YELLOW = (192, 192, 32)
STATUS_RED = (192, 32, 32)
SCREEN_COLOUR = (0, 0, 0)
TEXT_COLOUR = (192, 192, 192)

pygame.init()
pygame.font.init()
font = pygame.font.Font(None, 16)
clock = pygame.time.Clock()
screen = pygame.display.set_mode(SHEET_SIZE)
status = pygame.Surface(STATUS_SIZE)
input_bar = pygame.Surface(STATUS_SIZE)


def draw_status_text(text, colour):
    status_output = font.render(text, True, (0, 0, 0))
    status_rect = status_output.get_rect(centerx=screen.get_width() // 2, centery=16)
    status.fill(colour)
    status.blit(status_output, status_rect)
    screen.blit(status, (0, 0))
    return True


def draw_colour_bar():
    status.fill(SCREEN_COLOUR)
    x = 0
    colour_select = {}
    for c in colours.PALETTE:
        patch = pygame.Surface(PAINT_SIZE)
        patch.fill(c)
        patch_rect = patch.get_rect()
        patch_rect.x = x
        status.blit(patch, (x, 0))
        x += 80
        colour_select[tuple(patch_rect)] = c
    screen.blit(status, (0, 0))
    return colour_select


def draw_input_bar(text, colour):
    display_value = font.render(text, True, (0, 0, 0))
    display_rect = display_value.get_rect(centerx=screen.get_width() // 2, centery=16)
    input_bar.fill(colour)
    input_bar.blit(display_value, display_rect)
    screen.blit(input_bar, (0, screen.get_height()-32))
    return True


def get_text_input(prompt, default):
    typing = True
    if default is not None:
        input_text = default
    else:
        input_text = ''
    while typing:
        clock.tick(60)
        draw_input_bar(f'{prompt}{input_text}', STATUS_GREEN)
        pygame.display.flip()

        for typing_event in pygame.event.get():
            if typing_event.type == pygame.QUIT:
                return None
            if typing_event.type == pygame.KEYDOWN:
                if typing_event.key == pygame.K_BACKSPACE:
                    input_text = input_text[:-1]
                elif typing_event.key == pygame.K_ESCAPE:
                    typing = False
                    input_text = None
                elif typing_event.key == pygame.K_RETURN:
                    typing = False
                else:
                    input_text = input_text + typing_event.unicode
    return input_text


def clear_status_text():
    screen.fill(SCREEN_COLOUR)
    draw_colour_bar()
    pygame.display.flip()
    return False
