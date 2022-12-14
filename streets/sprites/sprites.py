import pygame
import colours
import studio
import sheets


class Editor:
    # need to start bundling data together
    # connection between editor and sprite on sheet must be intimate
    def __init__(self, copy_editor=None):
        self.sprite = sprite_pos
        self.surface, self.tag = self.get_sprite()
        if copy_editor is not None and self.tag is None:
            self.surface.blit(copy_editor.surface, (0, 0))
            self.tag = copy_editor.tag
        self.rect = self.surface.get_rect()
        self.rect.x = editor_pos.x
        self.rect.y = editor_pos.y

    def get_sprite(self):
        lil_editor = pygame.Surface(studio.SPRITE_SIZE)
        lil_editor.blit(sprite_sheet, (0, 0), pygame.Rect(self.sprite, studio.SPRITE_SIZE))
        return pygame.transform.scale(lil_editor, studio.EDITOR_SIZE), sprite_meta.get(self.sprite)

    def save_sprite(self):
        lil_editor = pygame.transform.scale(self.surface, studio.SPRITE_SIZE)
        sprite_sheet.blit(lil_editor, self.sprite)
        self.tag = studio.get_text_input('Sprite tag: ', self.tag)
        return self.tag

    def paint(self, colour):
        rel_x, rel_y = pygame.mouse.get_pos()
        px_x = rel_x-self.rect.x
        px_x = px_x - (px_x % studio.EDITOR_PIXEL)
        px_y = rel_y-self.rect.y
        px_y = px_y - (px_y % studio.EDITOR_PIXEL)
        pixel = pygame.Surface((studio.EDITOR_PIXEL, studio.EDITOR_PIXEL))
        pixel.fill(colour)
        self.surface.blit(pixel, (px_x, px_y))
        studio.screen.blit(self.surface, self.rect)

    def draw(self):
        studio.screen.blit(self.surface, self.rect)


def go_next_sprite(pos):
    sprite_x, sprite_y = pos
    new_pos = (sprite_x + studio.SPRITE_SIZE[0], sprite_y)
    if studio.SHEET_SIZE[0] > new_pos[0] + studio.SPRITE_SIZE[0] > 0:
        return new_pos
    return None


def go_next_editor(pos):
    new_pos = pos
    new_pos.x += studio.EDITOR_SIZE[0] + 32
    if studio.SHEET_SIZE[0] > new_pos[0] + studio.EDITOR_SIZE[0] > 0:
        return new_pos
    return None


if __name__ == '__main__':
    pygame.display.set_caption('Sprite Editor')

    sprite_sheet, sprite_meta, save_filename = sheets.load_sprite_sheet()
    editors = {}

    sprite_pos = (0, 0)
    editors = {}
    editor_pos = pygame.Rect((32, 64), studio.EDITOR_SIZE)
    focus_editor = Editor()
    editors[tuple(focus_editor.rect)] = focus_editor
    overlay = pygame.Surface((studio.SHEET_SIZE[0], studio.SHEET_SIZE[1] - 64))
    overlay = overlay.convert_alpha()
    overlay.set_alpha(127)
    overlay.set_colorkey(studio.COLOUR_KEY)
    highlight = pygame.Surface(studio.EDITOR_SIZE)
    highlight.fill(studio.COLOUR_KEY)

    # edit sheet or copy and edit new
    editing = True
    status_shown = False
    palette = studio.draw_colour_bar()  # only need to do this once TBH
    draw_colour = None
    while editing:
        studio.clock.tick(60)
        overlay.fill(studio.SCREEN_COLOUR)
        overlay.blit(highlight, (editor_pos.x, editor_pos.y-32))
        for v in list(editors.values()):
            v.draw()
        studio.screen.blit(overlay, (0, 32))
        pygame.display.flip()

        mouse_x, mouse_y = pygame.mouse.get_pos()
        if 32 > mouse_y and not status_shown:
            studio.draw_colour_bar()

        # check for selecting a colour from the palette
        mouse_rect = pygame.Rect(pygame.mouse.get_pos(), (1, 1))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # exit but not immediately
                editing = False
                sheets.save_sprite_sheet(save_filename)
            if event.type == pygame.KEYDOWN:
                if status_shown:
                    # if we show a status, dismiss with any key
                    status_shown = studio.clear_status_text()
                elif event.key == pygame.K_ESCAPE:
                    # escape resets current editor
                    focus_editor.get_sprite()
                    status_shown = studio.draw_status_text(
                        f'Reset edits to sprite {sprite_pos}', studio.STATUS_YELLOW)
                elif event.key == pygame.K_RETURN:
                    sprite_meta[sprite_pos] = focus_editor.save_sprite()
                    status_shown = studio.draw_status_text(
                        f'Saved sprite {sprite_meta[sprite_pos]}', studio.STATUS_GREEN)
                elif event.key == pygame.K_RIGHT:
                    next_sprite_pos = go_next_sprite(sprite_pos)
                    next_editor_pos = go_next_editor(editor_pos)
                    if next_sprite_pos is None:
                        status_shown = studio.draw_status_text(
                            'Out of bounds on sprite sheet', studio.STATUS_RED)
                    elif next_editor_pos is None:
                        status_shown = studio.draw_status_text(
                            'Out of bounds on new editor', studio.STATUS_RED)
                    else:
                        sprite_pos = next_sprite_pos
                        editor_pos = next_editor_pos
                        focus_editor = Editor(focus_editor)
                        editors[tuple(focus_editor.rect)] = focus_editor
                        status_shown = studio.clear_status_text()
                        status_shown = studio.draw_status_text(
                            f'Editing sprite {sprite_pos}', studio.STATUS_GREEN)
                else:
                    studio.clear_status_text()
                    studio.screen.blit(sprite_sheet, (0, 0))
                    new_filename = studio.save_sprite_sheet(save_filename)
                    status_shown = True
                    if new_filename is not None:
                        save_filename = new_filename
            if event.type == pygame.MOUSEBUTTONDOWN:
                status_shown = studio.clear_status_text()
                colour_choice = mouse_rect.collidedict(palette)
                if colour_choice:
                    draw_colour = colour_choice[1]
                    status_shown = studio.draw_status_text('Current colour', draw_colour)

        # check for drawing on the editor
        mouse_buttons = pygame.mouse.get_pressed()
        if draw_colour and mouse_buttons[0]:
            focus_selection = mouse_rect.collidedict(editors)
            if focus_selection:
                focus_editor = focus_selection[1]
                editor_pos = focus_editor.rect
                sprite_pos = focus_editor.sprite
                focus_editor.paint(draw_colour)
                status_shown = studio.draw_status_text(
                    f'Editing sprite {sprite_pos}, ENTER to save or ESCAPE to reset', draw_colour)

    pygame.quit()
