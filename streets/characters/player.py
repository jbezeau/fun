import streets.characters.characters as c
import streets.characters.actions as a

X = 0
Y = 1


class Player(c.Character):
    def __init__(self, position, sheet, animation):
        super(Player, self).__init__(position, sheet, animation)
        self.stats = {a.FIGHT: 4, a.PWR: 3, a.RES: 3}
        self.interactions = {'Smoke': self.smoke, 'Act Casual': self.casual, 'Fight': self.fight}

    def bump(self, char):
        # override default character behaviour when bumping into things
        print('Catch these hands!')
        # NPC subclasses will override this to change character behaviour
        if char.rect.x > self.rect.x:
            self.left_input((0, 0))
            self.set_animation('left_punch', a.punch, char)
        elif 0 > self.vel_x:
            self.right_input((0, 0))
            self.set_animation('right_punch', a.punch, char)
        char.vel_x = 0
        char.zero_input()

    def smoke(self, char):
        self.set_animation('right_smoke', a.idle, None)
        self.action = 'Smoke'

    def casual(self, char):
        # reset other choices of idle action
        self.action = 'Casual'

    def fight(self, char):
        # set active state to fight
        self.action = 'Fight'


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
