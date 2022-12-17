import glob
import pickle
import pygame
from pygame import image
from sprite import sprites


CHARACTER_SIZE = (64, 128)
SCREEN_SIZE = (960, 960)
BLACK = (0, 0, 0)
GRAY = (96, 96, 96)

STAIR_HEIGHT = 8
X = 0
Y = 1


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
    def __init__(self, sheet_name, default_a):
        super(Model, self).__init__()
        self.a_frame = 0
        self.a_speed = 0.1
        self._sheet_name = None
        self._sheet = None
        self._tag = None
        self._frames = None
        self.set_sheet(sheet_name)
        self.set_animation(default_a)

    def set_sheet(self, sheet_name):
        if sheet_name:
            sheet = animations.get(sheet_name)
            if sheet:
                self._sheet_name = sheet_name
                self._sheet = animations.get(self._sheet_name)
                return True
        return False

    def set_animation(self, animation_name):
        if animation_name:
            frames = self._sheet.get(animation_name)
            if frames:
                self._tag = animation_name
                self._frames = frames
                return True
        return False

    def check(self, tag):
        return tag in self._tag

    def update(self):
        super(Model, self).update()
        # add to mysterious state transition function
        if self.check('jump') and self.vel_y > 11:
            if self.check('right'):
                self.set_animation('right_fall')
            else:
                self.set_animation('left_fall')
        self.a_frame = (self.a_frame + self.a_speed) % len(self._frames)
        frame_image = self._frames[int(self.a_frame)]
        self.image = pygame.transform.scale(frame_image, CHARACTER_SIZE)
        self.image.set_colorkey(sprites.COLOUR_KEY)


def get_input(mouse_input, character, contact):
    adj_x = _min_limit(mouse_input[X], -3, 0)
    adj_y = _min_limit(mouse_input[Y], -3, 0)

    if mouse_input[X] == 0 and mouse_input[Y] == 0:
        zero_input(character, contact)
    elif abs(adj_y) > abs(adj_x):
        if mouse_input[Y] > 0:
            down_input((adj_x, adj_y), character, contact)
        else:
            up_input((adj_x, adj_y), character, contact)
    else:
        if mouse_input[X] > 0:
            right_input((adj_x, adj_y), character, contact)
        else:
            left_input((adj_x, adj_y), character, contact)


def _min_limit(val, shift, min_value):
    # min function that works for positive or negative values
    # used for softening mouse input values
    if val == 0:
        return 0
    return max(abs(val) + shift, min_value) * val//abs(val)


def _max_limit(val, shift, max_value):
    # max function that works for positive or negative values
    # used for capping character movement speeds
    if val == 0:
        return 0
    return min(abs(val) + shift, max_value) * val//abs(val)


def zero_input(character, contact):
    if character.vel_x == 0 and contact:
        if character.check('left_walk'):
            char.set_animation('left_stand')
        elif character.check('right_walk'):
            char.set_animation('right_stand')


def left_input(adj_input, character, contact):
    if contact:
        character.vel_x = _max_limit(adj_input[X], 0, 5)
        character.set_animation('left_walk')


def right_input(adj_input, character, contact):
    if contact:
        character.vel_x = _max_limit(adj_input[X], 0, 5)
        character.set_animation('right_walk')


def up_input(adj_input, character, contact):
    # check squat first
    if adj_input[Y] < 0 and contact:
        if character.check('squat'):
            character.vel_y = _max_limit(adj_input[Y], 0, 20)
            if character.check('right'):
                character.set_animation('right_jump')
            else:
                character.set_animation('left_jump')
        elif char.check('walk'):
            char.vel_y = _max_limit(adj_input[Y], 0, 10)
            if char.check('right'):
                char.set_animation('right_jump')
            else:
                char.set_animation('left_jump')
        character.vel_x = _max_limit(adj_input[X], 0, 5)


def down_input(adj_input, character, contact):
    # down / up
    if contact:
        if character.check('right'):
            character.set_animation('right_squat')
        else:
            character.set_animation('left_squat')
        character.vel_x = 0


class Character(Model):
    def __init__(self, position, sheet, animation):
        super(Character, self).__init__(sheet, animation)
        self.rect.x, self.rect.y = position


def interact_loop(active_objects):
    interacting = True
    while interacting:
        for interact_event in pygame.event.get():
            if interact_event.type == pygame.QUIT:
                # return to quit
                return False
            if interact_event.type == pygame.MOUSEBUTTONUP:
                # select object and bring up interact UI
                mouse_rect = pygame.Rect(pygame.mouse.get_pos(), (1, 1))
                interact_with = mouse_rect.collidedict(active_objects)
            if interact_event.type == pygame.MOUSEBUTTONDOWN:
                # select interact event and return to action loop
                interacting = False
    # return to play
    return True


if __name__ == '__main__':
    animations = load_animations()
    print(animations)

    pygame.init()
    pygame.font.init()
    clock = pygame.time.Clock()
    pygame.display.set_mode(SCREEN_SIZE)
    pygame.display.set_caption('Character Test')
    pygame.mouse.set_visible(False)
    screen = pygame.display.set_mode(SCREEN_SIZE)

    char = Character((480, 480), 'sprite/test_sheet', 'right_smoke')
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

        pos = pygame.mouse.get_pos()
        rel = pygame.mouse.get_rel()
        pygame.draw.line(screen, (255, 0, 0), pos, (pos[X]-rel[X], pos[Y]-rel[Y]))

        pygame.display.flip()

        collision = pygame.sprite.spritecollide(char, obstacles, False, False)
        for o in collision:
            if char.rect.y + char.rect.height > o.rect.y - 2 * STAIR_HEIGHT:
                char.rect.y = o.rect.y - char.rect.height + STAIR_HEIGHT
                if char.vel_y > 0:
                    char.vel_y = 0
                if char.check('jump'):
                    if char.vel_x > 0:
                        char.set_animation('right_walk')
                    else:
                        char.set_animation('left_walk')
                if char.check('fall'):
                    if char.vel_x > 0:
                        char.set_animation('right_squat')
                    else:
                        char.set_animation('left_squat')
                    char.vel_x = 0

        get_input(rel, char, collision)

        click = pygame.mouse.get_pressed()
        if click[2]:
            char.rect.x = 480
            char.rect.y = 480
            char.vel_x = 0
            char.vel_y = 0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                playing = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                playing = interact_loop({})

    pygame.quit()
