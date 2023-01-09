import pygame

ITEMS = 'Items'
INTERACTIVE = 'Interactive'
PLAYER = 'Player'
NPC = 'Non-Player'


class Environment:
    def __init__(self, screen):
        # pack all of our junk into one object instance
        self.items = pygame.sprite.Group()
        self.obstacles = pygame.sprite.Group()
        self.interactive = pygame.sprite.Group()
        self.player = pygame.sprite.GroupSingle()
        self.non_player = pygame.sprite.Group()
        self._surface = pygame.Surface(screen.get_size())
        self._surface.set_colorkey((0, 0, 0))

    def update(self):
        # update, collide, and draw everything
        self.obstacles.update()
        self.interactive.update()
        self.items.update()
        self.player.update()
        self.non_player.update()

        item_collision = pygame.sprite.groupcollide(self.items, self.obstacles, False, False)
        for i in item_collision:
            obstacle_list = item_collision.get(i)
            if obstacle_list:
                for o in obstacle_list:
                    o.collide(i, len(obstacle_list))

        collision = pygame.sprite.groupcollide(self.non_player, self.non_player, False, False, pygame.sprite.collide_mask)
        for n in collision:
            for n2 in collision[n]:
                if n != n2:
                    n.bump(n2)

        collision = pygame.sprite.groupcollide(self.player, self.non_player, False, False, pygame.sprite.collide_mask)
        for p in collision:
            for n in collision[p]:
                n.bump(p)
                p.bump(n)

    def draw(self, screen):
        self._surface.fill((0, 0, 0))
        self.obstacles.draw(self._surface)
        self.interactive.draw(self._surface)
        self.items.draw(self._surface)
        self.player.draw(self._surface)
        self.non_player.draw(self._surface)

        screen.blit(self._surface, (0, 0))

    def get_mouse_over(self, groups):
        mouse_point = pygame.mouse.get_pos()
        mouse_rect = pygame.Rect(mouse_point, (1, 1))
        mouse_over = None

        if PLAYER in groups:
            mouse_over = mouse_rect.collidedict(self.player.spritedict)
        if NPC in groups and mouse_over is None:
            mouse_over = mouse_rect.collidedict(self.non_player.spritedict)
        if INTERACTIVE in groups and mouse_over is None:
            mouse_over = mouse_rect.collidedict(self.interactive.spritedict)
        if ITEMS in groups and mouse_over is None:
            mouse_over = mouse_rect.collidedict(self.items.spritedict)

        if mouse_over:
            for o in mouse_over:
                return o
