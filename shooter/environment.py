import pygame
import random
import static as s


objects = pygame.sprite.Group()
parallax = pygame.sprite.Group()


def new_obstacle(o, spacing=2.0):
    # if we put an obstacle on top we want the next on bottom etc
    new_orientation = not o

    new_height = s.screen.get_height() // 4 + random.randrange(s.screen.get_height() // 2)
    new_length = s.screen.get_width() // 8 + random.randrange(s.screen.get_width())
    shadow_height = new_height * 9/8
    shadow_length = new_length * 7/8

    if o:
        obs = Obstacle(s.screen.get_height() - new_height, new_length, new_height)
        shd = Shadow(s.screen.get_height() - shadow_height, shadow_length, shadow_height)
    else:
        obs = Obstacle(0, new_length, new_height)
        shd = Shadow(0, shadow_length, shadow_height)

    # test for collision on obs
    if pygame.sprite.spritecollideany(obs, objects, pygame.sprite.collide_rect_ratio(spacing)) is None:
        objects.add(obs)
        parallax.add(shd)
    else:
        del obs
        del shd
        new_orientation = o

    return new_orientation


def check_shadow_bounds(obstacle):
    # obstacle is alive as long as it's touching its shadow
    # the shadow's lifetime is bounded by the screen
    if pygame.sprite.spritecollideany(obstacle, parallax) is None:
        obstacle.kill()
        del obstacle


class Obstacle(pygame.sprite.Sprite):
    def __init__(self, top, wd, ht):
        super(Obstacle, self).__init__()
        self.image = pygame.Surface((wd, ht))
        self.image.fill(s.OBSTACLE)
        self.rect = self.image.get_rect()
        self.rect.x = s.screen.get_width() + 200
        self.rect.y = top
        self.vel_x = -5

    def update(self):
        self.rect.x += self.vel_x
        check_shadow_bounds(self)


class Shadow(Obstacle):
    def __init__(self, top, wd, ht):
        super(Shadow, self).__init__(top, wd, ht)
        self.image.fill(s.SHADOW)
        self.rect.x = s.screen.get_width()
        self.vel_x = -4


if __name__ == '__main__':
    clock = pygame.time.Clock()
    pygame.display.set_caption('Environment Test')
    orientation = True

    timer = 0
    playing = True
    while playing:
        clock.tick(240)
        s.screen.fill(s.SPACE)

        objects.update()
        parallax.update()
        parallax.draw(s.screen)
        objects.draw(s.screen)

        timer += 1
        if timer % 100 == 0:
            # add obstacle to the list
            orientation = new_obstacle(orientation)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                playing = False
            if event.type == pygame.KEYDOWN:
                objects.empty()
                parallax.empty()
    pygame.quit()
