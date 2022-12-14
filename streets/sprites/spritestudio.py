import glob
import pickle
import pygame
from pygame import image
import colours

# important measurements
SPRITE_SIZE = (8, 16)
SPRITE_RECT = (0, 0, 8, 16)
EDITOR_PIXEL = 16
EDITOR_SIZE = (128, 256)
SHEET_SIZE = (1280, 960)
PAINT_SIZE = (80, 32)
STATUS_SIZE = (1280, 32)

# UI colours
COLOUR_KEY = (128, 128, 128)
STATUS_GREEN = (32, 128, 32)
STATUS_YELLOW = (192, 192, 32)
STATUS_RED = (192, 32, 32)
SCREEN_COLOUR = (0, 0, 0)
TEXT_COLOUR = (192, 192, 192)


class Editor:
    # need to start bundling data together
    # connection between editor and sprite on sheet must be intimate
    def __init__(self, copy_editor=None):
        self.sprite = sprite_pos
        self.surface, self.tag = self.get_sprite()
        if self.tag is None and copy_editor is not None:
            self.surface.blit(copy_editor.surface, (0, 0))
            self.tag = copy_editor.tag
        self.surface = self.surface.convert_alpha()
        self.rect = self.surface.get_rect()
        self.rect.x = editor_pos.x
        self.rect.y = editor_pos.y

    def get_sprite(self):
        lil_editor = pygame.Surface(SPRITE_SIZE)
        lil_editor.blit(sprite_sheet, self.sprite, SPRITE_RECT)
        return pygame.transform.scale(lil_editor, EDITOR_SIZE), sprite_meta.get(self.sprite)

    def save_sprite(self):
        lil_editor = pygame.transform.scale(self.surface, SPRITE_SIZE)
        sprite_sheet.blit(lil_editor, self.sprite)
        self.tag = get_text_input('Sprite tag: ', self.tag)
        return self.tag

    def paint(self, colour):
        rel_x, rel_y = pygame.mouse.get_pos()
        px_x = rel_x-self.rect.x
        px_x = px_x - (px_x % EDITOR_PIXEL)
        px_y = rel_y-self.rect.y
        px_y = px_y - (px_y % EDITOR_PIXEL)
        pixel = pygame.Surface((EDITOR_PIXEL, EDITOR_PIXEL))
        pixel.fill(colour)
        self.surface.blit(pixel, (px_x, px_y))
        screen.blit(self.surface, self.rect)

    def draw(self, focus=False):
        if focus:
            self.surface.set_alpha(255)
        else:
            self.surface.set_alpha(128)
        screen.blit(self.surface, self.rect)


def draw_status_text(text, colour):
    status_output = font.render(text, True, (0, 0, 0))
    status_rect = status_output.get_rect(centerx=screen.get_width() // 2, centery=16)
    status.fill(colour)
    status.blit(status_output, status_rect)
    screen.blit(status, (0, 0))
    return True


def draw_colour_bar():
    status.fill(SCREEN_COLOUR)
    x = 0
    colour_select = {}
    for c in colours.PALETTE:
        patch = pygame.Surface(PAINT_SIZE)
        patch.fill(c)
        patch_rect = patch.get_rect()
        patch_rect.x = x
        status.blit(patch, (x, 0))
        x += 80
        colour_select[tuple(patch_rect)] = c
    screen.blit(status, (0, 0))
    return colour_select


def draw_input_bar(text, colour):
    display_value = font.render(text, True, (0, 0, 0))
    display_rect = display_value.get_rect(centerx=screen.get_width() // 2, centery=16)
    input_bar.fill(colour)
    input_bar.blit(display_value, display_rect)
    screen.blit(input_bar, (0, screen.get_height()-32))
    return True


def get_text_input(prompt, default):
    typing = True
    if default is not None:
        input_text = default
    else:
        input_text = ''
    while typing:
        clock.tick(60)
        draw_input_bar(f'{prompt}{input_text}', STATUS_GREEN)
        pygame.display.flip()

        for typing_event in pygame.event.get():
            if typing_event.type == pygame.QUIT:
                return None
            if typing_event.type == pygame.KEYDOWN:
                if typing_event.key == pygame.K_BACKSPACE:
                    input_text = input_text[:-1]
                elif typing_event.key == pygame.K_ESCAPE:
                    typing = False
                    input_text = None
                elif typing_event.key == pygame.K_RETURN:
                    typing = False
                else:
                    input_text = input_text + typing_event.unicode
    return input_text


def clear_status_text():
    screen.fill(SCREEN_COLOUR)
    for v in list(editors.values()):
        v.draw(False)
    draw_colour_bar()
    pygame.display.flip()
    return False


# sprite sheet functions
def load_sprite_sheet():
    sheet_list = glob.glob('*.png')

    if len(sheet_list) == 0:
        # create new sheet on empty directory
        new_sheet = pygame.Surface(SHEET_SIZE)
        new_sheet.fill(COLOUR_KEY)
        return new_sheet, {}, 'new_sheet'

    # list sprite sheets on screen
    draw_status_text('Select sprite sheet file', STATUS_GREEN)

    sheet_set = {}
    x, y = (2, 34)
    for sheet_name in sheet_list:
        sheet_text = font.render(sheet_name, True, TEXT_COLOUR)
        sheet_rect = sheet_text.get_rect()
        sheet_rect.x, sheet_rect.y = (x, y)
        screen.blit(sheet_text, (x, y))
        sheet_set[tuple(sheet_rect)] = sheet_name
        y += 24
        if y + font.get_height() > screen.get_height():
            y = 34
            x += screen.get_width()//8

    # choose template sheet
    loading = True
    while loading:
        clock.tick(60)
        pygame.display.flip()
        for load_sheet_event in pygame.event.get():
            if load_sheet_event.type == pygame.QUIT:
                pygame.quit()
            if load_sheet_event.type == pygame.MOUSEBUTTONDOWN:
                select_mouse_pos = pygame.Rect(pygame.mouse.get_pos(), (1, 1))
                select_sheet = select_mouse_pos.collidedict(sheet_set)
                if select_sheet is not None:
                    png_name = select_sheet[1]
                    bin_name = png_name[:-3] + 'bin'
                    load_sheet = pygame.image.load(png_name)
                    try:
                        file = open(bin_name, 'rb')
                        load_meta = pickle.load(file)
                        file.close()
                    except FileNotFoundError:
                        load_meta = {}
                    screen.fill(SCREEN_COLOUR)
                    return load_sheet, load_meta, png_name[:-4]
    # we should never see this
    return None, None, None


def save_sprite_sheet(filename):
    # prompt to save work on quit or key-down
    filename = get_text_input('Save file name: ', filename)
    if filename is not None:
        pygame.image.save(sprite_sheet, filename+'.png')
        file = open(filename+'.meta', 'wb')
        pickle.dump(sprite_meta, file)
        draw_status_text(f'{filename} saved', STATUS_GREEN)
    else:
        clear_status_text()
        draw_status_text('Save Canceled', STATUS_YELLOW)
    return filename


def go_next_frame(pos):
    sprite_x, sprite_y = pos
    new_pos = (sprite_x + SPRITE_SIZE[0], sprite_y)
    if SHEET_SIZE[0] > new_pos[0] + SPRITE_SIZE[0] > 0:
        return new_pos
    return None


def go_next_editor(pos):
    new_pos = pos
    new_pos.x += EDITOR_SIZE[0] + 32
    if SHEET_SIZE[0] > new_pos[0] + EDITOR_SIZE[0] > 0:
        return new_pos
    return None


if __name__ == '__main__':
    pygame.init()
    pygame.font.init()

    font = pygame.font.Font(None, 16)
    clock = pygame.time.Clock()
    screen = pygame.display.set_mode(SHEET_SIZE)
    status = pygame.Surface(STATUS_SIZE)
    input_bar = pygame.Surface(STATUS_SIZE)
    pygame.display.set_caption('Sprite Editor')

    sprite_sheet, sprite_meta, save_filename = load_sprite_sheet()
    editors = {}

    sprite_pos = (0, 0)
    editors = {}
    editor_pos = pygame.Rect((32, 64), EDITOR_SIZE)
    big_editor = Editor()
    editors[tuple(big_editor.rect)] = big_editor

    # edit sheet or copy and edit new
    editing = True
    status_shown = False
    palette = draw_colour_bar()  # only need to do this once TBH
    draw_colour = None
    while editing:
        clock.tick(60)
        editors[tuple(editor_pos)].draw(True)
        pygame.display.flip()

        mouse_x, mouse_y = pygame.mouse.get_pos()
        if 32 > mouse_y and not status_shown:
            draw_colour_bar()

        # check for selecting a colour from the palette
        mouse_rect = pygame.Rect(pygame.mouse.get_pos(), (1, 1))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # exit but not immediately
                editing = False
                save_sprite_sheet(save_filename)
            if event.type == pygame.KEYDOWN:
                if status_shown:
                    # if we show a status, dismiss with any key
                    status_shown = clear_status_text()
                elif event.key == pygame.K_ESCAPE:
                    # escape resets current editor
                    big_editor.get_sprite()
                    status_shown = draw_status_text(f'Reset edits to sprite {sprite_pos}', STATUS_YELLOW)
                elif event.key == pygame.K_RETURN:
                    sprite_meta[sprite_pos] = big_editor.save_sprite()
                    status_shown = clear_status_text()
                    status_shown = draw_status_text(f'Saved sprite {sprite_meta[sprite_pos]}', STATUS_GREEN)
                elif event.key == pygame.K_RIGHT:
                    next_sprite_pos = go_next_frame(sprite_pos)
                    next_editor_pos = go_next_editor(editor_pos)
                    if next_sprite_pos is None:
                        status_shown = draw_status_text('Out of bounds on sprite sheet', STATUS_RED)
                    elif next_editor_pos is None:
                        status_shown = draw_status_text('Out of bounds on new editor', STATUS_RED)
                    else:
                        sprite_pos = next_sprite_pos
                        editor_pos = next_editor_pos
                        big_editor = Editor(big_editor)
                        editors[tuple(big_editor.rect)] = big_editor
                        status_shown = clear_status_text()
                        status_shown = draw_status_text(f'Editing sprite {sprite_pos}', STATUS_GREEN)
                else:
                    screen.blit(sprite_sheet, (0, 0))
                    new_filename = save_sprite_sheet(save_filename)
                    if new_filename is None:
                        status_shown = True
                    else:
                        save_filename = new_filename
            if event.type == pygame.MOUSEBUTTONDOWN:
                if status_shown:
                    status_shown = clear_status_text()
                else:
                    colour_choice = mouse_rect.collidedict(palette)
                    if colour_choice:
                        draw_colour = colour_choice[1]
                        status_shown = draw_status_text('Current colour', draw_colour)

        # check for drawing on the editor
        mouse_buttons = pygame.mouse.get_pressed()
        if draw_colour and mouse_buttons[0]:
            focus_selection = mouse_rect.collidedict(editors)
            if focus_selection:
                focus_editor = focus_selection[1]
                focus_editor.paint(draw_colour)
                status_shown = draw_status_text(
                    f'Editing sprite {sprite_pos}, ENTER to save or ESCAPE to reset', draw_colour)

    pygame.quit()
