import glob
import pickle
import pygame
from pygame import image
from sprite import sprites


CHARACTER_SIZE = (64, 128)
SCREEN_SIZE = (960, 960)
BLACK = (0, 0, 0)
GRAY = (96, 96, 96)


def load_animations():
    sheet_list = glob.glob('sprite/*.png')
    animation_set = {}
    for filename in sheet_list:
        sheet_image = image.load(filename)
        metaname = filename[:-3]+'meta'
        pickle_file = open(metaname, 'rb')
        sheet_meta = pickle.load(pickle_file)
        pickle_file.close()

        sheet_animations = {}
        tag_list = list(sheet_meta.values())
        pos_list = list(sheet_meta.keys())
        for index in range(len(tag_list)):
            sprite_series = sheet_animations.get(tag_list[index])
            if not sprite_series:
                sprite_series = []
                sheet_animations[tag_list[index]] = sprite_series
            lil_pic = pygame.Surface(sprites.SPRITE_SIZE)
            lil_pic.blit(sheet_image, (0, 0), pos_list[index])
            new_sprite = pygame.transform.scale(lil_pic, CHARACTER_SIZE)
            sprite_series.append(new_sprite)
        animation_set[filename[:-4]] = sheet_animations
    return animation_set


class Obstacle(pygame.sprite.Sprite):
    def __init__(self, pos, size):
        super(Obstacle, self).__init__()
        self.image = pygame.Surface(size)
        self.image.fill(GRAY)
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = pos


class Actor(pygame.sprite.Sprite):
    def __init__(self):
        super(Actor, self).__init__()
        self.image = pygame.Surface(CHARACTER_SIZE)
        self.image.fill(sprites.COLOUR_KEY)
        self.rect = self.image.get_rect()
        self.vel_x = 0
        self.vel_y = 0

    def update(self):
        self.rect.x += self.vel_x
        self.rect.y += self.vel_y
        self.vel_y += 1


class Model(Actor):
    def __init__(self, default_a):
        super(Model, self).__init__()
        self.a_frame = 0
        self.a_speed = 0.1
        self.a_images = default_a

    def update(self):
        super(Model, self).update()
        self.a_frame = (self.a_frame + self.a_speed) % len(self.a_images)
        frame_image = self.a_images[int(self.a_frame)]
        self.image = pygame.transform.scale(frame_image, CHARACTER_SIZE)
        self.image.set_colorkey(sprites.COLOUR_KEY)


class Character(Model):
    def __init__(self, pos, animation):
        super(Character, self).__init__(animation)
        self.rect.x, self.rect.y = pos


if __name__ == '__main__':
    animations = load_animations()
    print(animations)

    pygame.init()
    pygame.font.init()
    clock = pygame.time.Clock()
    pygame.display.set_mode(SCREEN_SIZE)
    pygame.display.set_caption('Character Test')
    screen = pygame.display.set_mode(SCREEN_SIZE)

    test_sheet = animations.get('sprite/test_sheet')
    char = Character((480, 480), test_sheet.get('right_smoke'))
    ground = Obstacle((40, 800), (800, 32))
    player = pygame.sprite.Group()
    obstacles = pygame.sprite.Group()
    player.add(char)
    obstacles.add(ground)

    playing = True
    while playing:
        clock.tick(60)
        screen.fill((0, 32, 32))

        obstacles.update()
        char.update()
        obstacles.draw(screen)
        player.draw(screen)

        pygame.display.flip()

        collision = pygame.sprite.spritecollide(char, obstacles, False, False)
        for o in collision:
            if o.rect.x < char.rect.x:
                char.vel_y = 0
                char.rect.y = o.rect.y - char.rect.height + 8

        rel = pygame.mouse.get_rel()
        if rel[0] > 0:
            char.vel_x = min(10, rel[0])
            char.a_images = animations.get('sprite/test_sheet').get('right_walk')
        elif rel[0] < 0:
            char.vel_x = max(-10, rel[0])
            char.a_images = animations.get('sprite/test_sheet').get('left_walk')
        if rel[1] > 0:
            char.vel_x = 0
            char.a_images = animations.get('sprite/test_sheet').get('right_smoke')
        elif rel[1] < 0 and char.vel_y == 0:
            char.vel_y += rel[1]
            char.a_images = animations.get('sprite/test_sheet').get('right_stand')

        click = pygame.mouse.get_pressed()
        if click[0]:
            char.vel_x = 0
        if click[2]:
            char.rect.x = 480
            char.rect.y = 480

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                playing = False

    pygame.quit()
