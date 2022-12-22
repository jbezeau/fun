import glob
import pickle
import pygame
from pygame import image
from streets.sprite import sprites
from streets.characters import actions


CHARACTER_SIZE = (64, 128)
STAIR_HEIGHT = 16
X = 0
Y = 1

CONTACT_LOW = 'B'
CONTACT_HIGH = 'M'
CONTACT_HEAD = 'H'
CONTACT_WALL = 'W'
CONTACT_LEFT = '<'
CONTACT_RIGHT = '>'
CONTACT_CENTER = '-'


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


class Actor(pygame.sprite.Sprite):
    def __init__(self):
        super(Actor, self).__init__()
        self.image = pygame.Surface(CHARACTER_SIZE)
        self.image.fill(sprites.COLOUR_KEY)
        self.rect = self.image.get_rect()
        self.vel_x = 0
        self.vel_y = 0
        self.contact = []

    def update(self):
        self.rect.x += self.vel_x
        self.rect.y += self.vel_y
        self.vel_y += 1
        self.contact.clear()


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
        if self.check('jump') and self.vel_y > STAIR_HEIGHT + 1:
            if self.check('right'):
                self.set_animation('right_fall')
            else:
                self.set_animation('left_fall')
        self.a_frame = (self.a_frame + self.a_speed) % len(self._frames)
        frame_image = self._frames[int(self.a_frame)]
        self.image = pygame.transform.scale(frame_image, CHARACTER_SIZE)
        self.image.set_colorkey(sprites.COLOUR_KEY)

    def bump(self, char):
        # NPC subclasses will override this to change character behaviour
        if self.vel_x > 0:
            self.left_input((-5, 0))
        elif 0 > self.vel_x:
            self.right_input((5, 0))
        char.vel_x = 0
        char.zero_input()

    # use control inputs when manipulating characters, they combine movement and animation
    def zero_input(self):
        if self.vel_x == 0 and self.is_on_ground():
            if self.check('left_walk'):
                self.set_animation('left_stand')
            elif self.check('right_walk'):
                self.set_animation('right_stand')

    def left_input(self, adj_input):
        if self.is_on_ground():
            self.vel_x = _max_limit(adj_input[X], 0, 5)
            self.set_animation('left_walk')

    def right_input(self, adj_input):
        if self.is_on_ground():
            self.vel_x = _max_limit(adj_input[X], 0, 5)
            self.set_animation('right_walk')

    def up_input(self, adj_input):
        if self.is_on_ground():
            # check squat first
            if self.check('squat'):
                self.vel_y = _max_limit(adj_input[Y], 0, 2*STAIR_HEIGHT)
                if self.check('right'):
                    self.set_animation('right_jump')
                else:
                    self.set_animation('left_jump')
            elif self.check('walk'):
                self.vel_y = _max_limit(adj_input[Y], 0, STAIR_HEIGHT)
                if self.check('right'):
                    self.set_animation('right_jump')
                else:
                    self.set_animation('left_jump')
            self.vel_x = _max_limit(adj_input[X], 0, 5)

    def down_input(self, adj_input):
        # down / up
        if self.is_on_ground():
            if self.check('right'):
                self.set_animation('right_squat')
            else:
                self.set_animation('left_squat')
            self.vel_x = 0

    def is_on_ground(self):
        return self.contact.count(CONTACT_LOW) and self.contact.count(CONTACT_CENTER)

    def navigate(self, scene, char, obstacles):
        # NPC subclasses will override this to change how they deal with terrain
        # scene is set of interactive objects
        # char is player character
        # obstacles is set of terrain to navigate
        # this is incredibly over-engineered for default behaviour of walking until you hit something
        if self.contact.count(CONTACT_RIGHT):
            self.left_input((-5, 0))
        elif self.contact.count(CONTACT_LEFT):
            self.right_input((5, 0))
        elif self.check('smoke'):
            self.left_input((5, 4))


class Character(Model):
    def __init__(self, position, sheet, animation):
        super(Character, self).__init__(sheet, animation)
        self.rect.x, self.rect.y = position
        self.stats = {actions.FIGHT: 4, actions.PWR: 3, actions.RES: 3}
        self.interactions = {}
        self._action_function = None
        self._action_target = None

    def update(self):
        super(Character, self).update()
        if self._action_function:
            self._action_function(self, self._action_target)

    def set_animation(self, animation_name, function=None, target=None):
        super(Character, self).set_animation(animation_name)
        # we want action function to be None for actions that don't need a callback
        self._action_function = function
        self._action_target = target

    def interact(self, action, char):
        action = self.interactions.get(action)
        if action:
            action(char)


class Punk(Character):
    def __init__(self, position, sheet, animation):
        super(Punk, self).__init__(position, sheet, animation)
        self.interactions = {'Provoke': self.provoke}
        self.stats = {actions.FIGHT: 5, actions.PWR: 5, actions.RES: 5}

    def provoke(self, char):
        print('You know what? Fuck you!')
        if char.rect.x < self.rect.x:
            self.left_input((-10, 0))
        elif char.rect.x > self.rect.x:
            self.right_input((10, 0))

    def bump(self, char):
        if self.check('walk'):
            print('Hey, asshole!')
            # NPC subclasses will override this to change character behaviour
            if char.rect.x > self.rect.x:
                self.left_input((0, 0))
                self.set_animation('left_stand', actions.punch, char)
            elif 0 > self.vel_x:
                self.right_input((0, 0))
                self.set_animation('right_stand', actions.punch, char)
        char.vel_x = 0
        char.zero_input()


# control a character using mouse
def get_input(mouse_input, character):
    # handle all input, breaking it down into up/down/left right and handle states
    adj_x = _min_limit(mouse_input[X], -3, 0)
    adj_y = _min_limit(mouse_input[Y], -3, 0)

    if mouse_input[X] == 0 and mouse_input[Y] == 0:
        character.zero_input()
    elif abs(adj_y) > abs(adj_x):
        if mouse_input[Y] > 0:
            character.down_input((adj_x, adj_y))
        else:
            character.up_input((adj_x, adj_y))
    else:
        if mouse_input[X] > 0:
            character.right_input((adj_x, adj_y))
        else:
            character.left_input((adj_x, adj_y))


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


animations = load_animations()
print(animations)
