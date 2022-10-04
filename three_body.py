import pygame


EARTH = (128, 192, 255)
MOON = (128, 128, 128)
SPACE = (0, 0, 0)
STATUS_GREEN = (64, 128, 64)


def calc_gravity(body1, body2):
    dist2 = (body1.rect.centerx - body2.rect.centerx) ** 2 + (body1.rect.centery - body2.rect.centery) ** 2
    if dist2 > 0:
        body1.x_vel += (body2.rect.centerx - body1.rect.centerx) * body2.mass / dist2
        body1.y_vel += (body2.rect.centery - body1.rect.centery) * body2.mass / dist2
        body2.x_vel += (body1.rect.centerx - body2.rect.centerx) * body1.mass / dist2
        body2.y_vel += (body1.rect.centery - body2.rect.centery) * body1.mass / dist2


def input_gravity(pos, body1):
    dist2 = (pos[0] - body1.rect.centerx) ** 2 + (pos[1] - body1.rect.centery) ** 2
    if dist2 > 0:
        body1.x_vel += (pos[0] - body1.rect.x) * mouse_mass / dist2
        body1.y_vel += (pos[1] - body1.rect.y) * mouse_mass / dist2


def draw_status():
    if pygame.font:
        small_font = pygame.font.Font(None, 24)
        status = f'black hole mass {mouse_mass}'
        text_output = small_font.render(status, True, (16, 16, 16))
        text_rect = text_output.get_rect(centerx=screen.get_width()//2, top=2)
        text_surface.fill(STATUS_GREEN)
        text_surface.blit(text_output, text_rect)


# the game is called three-body problem, but we're only initializing two of these lol
class Body(pygame.sprite.Sprite):
    def __init__(self, size, color, initial_v):
        # self.image is required for pygame Sprite implementation
        super(Body, self).__init__()
        self.mass = size**3//1000
        self.x_vel, self.y_vel = initial_v
        self.image = pygame.Surface((2 * size, 2 * size))
        self.image.fill(SPACE)
        self.image.set_colorkey(SPACE)
        self.rect = self.image.get_rect()
        pygame.draw.circle(surface=self.image, color=color, center=(size, size), radius=size)

    def update(self):
        self.rect.x += int(self.x_vel)
        self.rect.y += int(self.y_vel)


if __name__ == '__main__':
    pygame.init()
    clock = pygame.time.Clock()
    screen = pygame.display.set_mode((1280, 960))
    pygame.display.set_caption('3-body problem')

    text_surface = pygame.Surface((screen.get_width(), 28))
    text_surface = text_surface.convert()

    mouse_mass = 0

    earth = Body(50, EARTH, (0, 0))
    earth.rect.x = 300
    earth.rect.y = 255

    moon = Body(10, MOON, (0, -13.0))
    moon.rect.x = 450
    moon.rect.y = 300

    planets = pygame.sprite.Group()
    planets.add(earth)
    planets.add(moon)

    temp_pos = None
    playing = True
    while playing:
        clock.tick(60)
        screen.fill(SPACE)
        draw_status()
        screen.blit(text_surface, (0, 0))
        planets.update()
        planets.draw(screen)
        pygame.display.flip()

        # calculate gravity for earth-moon system
        # I was surprised that changing frame rate doesn't disrupt orbit
        # guess this is neutral because velocity and force are both per-frame
        calc_gravity(earth, moon)

        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                buttons = pygame.mouse.get_pressed()
                if buttons[0]:
                    # left click to reset
                    earth.rect.x, earth.rect.y = pygame.mouse.get_pos()
                    earth.x_vel, earth.y_vel = (0, 0)
                    moon.rect.x, moon.rect.y = pygame.mouse.get_pos()
                    moon.rect.x += 150
                    moon.rect.y += 50
                    moon.x_vel, moon.y_vel = (0, -13)
                    mouse_mass = 0
                elif buttons[2]:
                    # right click down to start input on black hole change
                    pygame.mouse.get_rel()
                    temp_pos = pygame.mouse.get_pos()
            if event.type == pygame.MOUSEBUTTONUP:
                buttons = pygame.mouse.get_pressed()
                if temp_pos is not None:
                    rel_x, rel_y = pygame.mouse.get_rel()
                    mouse_mass -= rel_y//10
                    if 0 > mouse_mass:
                        mouse_mass = 0
                    pygame.mouse.set_pos([temp_pos[0], temp_pos[1]])
                    temp_pos = None
            elif event.type == pygame.QUIT:
                # yeet
                playing = False
            else:
                input_gravity(pygame.mouse.get_pos(), earth)
                input_gravity(pygame.mouse.get_pos(), moon)

    pygame.quit()
