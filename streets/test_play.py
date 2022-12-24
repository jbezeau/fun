import pygame
import random
import environment.obstacles as ob
import characters.characters as ch
import characters.player as pl


SCREEN_SIZE = (960, 960)

X = 0
Y = 1


def mouse_trail(colour):
    pointer.fill((0, 0, 0))
    pos = pygame.mouse.get_pos()
    rel = pygame.mouse.get_rel()
    pygame.draw.line(pointer, colour, pos, (pos[X] - rel[X], pos[Y] - rel[Y]))
    screen.blit(pointer, (0, 0))
    return rel


def interact_loop():
    interactions.empty()
    interaction_object = None

    interacting = True
    while interacting:
        clock.tick(60)
        screen.fill((64, 0, 0))
        screen.blit(play, (0, 0))
        mouse_trail((0, 255, 0))

        interactions.update()
        interactions.draw(screen)

        pygame.display.flip()

        mouse_rect = pygame.Rect(pygame.mouse.get_pos(), (1, 1))
        interact_collide = mouse_rect.collidedict(interactive.spritedict)
        if interact_collide:
            for ic in interact_collide:
                if ic and ic != interaction_object:
                    interactions.empty()
                    interaction_object = ic
                    ic_interacts = list(ic.interactions.keys())
                    for ic_key in ic_interacts:
                        if ic.selected_interaction == ic_key:
                            text_colour = (255, 255, 128)
                        else:
                            text_colour = (255, 255, 255)
                        interactions.add(InteractionItem(ic.rect, ic_key, text_colour))

        for interact_event in pygame.event.get():
            if interact_event.type == pygame.QUIT:
                # return to quit
                return False
            if interact_event.type == pygame.MOUSEBUTTONDOWN:
                # select interact event and return to action loop
                interaction_select = mouse_rect.collidedict(interactions.spritedict)
                if interaction_select:
                    interaction_sprite = interaction_select[0]
                    interaction_object.interact(interaction_sprite.name, char)
                interacting = False
    # return to play
    return True


class InteractionItem(pygame.sprite.Sprite):
    def __init__(self, parent_sprite, name, text_colour=(255, 255, 255)):
        super(InteractionItem, self).__init__()
        self.image = interaction_font.render(name, False, text_colour)
        self.rect = self.image.get_rect()
        self.rect.x += parent_sprite.x + random.randrange(9) - 4
        self.rect.y += parent_sprite.y + random.randrange(9) - 4
        self.name = name

    def update(self):
        cloud = pygame.sprite.spritecollide(self, interactions, False)
        for interaction in cloud:
            if self.rect != interaction.rect:
                self.rect.x += self.rect.x - interaction.rect.x
                self.rect.y += self.rect.y - interaction.rect.y


if __name__ == '__main__':
    pygame.init()
    pygame.font.init()
    interaction_font = pygame.font.Font(None, 32)

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

    char = pl.Player((480, 480), 'sprite/neon_hawk', 'right_smoke')
    shade = ch.Punk((600, 480), 'sprite/test_sheet', 'right_smoke')
    ground = ob.Obstacle((40, 800), (800, 32))
    block = ob.Obstacle((440, 780), (80, 20))
    tall_block = ob.Obstacle((800, 600), (80, 232))

    player = pygame.sprite.Group()
    non_player = pygame.sprite.Group()
    obstacles = pygame.sprite.Group()
    interactive = pygame.sprite.Group()
    interactions = pygame.sprite.Group()

    player.add(char)
    non_player.add(shade)
    interactive.add(char)
    interactive.add(shade)
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
        non_player.update()
        obstacles.draw(play)
        player.draw(play)
        non_player.draw(play)
        screen.blit(play, (0, 0))
        mouse_rel = mouse_trail((255, 0, 0))
        pygame.display.flip()

        collision = pygame.sprite.groupcollide(non_player, obstacles, False, False)
        # check for all contact between NPCs and obstacles
        for npc in collision:
            obstacle_list = collision.get(npc)
            if obstacle_list:
                # for every object this NPC is touching
                for o in obstacle_list:
                    # build one comprehensive list of spots where they're touching stuff
                    for c in o.collide(npc, len(obstacle_list)):
                        npc.contact.append(c)
            # NPCs only try navigating when they're touching the environment
            npc.navigate(None, char, obstacles)

        collision = pygame.sprite.spritecollide(char, obstacles, False, False)
        for o in collision:
            for c in o.collide(char, len(collision)):
                char.contact.append(c)

        collision = pygame.sprite.groupcollide(non_player, non_player, False, False, pygame.sprite.collide_mask)
        for npc in collision:
            for npc2 in collision[npc]:
                if npc != npc2:
                    npc.bump(npc2)

        collision = pygame.sprite.spritecollide(char, non_player, False, pygame.sprite.collide_mask)
        for npc in collision:
            npc.bump(char)

        pl.get_input(mouse_rel, char)

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
                playing = interact_loop()

    pygame.quit()
