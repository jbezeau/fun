import pygame
import math
import static as s

ship = pygame.sprite.Group()
bullets = pygame.sprite.Group()


def build_ship(pos):
    new = Player(pos)
    ship.add(new)
    ship.add(CurveGun(new, (8, 4)))
    ship.add(CurveGun(new, (8, -4)))
    ship.add(FwdGun(new, (-8, 6)))
    ship.add(FwdGun(new, (-8, -6)))
    ship.add(Engine(new, (-16, 6)))
    ship.add(Engine(new, (-16, -6)))
    return new


class Player(pygame.sprite.Sprite):
    def __init__(self, pos):
        super(Player, self).__init__()
        self.image = pygame.Surface((8, 8))
        self.image.fill(s.PLAYER)
        self.image.set_colorkey(s.SPACE)
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = pos

    def update(self):
        v = math.sqrt(s.distance((self.rect.x, self.rect.y), pygame.mouse.get_pos()))
        dx, dy = s.direction((self.rect.x, self.rect.y), pygame.mouse.get_pos())
        self.rect.x += (dx * v)
        self.rect.y += (dy * v)


class ShipPart(pygame.sprite.Sprite):
    def __init__(self, parent, offset):
        super(ShipPart, self).__init__()
        self.parent = parent
        self.image = pygame.Surface((8, 8))
        self.image.fill(s.SHIP)
        self.image.set_colorkey(s.SPACE)
        self.rect = self.image.get_rect()
        self.rect.x = self.parent.rect.x
        self.rect.y = self.parent.rect.y
        self.x_offset, self.y_offset = offset

    def update(self):
        self.rect.x = self.parent.rect.x + self.x_offset
        self.rect.y = self.parent.rect.y + self.y_offset


class FwdGun(ShipPart):
    def __init__(self, parent, offset):
        super(FwdGun, self).__init__(parent, offset)
        self.cooldown = 8
        self.timer = 0

    def update(self):
        super(FwdGun, self).update()
        self.timer = (self.timer + 1) % self.cooldown
        if self.timer == 0:
            bullets.add(Shot((self.rect.x, self.rect.y), (self.rect.x + 8, self.rect.y)))


class SideGun(ShipPart):
    def __init__(self, parent, offset):
        super(SideGun, self).__init__(parent, offset)
        self.cooldown = 8
        self.timer = 0

    def update(self):
        super(SideGun, self).update()
        self.timer = (self.timer + 1) % self.cooldown
        if self.timer == 0:
            bullets.add(Shot((self.rect.x, self.rect.y),
                             (self.rect.x + self.x_offset, self.rect.y + self.y_offset)))


class CurveGun(ShipPart):
    def __init__(self, parent, offset):
        super(CurveGun, self).__init__(parent, offset)
        self.cooldown = 8
        self.timer = 0

    def update(self):
        super(CurveGun, self).update()
        self.timer = (self.timer + 1) % self.cooldown
        if self.timer == 0:
            bullets.add(Curve((self.rect.x, self.rect.y),
                              (self.rect.x + self.x_offset, self.rect.y + self.y_offset)))


class Turret(ShipPart):
    def __init__(self, parent, offset):
        super(Turret, self).__init__(parent, offset)
        self.cooldown = 8
        self.timer = 0

    def update(self):
        super(Turret, self).update()
        self.timer = (self.timer + 1) % self.cooldown
        if self.timer == 0:
            bullets.add(Shot((self.rect.x, self.rect.y), pygame.mouse.get_pos()))


class Engine(ShipPart):
    def __init__(self, parent, offset):
        super(Engine, self).__init__(parent, offset)

    def update(self):
        super(Engine, self).update()
        bullets.add(Explosion((self.rect.x-15, self.rect.y-6), 11))


class Shot(pygame.sprite.Sprite):
    def __init__(self, pos, destination):
        super(Shot, self).__init__()
        self.vel_x, self.vel_y = s.direction(pos, destination)
        self.vel_x *= 8
        self.vel_y *= 8
        self.image = pygame.Surface((7, 7))
        self.image.fill(s.SPACE)
        self.image.set_colorkey(s.SPACE)
        self.rect = self.image.get_rect()
        pygame.draw.circle(surface=self.image, color=s.PLAYER_BULLET, center=(3, 3), radius=3)
        self.rect.x, self.rect.y = pos

    def update(self):
        self.rect.x += self.vel_x
        self.rect.y += self.vel_y
        s.check_bounds(self)


class Curve(Shot):
    def __init__(self, pos, destination):
        super(Curve, self).__init__(pos, destination)
        # adjust for rounding
        self.vel_y += 0.5

    def update(self):
        super(Curve, self).update()
        if self.vel_y > 0.1:
            self.vel_y = self.vel_y - 0.1
        elif 0 > self.vel_y:
            self.vel_y = self.vel_y + 0.1


class Explosion(pygame.sprite.Sprite):
    def __init__(self, pos, size):
        super(Explosion, self).__init__()
        self.size = size
        self.radius = size
        self.image = pygame.Surface((2*self.size+1, 2*self.size+1))
        self.image.set_colorkey(s.SPACE)
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = pos

    def update(self):
        self.image.fill(s.SPACE)
        pygame.draw.circle(surface=self.image, color=s.PLAYER_BULLET,
                           center=(self.size, self.size), radius=self.radius)
        self.radius = self.radius * 7/8
        if self.radius < 1:
            self.kill()
            del self
