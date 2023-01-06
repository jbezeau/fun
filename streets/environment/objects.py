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

    def update(self):
        # use inherited "falling object" behaviour
        super(Corpse, self).update()

        # get dragged around
        if self.follow:
            self.rect.x = self.follow.x
            self.rect.y = self.follow.y

    def leave(self, char):
        self.follow = None
        self.interactions[MOVE] = self.move

    def take(self, char):
        self.follow = char
        self.interactions[LEAVE] = self.leave
