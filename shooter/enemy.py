import pygame
import random
import static as s


objects = pygame.sprite.Group()
bullets = pygame.sprite.Group()


def new_enemy(pos):
    # choose a random enemy type
    i = random.randrange(2)
    match int(i):
        case 0:
            return objects.add(Accelerator(pos))
        case 1:
            return objects.add(Decelerator(pos))


class Enemy(pygame.sprite.Sprite):
    def __init__(self, pos):
        super(Enemy, self).__init__()
        self.image = pygame.Surface((16, 16))
        self.image.fill(s.ENEMY)
        self.image.set_colorkey(s.SPACE)
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = pos
        self.vel_x, self.vel_y = (0, 0)
        self.cooldown = 48 + random.randrange(32)
        self.timer = 0

    def update(self):
        self.timer = (self.timer+1) % self.cooldown
        self.rect.x += self.vel_x
        self.rect.y += self.vel_y
        if self.timer == 0:
            bullets.add(EnemyShot((self.rect.x, self.rect.y), pygame.mouse.get_pos()))
        s.check_bounds(self)


class Accelerator(Enemy):
    def __init__(self, pos):
        super(Accelerator, self).__init__(pos)
        self.vel_x, self.vel_y = (0 - random.randrange(4), 0)

    def update(self):
        super(Accelerator, self).update()
        self.vel_x *= 65/64


class Decelerator(Enemy):
    def __init__(self, pos):
        super(Decelerator, self).__init__(pos)
        self.vel_x, self.vel_y = (-8 - random.randrange(16), 0)

    def update(self):
        super(Decelerator, self).update()
        self.vel_x *= 63/64


class EnemyShot(pygame.sprite.Sprite):
    def __init__(self, pos, destination):
        super(EnemyShot, self).__init__()
        self.vel_x, self.vel_y = s.direction(pos, destination)
        self.vel_x *= 4
        self.vel_y *= 4
        self.image = pygame.Surface((11, 11))
        self.image.fill(s.SPACE)
        self.image.set_colorkey(s.SPACE)
        self.rect = self.image.get_rect()
        pygame.draw.circle(surface=self.image, color=s.ENEMY_BULLET, center=(5, 5), radius=5)
        self.rect.x, self.rect.y = pos

    def update(self):
        self.rect.x += self.vel_x
        self.rect.y += self.vel_y
        s.check_bounds(self)
