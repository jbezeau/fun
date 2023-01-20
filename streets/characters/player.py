import pygame
import streets.characters.characters as c
import streets.characters.actions as a
import streets.environment.environment as e

# coordinate indexes
X = 0
Y = 1

# AR parameters
AR_FONT_SIZE = 16
AR_RED = (255, 32, 0)
AR_BLUE = (32, 0, 255)

# action constants
FIGHT = 'Fight'
SMOKE = 'Smoke'
CASUAL = 'Act Casual'


class Player(c.Character):
    def __init__(self, position, sheet, animation, env):
        super(Player, self).__init__(position, sheet, animation, env)
        self.stats = {a.STUN: 0, a.WOUND: 0, a.FIGHT: 4, a.SHOOT: 4, a.PWR: 3, a.RES: 3}
        self.interactions = {SMOKE: self.smoke, CASUAL: None, FIGHT: None}

        # surface for augmented reality effects
        # can be turned on/off, suffer interference, etc.
        self._ar_surface = None
        self.ar = [a.HIGHLIGHT, a.WOUND, a.STUN]

    def set_ar_surface(self, screen):
        # pass the screen in to character so we can define AR display area
        self._ar_surface = pygame.Surface(screen.get_size())
        self._ar_surface.set_colorkey(e.BLANK)

    def update(self):
        self._ar_surface.fill(e.BLANK)
        self.get_input()
        self.get_target()
        if self.check(FIGHT) and self._target is not None:
            self.shoot()
        super(Player, self).update()

    def smoke(self, char):
        self.vel_x = 0
        self.set_animation('right_smoke', a.idle, None, True)

    def shoot(self):
        # shoot when we can see the target
        # simplified check: are we facing the right way
        if self._target.rect.x > self.rect.x and self.check('right'):
            self.vel_x = 0
            self.set_animation('right_shoot', a.pistol, self._target, True)
        elif self._target.rect.x < self.rect.x and self.check('left'):
            self.vel_x = 0
            self.set_animation('left_shoot', a.pistol, self._target, True)

    def bump(self, char):
        if self.check(FIGHT):
            # interaction states set the tone for what your character does when they bump people
            if char.rect.x > self.rect.x:
                self.set_animation('right_punch', a.punch, char)
            else:
                self.set_animation('left_punch', a.punch, char)
        self.vel_x = 0
        char.vel_x = 0
        char.zero_input()

    # control a character using mouse
    def get_input(self):
        mouse_input = pygame.mouse.get_rel()
        # handle all input, breaking it down into up/down/left right and handle states
        adj_x = _min_limit(mouse_input[X], -3, 0)
        adj_y = _min_limit(mouse_input[Y], -3, 0)

        if mouse_input[X] == 0 and mouse_input[Y] == 0:
            self.zero_input()
        elif abs(adj_y) > abs(adj_x):
            if mouse_input[Y] > 0:
                self.down_input((adj_x, adj_y))
            else:
                self.up_input((adj_x, adj_y))
        else:
            if mouse_input[X] > 0:
                self.right_input((adj_x, adj_y))
            else:
                self.left_input((adj_x, adj_y))

    def get_target(self):
        tgt = self.env.get_mouse_over([e.NPC])
        self._target = tgt
        if tgt and self._ar_surface:
            small_font = pygame.font.Font(None, AR_FONT_SIZE)
            if a.HIGHLIGHT in self.ar:
                pygame.draw.rect(self._ar_surface, AR_RED, tgt.rect, 1)
            if a.WOUND in self.ar:
                wound_num = small_font.render(str(tgt.stats.get(a.WOUND)), False, AR_RED)
                self._ar_surface.blit(wound_num, (tgt.rect.x + 2, tgt.rect.y + 2))
            if a.STUN in self.ar:
                stun_num = small_font.render(str(tgt.stats.get(a.STUN)), False, AR_BLUE)
                self._ar_surface.blit(stun_num, (tgt.rect.x + 2, tgt.rect.y + 4 + AR_FONT_SIZE))

    def draw_ar(self, screen):
        if self.ar:
            screen.blit(self._ar_surface, (0, 0))


def _min_limit(val, shift, min_value):
    # min function that works for positive or negative values
    # used for softening mouse input values
    if val == 0:
        return 0
    return max(abs(val) + shift, min_value) * val//abs(val)
