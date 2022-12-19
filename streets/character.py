import glob
import pickle
import pygame
from pygame import image
from sprite import sprites


CHARACTER_SIZE = (64, 128)
SCREEN_SIZE = (960, 960)
BLACK = (0, 0, 0)
GRAY = (96, 96, 96)

CONTACT_LOW = 'B'
CONTACT_HIGH = 'M'
CONTACT_HEAD = 'H'
CONTACT_WALL = 'W'
CONTACT_LEFT = '<'
CONTACT_RIGHT = '>'
CONTACT_CENTER = '-'

STAIR_HEIGHT = 16
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

    def collide(self, character, count):
        # check contact with obstacles in the environment
        contact = get_contact_pos(character.rect, self.rect)
        if contact.count(CONTACT_CENTER) > 0 and contact.count(CONTACT_LOW) > 0:
            new_y = self.rect.y - character.rect.height + STAIR_HEIGHT
            if count > 1:
                character.rect.y = min(new_y, character.rect.y)
            else:
                character.rect.y = new_y
            if character.vel_y > 0:
                character.vel_y = 0
            if character.check('jump'):
                if character.vel_x > 0:
                    character.set_animation('right_walk')
                else:
                    character.set_animation('left_walk')
            if character.check('fall'):
                if character.vel_x > 0:
                    character.set_animation('right_squat')
                else:
                    character.set_animation('left_squat')
                character.vel_x = 0
        if contact.count(CONTACT_HIGH) or contact.count(CONTACT_WALL):
            character.vel_x = 0
            if contact.count(CONTACT_RIGHT):
                char.rect.x = self.rect.x - character.rect.width
            elif contact.count(CONTACT_LEFT):
                char.rect.x = self.rect.x + self.rect.width
            if character.check('left'):
                character.set_animation('left_stand')
            else:
                character.set_animation('right_stand')


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
        if self.check('jump') and self.vel_y > STAIR_HEIGHT:
            if self.check('right'):
                self.set_animation('right_fall')
            else:
                self.set_animation('left_fall')
        self.a_frame = (self.a_frame + self.a_speed) % len(self._frames)
        frame_image = self._frames[int(self.a_frame)]
        self.image = pygame.transform.scale(frame_image, CHARACTER_SIZE)
        self.image.set_colorkey(sprites.COLOUR_KEY)


class Character(Model):
    def __init__(self, position, sheet, animation):
        super(Character, self).__init__(sheet, animation)
        self.rect.x, self.rect.y = position

    def zero_input(self, contact):
        if self.vel_x == 0 and contact.count(CONTACT_LOW) and contact.count(CONTACT_CENTER):
            if self.check('left_walk'):
                self.set_animation('left_stand')
            elif self.check('right_walk'):
                self.set_animation('right_stand')

    def left_input(self, adj_input, contact):
        if contact.count(CONTACT_LOW) and contact.count(CONTACT_CENTER):
            self.vel_x = _max_limit(adj_input[X], 0, 5)
            self.set_animation('left_walk')

    def right_input(self, adj_input, contact):
        if contact.count(CONTACT_LOW) and contact.count(CONTACT_CENTER):
            self.vel_x = _max_limit(adj_input[X], 0, 5)
            self.set_animation('right_walk')

    def up_input(self, adj_input, contact):
        if contact.count(CONTACT_LOW) and contact.count(CONTACT_CENTER):
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

    def down_input(self, adj_input, contact):
        # down / up
        if contact.count(CONTACT_LOW) and contact.count(CONTACT_CENTER):
            if self.check('right'):
                self.set_animation('right_squat')
            else:
                self.set_animation('left_squat')
            self.vel_x = 0


def get_input(mouse_input, character, contact):
    # handle all input, breaking it down into up/down/left right and handle states
    adj_x = _min_limit(mouse_input[X], -3, 0)
    adj_y = _min_limit(mouse_input[Y], -3, 0)

    if mouse_input[X] == 0 and mouse_input[Y] == 0:
        character.zero_input(contact)
    elif abs(adj_y) > abs(adj_x):
        if mouse_input[Y] > 0:
            character.down_input((adj_x, adj_y), contact)
        else:
            character.up_input((adj_x, adj_y), contact)
    else:
        if mouse_input[X] > 0:
            character.right_input((adj_x, adj_y), contact)
        else:
            character.left_input((adj_x, adj_y), contact)


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


def get_contact_pos(ch, ob):
    # depth param indicates how much sprite overlap we're looking for
    # return 4 values, all must be greater than 0 if there is a collision
    # value between 0 and character dimension represents degree to which object is imposing from
    # that side of the character's hit box

    top_contact = (ob.y + ob.height - ch.y)
    left_contact = (ob.x + ob.width - ch.x)
    right_contact = (ch.x + ch.width - ob.x)
    bottom_contact = (ch.y + ch.height - ob.y)

    contact = []
    if ch.height // 3 > bottom_contact:
        contact.append(CONTACT_LOW)
    elif 2 * ch.height // 3 > bottom_contact:
        contact.append(CONTACT_HIGH)
    elif ch.height // 3 > top_contact:
        contact.append(CONTACT_HEAD)
    else:
        contact.append(CONTACT_WALL)

    if ch.width // 3 > left_contact:
        contact.append(CONTACT_LEFT)
    elif ch.width // 3 > right_contact:
        contact.append(CONTACT_RIGHT)
    elif right_contact > ch.width // 3 and left_contact > ch.width // 3:
        contact.append(CONTACT_CENTER)
    return contact


def mouse_trail(colour):
    pointer.fill((0, 0, 0))
    pos = pygame.mouse.get_pos()
    rel = pygame.mouse.get_rel()
    pygame.draw.line(pointer, colour, pos, (pos[X] - rel[X], pos[Y] - rel[Y]))
    screen.blit(pointer, (0, 0))
    return rel


def interact_loop(active_objects):
    interacting = True
    while interacting:
        clock.tick(60)
        screen.fill((64, 0, 0))
        screen.blit(play, (0, 0))
        mouse_trail((0, 255, 0))
        pygame.display.flip()

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

    # put game elements on a separate surface I can reuse without updating sprites
    play = pygame.Surface(screen.get_size())
    play.set_colorkey((0, 0, 0))

    # separate surface for pointer trail active while paused
    pointer = pygame.Surface(screen.get_size())
    pointer.set_colorkey((0, 0, 0))

    char = Character((480, 480), 'sprite/test_sheet', 'right_smoke')
    ground = Obstacle((40, 800), (800, 32))
    block = Obstacle((440, 780), (80, 20))
    tall_block = Obstacle((800, 600), (80, 232))
    player = pygame.sprite.Group()
    obstacles = pygame.sprite.Group()
    player.add(char)
    obstacles.add(ground)
    obstacles.add(block)
    obstacles.add(tall_block)

    playing = True
    while playing:
        clock.tick(60)
        screen.fill((0, 32, 32))
        play.fill((0, 0, 0))

        obstacles.update()
        char.update()
        obstacles.draw(play)
        player.draw(play)
        screen.blit(play, (0, 0))
        mouse_rel = mouse_trail((255, 0, 0))
        pygame.display.flip()

        collision = pygame.sprite.spritecollide(char, obstacles, False, False)
        contacts = []
        for o in collision:
            o.collide(char, len(collision))
            # collect collision directions from all the stuff we're touching
            for c in get_contact_pos(char.rect, o.rect):
                contacts.append(c)
        get_input(mouse_rel, char, contacts)

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
