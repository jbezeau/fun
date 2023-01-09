import pygame

SEARCH = 'Search'
TAKE = 'Take'
MOVE = 'Move'
LEAVE = 'Leave'


class Object(pygame.sprite.Sprite):
    def __init__(self):
        super(Object, self).__init__()
        self.vel_y = 1
        self.vel_x = 0
        self.interactions = {SEARCH: self.search}

    def update(self):
        # in case we die midair or get thrown
        self.rect.y += self.vel_y
        self.vel_y += 1

    def search(self, char):
        print('Nothing')
        self.interactions.pop(SEARCH)


class Corpse(Object):
    def __init__(self, char):
        super(Corpse, self).__init__()
        self.image = char.image
        self.rect = char.rect
        self.follow = None
        self.interactions[MOVE] = self.take
        self.selected_interaction = None

    def update(self):
        # use inherited "falling object" behaviour
        super(Corpse, self).update()

        # get dragged around
        if self.follow:
            self.rect.x += (self.follow.rect.x - self.rect.x) // 2
            self.rect.y += (self.follow.rect.y - self.rect.height // 2 - self.rect.y) // 2

    def interact(self, action_name, char):
        # different definition for objects than characters!
        interaction_func = self.interactions.get(action_name)
        if interaction_func:
            interaction_func(char)

    def leave(self, char):
        self.follow = None
        self.interactions.pop(LEAVE)
        self.interactions[MOVE] = self.take

    def take(self, char):
        self.follow = char
        self.interactions.pop(MOVE)
        self.interactions[LEAVE] = self.leave
