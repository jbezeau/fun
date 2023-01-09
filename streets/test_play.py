import pygame
import random
import environment.obstacles as ob
import environment.environment as en
import characters.characters as ch
import characters.player as pl


SCREEN_SIZE = (960, 960)

# coordinate indexes
X = 0
Y = 1

# mouse buttons
L = 0
M = 1
R = 2


def mouse_trail(last_mouse, colour):
    pointer.fill((0, 0, 0))
    pos = pygame.mouse.get_pos()
    pygame.draw.line(pointer, colour, pos, last_mouse)
    screen.blit(pointer, (0, 0))
    return pos


def interact_loop(environment):
    interactions = pygame.sprite.Group()
    interactions.empty()
    interaction_object = None
    i_pos = last_pos

    interacting = True
    while interacting:
        clock.tick(60)
        screen.fill((64, 0, 0))
        environment.draw(screen)
        i_pos = mouse_trail(i_pos, (0, 255, 0))

        interactions.update()
        interactions.draw(screen)

        pygame.display.flip()

        mouse_rect = pygame.Rect(pygame.mouse.get_pos(), (1, 1))
        ic = environment.get_mouse_over([en.INTERACTIVE])
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
                    interaction_object.interact(interaction_sprite.name, environment.player.sprite)
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
        interactions = self.groups()
        for g in interactions:
            cloud = pygame.sprite.spritecollide(self, g, False)
            for i in cloud:
                if self.rect != i.rect:
                    self.rect.x += self.rect.x - i.rect.x
                    self.rect.y += self.rect.y - i.rect.y


if __name__ == '__main__':
    pygame.init()
    pygame.font.init()
    interaction_font = pygame.font.Font(None, 32)
    last_pos = pygame.mouse.get_pos()

    clock = pygame.time.Clock()
    pygame.display.set_mode(SCREEN_SIZE)
    pygame.display.set_caption('Character Test')
    pygame.mouse.set_visible(False)
    screen = pygame.display.set_mode(SCREEN_SIZE)

    # separate surface for pointer trail active while paused
    pointer = pygame.Surface(screen.get_size())
    pointer.set_colorkey((0, 0, 0))

    env = en.Environment(screen)
    char = pl.Player((480, 480), 'sprite/neon_hawk', 'right_smoke', env)
    shade = ch.Punk((600, 480), 'sprite/test_sheet', 'right_smoke', env)
    ground = ob.Obstacle((40, 800), (800, 32))
    block = ob.Obstacle((440, 780), (80, 20))
    tall_block = ob.Obstacle((800, 600), (80, 232))

    env.player.add(char)
    env.non_player.add(shade)
    env.interactive.add(char)
    env.interactive.add(shade)
    env.obstacles.add(ground)
    env.obstacles.add(block)
    env.obstacles.add(tall_block)

    del char

    playing = True
    while playing:
        clock.tick(60)
        screen.fill((0, 32, 32))
        env.update()
        env.draw(screen)

        last_pos = mouse_trail(last_pos, (255, 0, 0))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                playing = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                # reset player on right-click
                click = pygame.mouse.get_pressed()
                if click[L]:
                    playing = interact_loop(env)
                elif click[R]:
                    for sprite in env.player.sprites():
                        sprite.kill()
                    new_char = pl.Player(pygame.mouse.get_pos(), 'sprite/neon_hawk', 'right_smoke', env)
                    env.player.add(new_char)
                    env.interactive.add(new_char)

    pygame.quit()
