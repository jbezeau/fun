import pygame


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

        collision = pygame.sprite.groupcollide(self.non_player, self.obstacles, False, False)
        # check for all contact between NPCs and obstacles
        for n in collision:
            obstacle_list = collision.get(n)
            if obstacle_list:
                # for every object this NPC is touching
                for o in obstacle_list:
                    # build one comprehensive list of spots where they're touching stuff
                    for c in o.collide(n, len(obstacle_list)):
                        n.contact.append(c)
            # NPCs only try navigating when they're touching the environment
            n.navigate()

        collision = pygame.sprite.groupcollide(self.player, self.obstacles, False, False)
        for p in collision:
            for o in collision[p]:
                for c in o.collide(p, len(collision)):
                    p.contact.append(c)

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
