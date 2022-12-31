import pygame

SEARCH = 'Search'
MOVE = 'Move'
LEAVE = 'Leave Alone'


class Corpse(pygame.sprite.Sprite):
    def __init__(self, char):
        super(Corpse, self).__init__()
        self.image = char.image
        self.rect = char.rect
        self.interactions = {SEARCH: self.search, MOVE: self.move, LEAVE: self.leave}
        self.follow = None

    def update(self):
        # in case we die midair or get thrown
        self.rect.y += 1
        if self.follow:
            self.rect.x = self.follow.x
            self.rect.y = self.follow.y
            self.follow.y += 1

    def search(self, char):
        print('You get nothing')

    def leave(self, char):
        self.follow = None

    def move(self, char):
        self.follow = char
