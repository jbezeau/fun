import glob
import pickle
import pygame
from pygame import image
from streets.sprite import sprites
from streets.characters import actions
import streets.environment.objects as obj


ANIMATION_SPEED = 0.1
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
    def __init__(self, position):
        super(Actor, self).__init__()
        self.image = pygame.Surface(CHARACTER_SIZE)
        self.image.fill(sprites.COLOUR_KEY)
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = position
        self.vel_x = 0
        self.vel_y = 0

    def update(self):
        self.rect.x += self.vel_x
        self.rect.y += self.vel_y
        self.vel_y += 1


class Model(Actor):
    def __init__(self, position, sheet_name, default_a, environment):
        super(Model, self).__init__(position)
        self._frame = 0
        self._speed = ANIMATION_SPEED
        self._sheet_name = None
        self._sheet = None
        self._tag = None
        self._frames = None
        self._locked = False
        self.set_sheet(sheet_name)
        self.set_animation(default_a)
        self.contact = []
        self.env = environment

    def set_sheet(self, sheet_name):
        if sheet_name:
            sheet = animations.get(sheet_name)
            if sheet:
                self._sheet_name = sheet_name
                self._sheet = animations.get(self._sheet_name)
                return True
        return False

    def set_animation(self, animation_name, lock=False):
        if self._locked:
            return False
        elif animation_name and self._tag == animation_name:
            return True
        else:
            frames = self._sheet.get(animation_name)
            if frames:
                self._tag = animation_name
                self._frames = frames
                self._frame = 0
                self._locked = lock
                return True
        return False

    def check(self, tag):
        if self._tag:
            return tag in self._tag
        return False

    def update(self):
        super(Model, self).update()

        collisions = pygame.sprite.spritecollide(self, self.env.obstacles, False)
        self.contact.clear()
        for o in collisions:
            touching = o.collide(self, len(collisions))
            for t in touching:
                self.contact.append(t)

        # apex of jump
        if self.check('jump') and self.vel_y > STAIR_HEIGHT + 1:
            if self.check('right'):
                self.set_animation('right_fall')
            else:
                self.set_animation('left_fall')

        # landing on the ground
        if self.contact.count(CONTACT_CENTER) > 0 and self.contact.count(CONTACT_LOW) > 0:
            if self.check('jump'):
                if self.vel_x > 0:
                    self.set_animation('right_walk')
                else:
                    self.set_animation('left_walk')
            if self.check('fall'):
                if self.vel_x > 0:
                    self.set_animation('right_squat')
                else:
                    self.set_animation('left_squat')
                self.vel_x = 0

        # run into wall
        if self.contact.count(CONTACT_HIGH) or self.contact.count(CONTACT_WALL):
            if self.check('left'):
                self.set_animation('left_stand')
            else:
                self.set_animation('right_stand')

        # character animation
        if self._frames:
            self._frame = (self._frame + self._speed) % len(self._frames)
            frame_image = self._frames[int(self._frame)]
            self.image = pygame.transform.scale(frame_image, CHARACTER_SIZE)
            self.image.set_colorkey(sprites.COLOUR_KEY)
            if self.is_animation_over():
                self._locked = False

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
        if self.is_on_ground() and self.set_animation('left_walk'):
            self.vel_x = _max_limit(adj_input[X], 0, 5)

    def right_input(self, adj_input):
        if self.is_on_ground() and self.set_animation('right_walk'):
            self.vel_x = _max_limit(adj_input[X], 0, 5)

    def up_input(self, adj_input):
        if self.is_on_ground():
            # check squat first
            jump = False
            if self.check('squat'):
                self.vel_y = _max_limit(adj_input[Y], 0, 2*STAIR_HEIGHT)
                if self.check('right'):
                    jump = self.set_animation('right_jump')
                else:
                    jump = self.set_animation('left_jump')
            elif self.check('walk'):
                self.vel_y = _max_limit(adj_input[Y], 0, STAIR_HEIGHT)
                if self.check('right'):
                    jump = self.set_animation('right_jump')
                else:
                    jump = self.set_animation('left_jump')
            if jump:
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

    def is_frame_num(self, num):
        return self._frame + self._speed > num >= self._frame

    def is_animation_over(self):
        if self._frames:
            return self._frame + self._speed >= len(self._frames)
        return True

    def navigate(self):
        # NPC subclasses will override this to change how they deal with terrain
        # scene is set of interactive objects
        # char is player character
        # obstacles is set of terrain to navigate
        # this is incredibly over-engineered for default behaviour of walking until you hit something
        if self.contact.count(CONTACT_RIGHT):
            self.left_input((-3, 0))
        elif self.contact.count(CONTACT_LEFT):
            self.right_input((3, 0))


class Character(Model):
    def __init__(self, position, sheet, animation, environment):
        super(Character, self).__init__(position, sheet, animation, environment)
        self.stats = {actions.STUN: 0, actions.WOUND: 0, actions.FIGHT: 4, actions.PWR: 3, actions.RES: 3}
        self.interactions = {}
        self.selected_interaction = None
        self._action_function = None
        self._target = None
        self._item_group = None

    def update(self):
        super(Character, self).update()
        injury = max(self.stats.get(actions.STUN), self.stats.get(actions.WOUND))
        if injury > 9 and not self.check('die'):
            if self.check('left'):
                self.set_animation('left_die', actions.die, None, True)
            else:
                self.set_animation('right_die', actions.die, None, True)
        if self._action_function:
            # action function is a one-time thing, like throwing a punch
            self._action_function(self, self._target)
        elif self.interactions.get(self.selected_interaction):
            # status functions are overall behaviour profiles
            # it coordinates moving, attacking, etc
            self.interactions[self.selected_interaction](self._target)

    def set_animation(self, animation_name, function=None, target=None, lock=False):
        if super(Character, self).set_animation(animation_name, lock):
            # we want action function to be None for actions that don't need a callback
            self._action_function = function
            self._target = target
            return True
        return False

    def interact(self, action_name, char):
        self.selected_interaction = action_name
        self._target = char

    def check(self, tag):
        # override status check to look at state name as well
        if super(Character, self).check(tag):
            return True
        if self.selected_interaction:
            return tag in self.selected_interaction


class Punk(Character):
    def __init__(self, position, sheet, animation, env):
        super(Punk, self).__init__(position, sheet, animation, env)
        self.interactions = {'Provoke': self.provoke}
        self.stats = {actions.STUN: 0, actions.WOUND: 0, actions.FIGHT: 5, actions.PWR: 5, actions.RES: 5}

    def provoke(self, char):
        if char:
            print('You know what? Fuck you!')
            if char.rect.x < self.rect.x:
                self.left_input((-10, 0))
            elif char.rect.x > self.rect.x:
                self.right_input((10, 0))

    def bump(self, char):
        if char.rect.x > self.rect.x:
            self.left_input((0, 0))
            self.set_animation('right_punch', actions.punch, char, True)
        else:
            self.right_input((0, 0))
            self.set_animation('left_punch', actions.punch, char, True)
        char.vel_x = 0
        char.zero_input()


def _max_limit(val, shift, max_value):
    # max function that works for positive or negative values
    # used for capping character movement speeds
    if val == 0:
        return 0
    return min(abs(val) + shift, max_value) * val//abs(val)


animations = load_animations()
print(animations)
