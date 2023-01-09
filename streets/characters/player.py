import pygame
import streets.characters.characters as c
import streets.characters.actions as a
import streets.environment.environment as e

X = 0
Y = 1

# action constants
FIGHT = 'Fight'
SMOKE = 'Smoke'
CASUAL = 'Act Casual'


class Player(c.Character):
    def __init__(self, position, sheet, animation, env):
        super(Player, self).__init__(position, sheet, animation, env)
        self.stats = {a.STUN: 0, a.WOUND: 0, a.FIGHT: 4, a.SHOOT: 4, a.PWR: 3, a.RES: 3}
        self.interactions = {SMOKE: self.smoke, CASUAL: None, FIGHT: None}

    def update(self):
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


def _min_limit(val, shift, min_value):
    # min function that works for positive or negative values
    # used for softening mouse input values
    if val == 0:
        return 0
    return max(abs(val) + shift, min_value) * val//abs(val)
