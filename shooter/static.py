import pygame
import math

SPACE = (0, 0, 0)
ENEMY = (192, 128, 64)
PLAYER = (64, 128, 192)
SHIP = (128, 64, 192)
OBSTACLE = (64, 64, 64)
SHADOW = (32, 32, 32)

ENEMY_BULLET = (255, 192, 128)
PLAYER_BULLET = (128, 192, 255)


def direction(pos, destination):
    px, py = pos
    dx, dy = destination
    diff_x = dx - px
    diff_y = dy - py
    dist = 1 + distance(pos, destination)
    return diff_x/dist, diff_y/dist


def distance(pos, destination):
    # pythagoras would have a lot to say to me about this
    px, py = pos
    dx, dy = destination
    diff_x = dx - px
    diff_y = dy - py
    return math.sqrt(diff_x**2 + diff_y**2)


def check_bounds(obj):
    # allow stuff to be mostly off-screen without killing it
    if not screen.get_rect().colliderect(obj.rect):
        obj.kill()
        del obj


pygame.init()
pygame.font.init()
screen = pygame.display.set_mode((1280, 960))
