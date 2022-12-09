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
        self.color = s.ENEMY
        self.image.fill(self.color)
        self.image.set_colorkey(s.SPACE)
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = pos
        self.vel_x, self.vel_y = (0, 0)
        self.cooldown = 48 + random.randrange(32)
        self.eruption_timer = 0
        self.vitality = 32 + random.randrange(128)
        self.cancer_timer = 0

    def update(self):
        self.eruption_timer = (self.eruption_timer + 1) % self.cooldown
        self.cancer_timer = (self.cancer_timer + 1) % self.vitality
        self.rect.x += self.vel_x
        self.rect.y += self.vel_y
        if self.eruption_timer == 0:
            bullets.add(EnemyShot((self.rect.x, self.rect.y), pygame.mouse.get_pos()))
        if self.cancer_timer == 0:
            objects.add(Chunk(self, (random.randrange(33)-16, random.randrange(33)-16)))
            self.color = (self.color[0] * 7 / 8, self.color[1], self.color[2] * 3 / 4)
        s.check_bounds(self)


class Accelerator(Enemy):
    def __init__(self, pos):
        super(Accelerator, self).__init__(pos)
        self.vel_x, self.vel_y = (0 - random.randrange(4), 0)
        self.name = 'Rush'

    def update(self):
        super(Accelerator, self).update()
        self.vel_x *= 65/64


class Decelerator(Enemy):
    def __init__(self, pos):
        super(Decelerator, self).__init__(pos)
        self.vel_x, self.vel_y = (-8 - random.randrange(16), 0)
        self.name = 'Brake'

    def update(self):
        super(Decelerator, self).update()
        self.vel_x *= 63/64


class Chunk(Enemy):
    # living enemies will cover themselves in gross new shit
    def __init__(self, host, offset):
        super(Chunk, self).__init__((host.rect.x, host.rect.y))
        self.host = host
        self.vitality = host.vitality
        self.x_offset, self.y_offset = offset
        self.color = (host.color[0] * 7/8, host.color[1], host.color[2] * 3/4)
        self.image.fill(self.color)

    def update(self):
        self.rect.x = self.host.rect.x + self.x_offset
        self.rect.y = self.host.rect.y + self.y_offset


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
        self.rect.x, self.rect.y = pos
        self.color = s.ENEMY_BULLET
        pygame.draw.circle(surface=self.image, color=self.color, center=(5, 5), radius=5)

    def update(self):
        self.rect.x += self.vel_x
        self.rect.y += self.vel_y
        bullets.add(Trail((self.rect.x, self.rect.y), 5))
        s.check_bounds(self)


class Trail(pygame.sprite.Sprite):
    def __init__(self, pos, size):
        super(Trail, self).__init__()
        self.size = size
        self.radius = size
        self.image = pygame.Surface((2*self.size+1, 2*self.size+1))
        self.image.set_colorkey(s.SPACE)
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = pos
        self.color = s.ENEMY_BULLET

    def update(self):
        self.image.fill(s.SPACE)
        pygame.draw.circle(surface=self.image, color=self.color,
                           center=(self.size, self.size), radius=self.radius)
        self.radius = self.radius * 7/8
        self.color = (self.color[0]*7/8, self.color[1], self.color[2]*3/4)
        if self.radius < 2:
            self.kill()
            del self


if __name__ == '__main__':
    clock = pygame.time.Clock()
    pygame.display.set_caption('Enemy Test')

    timer = 0
    playing = True
    while playing:
        clock.tick(60)
        s.screen.fill(s.SPACE)

        objects.update()
        bullets.update()
        bullets.draw(s.screen)
        objects.draw(s.screen)

        timer += 1
        if timer % 23 == 0:
            # add obstacle to the list
            new_enemy((s.screen.get_width() - 16, timer % s.screen.get_height()))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                playing = False
            if event.type == pygame.KEYDOWN:
                objects.empty()
                bullets.empty()
    pygame.quit()
