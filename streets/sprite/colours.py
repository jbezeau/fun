import pygame

NONE = (128, 128, 128)
GRAY1 = (16, 16, 16)
GRAY2 = (32, 32, 32)
GRAY3 = (48, 48, 48)
WHITE2 = (192, 192, 192)
WHITE1 = (255, 255, 255)
RED_D = (96, 0, 0)
RED = (255, 0, 0)
GRN = (0, 255, 0)
BLUE = (0, 0, 255)
YLW_D = (96, 96, 0)
YLW = (255, 255, 0)
MAG_D = (96, 0, 96)
MAG = (255, 0, 255)
CYAN_D = (0, 96, 96)
CYAN = (0, 255, 255)

PALETTE = [NONE, GRAY1, GRAY2, GRAY3, WHITE2, WHITE1, RED_D, RED, GRN, BLUE, YLW_D, YLW, MAG_D, MAG, CYAN_D, CYAN]


if __name__ == '__main__':
    pygame.init()
    pygame.display.set_caption('Colour Test')
    screen = pygame.display.set_mode((1280, 80))

    x = 0
    for c in PALETTE:
        patch = pygame.Surface((80, 80))
        patch.fill(c)
        screen.blit(patch, (x, 0))
        x += 80
    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                waiting = False
    pygame.quit()
