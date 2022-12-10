import pygame
import math
import random
import static as s


ship = pygame.sprite.Group()
bullets = pygame.sprite.Group()


class Player(pygame.sprite.Sprite):
    def __init__(self, pos, name=None):
        super(Player, self).__init__()
        self.image = pygame.Surface((8, 8))
        self.image.fill(s.PLAYER)
        self.image.set_colorkey(s.SPACE)
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = pos
        self.name = name

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


class TailCurveGun(ShipPart):
    # fires a curve shot with its x direction reversed, so it aims forward if mounted behind cockpit
    def __init__(self, parent, offset):
        super(TailCurveGun, self).__init__(parent, offset)
        self.cooldown = 8
        self.timer = 0

    def update(self):
        super(TailCurveGun, self).update()
        self.timer = (self.timer + 1) % self.cooldown
        if self.timer == 0:
            bullets.add(Curve((self.rect.x, self.rect.y),
                              (self.rect.x - self.x_offset, self.rect.y + self.y_offset)))


class Turret(ShipPart):
    # fires towards mouse position, from gun through hit box when ship is at rest
    def __init__(self, parent, offset):
        super(Turret, self).__init__(parent, offset)
        self.cooldown = 8
        self.timer = 0

    def update(self):
        super(Turret, self).update()
        self.timer = (self.timer + 1) % self.cooldown
        if self.timer == 0:
            bullets.add(Shot((self.rect.x, self.rect.y), pygame.mouse.get_pos()))


class TailTurret(ShipPart):
    # turret that fires away from mouse position rather than toward
    def __init__(self, parent, offset):
        super(TailTurret, self).__init__(parent, offset)
        self.cooldown = 8
        self.timer = 0

    def update(self):
        super(TailTurret, self).update()
        self.timer = (self.timer + 1) % self.cooldown
        if self.timer == 0:
            bullets.add(TailShot((self.rect.x, self.rect.y), pygame.mouse.get_pos()))


class Engine(ShipPart):
    def __init__(self, parent, offset):
        super(Engine, self).__init__(parent, offset)

    def update(self):
        super(Engine, self).update()
        bullets.add(Explosion((self.rect.x-15, self.rect.y-7), 11))


class Shot(pygame.sprite.Sprite):
    def __init__(self, pos, destination):
        super(Shot, self).__init__()
        self.vel_x, self.vel_y = s.direction(pos, destination)
        self.vel_x *= 8
        self.vel_y *= 8
        self.vel_y += 0.5  # fix rounding
        self.image = pygame.Surface((7, 7))
        self.image.fill(s.SPACE)
        self.image.set_colorkey(s.SPACE)
        self.rect = self.image.get_rect()
        pygame.draw.circle(surface=self.image, color=s.PLAYER_BULLET, center=(3, 3), radius=3)
        self.rect.x, self.rect.y = pos

    def update(self):
        self.rect.x += self.vel_x
        self.rect.y += self.vel_y
        bullets.add(Trail((self.rect.x, self.rect.y), 3))
        s.check_bounds(self)


class TailShot(Shot):
    # shot with reversed attack direction
    def __init__(self, pos, destination):
        super(TailShot, self).__init__(pos, destination)
        self.vel_x *= -1
        self.vel_y = (self.vel_y * -1) + 0.5  # adjust for rounding


class Curve(Shot):
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
        self.color = s.PLAYER_BULLET

    def update(self):
        self.image.fill(s.SPACE)
        pygame.draw.circle(surface=self.image, color=self.color,
                           center=(self.size, self.size), radius=self.radius)
        self.radius = self.radius * 7/8
        self.color = (self.color[0], self.color[1]*7/8, self.color[2]*15/16)
        if self.radius < 1:
            self.kill()
            del self


class Trail(Explosion):
    def update(self):
        self.image.fill(s.SPACE)
        pygame.draw.circle(surface=self.image, color=self.color,
                           center=(self.size, self.size), radius=self.radius)
        self.radius = self.radius * 3/4
        self.color = (self.color[0], self.color[1]*3/4, self.color[2]*7/8)
        if self.radius < 1:
            self.kill()
            del self


def tiger(pos):
    # constant forward firepower
    new = Player(pos)
    new.name = 'Tiger'
    ship.add(new)
    ship.add(CurveGun(new, (8, 4)))
    ship.add(CurveGun(new, (8, -4)))
    ship.add(TailCurveGun(new, (-8, 6)))
    ship.add(TailCurveGun(new, (-8, -6)))
    ship.add(FwdGun(new, (-12, 14)))
    ship.add(FwdGun(new, (-12, -14)))
    ship.add(Engine(new, (-16, 6)))
    ship.add(Engine(new, (-16, -6)))
    return new


def panther(pos):
    # heavy direct punch and four offensive turrets
    new = Player(pos)
    new.name = 'Panther'
    ship.add(new)
    ship.add(FwdGun(new, (8, 4)))
    ship.add(FwdGun(new, (8, -4)))
    ship.add(FwdGun(new, (16, 0)))
    ship.add(Turret(new, (-8, 4)))
    ship.add(Turret(new, (-8, -4)))
    ship.add(Turret(new, (-12, 12)))
    ship.add(Turret(new, (-12, -12)))
    ship.add(Engine(new, (-16, 4)))
    ship.add(Engine(new, (-16, -4)))
    return new


def jaguar(pos):
    # balanced forward firepower and three defensive turrets
    new = Player(pos)
    new.name = 'Jaguar'
    ship.add(new)
    ship.add(TailTurret(new, (8, 4)))
    ship.add(TailTurret(new, (8, -4)))
    ship.add(TailTurret(new, (16, 0)))
    ship.add(TailCurveGun(new, (-8, 4)))
    ship.add(TailCurveGun(new, (-8, -4)))
    ship.add(FwdGun(new, (-12, 12)))
    ship.add(FwdGun(new, (-12, -12)))
    ship.add(Engine(new, (-16, 0)))
    return new


def lion(pos):
    # wide angle scattershot with two offensive turrets
    new = Player(pos)
    new.name = 'Lion'
    ship.add(new)
    ship.add(SideGun(new, (16, 4)))
    ship.add(SideGun(new, (16, -4)))
    ship.add(SideGun(new, (8, 8)))
    ship.add(SideGun(new, (8, 0)))
    ship.add(SideGun(new, (8, -8)))
    ship.add(Turret(new, (-8, 6)))
    ship.add(Turret(new, (-8, -6)))
    ship.add(Engine(new, (-16, 6)))
    ship.add(Engine(new, (-16, -6)))
    return new


# dict of ship construction functions
ship_functions = {'Tiger': tiger, 'Panther': panther, 'Jaguar': jaguar, 'Lion': lion}


def build_ship(pos, name=None):
    if name is None:
        i = random.randrange(len(ship_functions))
        build_function = list(ship_functions.values())[i]
        return build_function(pos)
    else:
        build_function = ship_functions.get(name)
        return build_function(pos)


def draw_ship_name(name, colour=(0, 32, 0)):
    size = min(512, 2600 // len(name))
    font = pygame.font.Font(None, size)
    text_output = font.render(name, True, colour)
    text_rect = text_output.get_rect(centerx=s.screen.get_width() // 2, centery=s.screen.get_height()//2)
    s.screen.blit(text_output, text_rect)


if __name__ == '__main__':
    clock = pygame.time.Clock()
    pygame.display.set_caption('Player Ship Test')
    ship_list = list(ship_functions.keys())
    ship_num = 0

    p1 = build_ship((s.screen.get_width()//3, s.screen.get_height()//2))

    timer = 0
    playing = True
    while playing:
        clock.tick(60)
        s.screen.fill(s.SPACE)

        draw_ship_name(p1.name)

        ship.update()
        bullets.update()
        bullets.draw(s.screen)
        ship.draw(s.screen)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                playing = False
            if event.type == pygame.KEYDOWN:
                ship.empty()
                del p1
                new_name = ship_list[ship_num]
                p1 = build_ship((s.screen.get_width()//3, s.screen.get_height()//2), new_name)
                ship_num = (ship_num + 1) % len(ship_list)
    pygame.quit()
