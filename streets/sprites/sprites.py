import pygame
import studio
import sheets

WORK_SIZE = (1280, 896)


class Editor:
    # need to start bundling data together
    # connection between editor and sprite on sheet must be intimate
    def __init__(self, sprite, editor, copy_editor=None):
        self.sprite = sprite
        self.surface, self.tag = self.get_sprite()
        if copy_editor is not None and self.tag is None:
            self.surface.blit(copy_editor.surface, (0, 0))
            self.tag = copy_editor.tag
        self.rect = self.surface.get_rect()
        self.rect.x, self.rect.y = editor.x, editor.y

    def get_sprite(self):
        lil_editor = pygame.Surface(studio.SPRITE_SIZE)
        lil_editor.blit(sprite_sheet, (0, 0), self.sprite)
        return pygame.transform.scale(lil_editor, studio.EDITOR_SIZE), sprite_meta.get(tuple(self.sprite))

    def save_sprite(self):
        lil_editor = pygame.transform.scale(self.surface, studio.SPRITE_SIZE)
        sprite_sheet.blit(lil_editor, self.sprite)
        self.tag = studio.get_text_input('Sprite tag: ', self.tag)
        return self.tag

    def paint(self, colour):
        rel_x, rel_y = pygame.mouse.get_pos()
        px_x = rel_x-self.rect.x
        px_x = px_x - (px_x % studio.EDITOR_PIXEL)

        # additional 32px Y offset from status bar at top of screen
        px_y = rel_y-self.rect.y-32
        px_y = px_y - (px_y % studio.EDITOR_PIXEL)

        pixel = pygame.Surface((studio.EDITOR_PIXEL, studio.EDITOR_PIXEL))
        pixel.fill(colour)
        self.surface.blit(pixel, (px_x, px_y))
        work.blit(self.surface, self.rect)


def next_sprite_column(editor):
    if editor is None:
        return None

    new_sprite_pos = pygame.Rect(editor.sprite)
    new_sprite_pos.x += studio.SPRITE_SIZE[0]
    new_editor_pos = pygame.Rect(editor.rect)
    new_editor_pos.x += studio.EDITOR_SIZE[0] + 32
    if studio.SHEET_SIZE[0] > new_editor_pos.x + studio.EDITOR_SIZE[0] \
            and studio.SHEET_SIZE[0] > new_sprite_pos.x + studio.SPRITE_SIZE[0]:
        new_editor = Editor(new_sprite_pos, new_editor_pos, editor)
        editors[tuple(new_editor.rect)] = new_editor
        return new_editor
    return None


def next_sprite_row(editor):
    if editor is None:
        return None

    new_sprite_pos = pygame.Rect(editor.sprite)
    new_sprite_pos.y += studio.SPRITE_SIZE[1]
    new_editor_pos = pygame.Rect(editor.rect)
    new_editor_pos.y += studio.EDITOR_SIZE[1] + 32
    if studio.SHEET_SIZE[1] > new_editor_pos.y + studio.EDITOR_SIZE[1] \
            and studio.SHEET_SIZE[1] > new_sprite_pos.y + studio.SPRITE_SIZE[1]:
        new_editor = Editor(new_sprite_pos, new_editor_pos, editor)
        editors[tuple(new_editor.rect)] = new_editor
        return new_editor
    return None


if __name__ == '__main__':
    pygame.display.set_caption('Sprite Editor')

    sprite_sheet, sprite_meta, save_filename = sheets.load_sprite_sheet()

    editors = {}
    sprite_pos = pygame.Rect((0, 0), studio.SPRITE_SIZE)
    editor_pos = pygame.Rect((16, 32), studio.EDITOR_SIZE)
    focus_editor = Editor(sprite_pos, editor_pos)
    editors[tuple(focus_editor.rect)] = focus_editor

    overlay = pygame.Surface(WORK_SIZE)
    overlay = overlay.convert_alpha()
    overlay.set_alpha(127)
    overlay.set_colorkey(studio.COLOUR_KEY)

    highlight = pygame.Surface(studio.EDITOR_SIZE)
    highlight.fill(studio.COLOUR_KEY)

    work = pygame.Surface(WORK_SIZE)

    # edit sheet or copy and edit new
    editing = True
    status_shown = False
    palette = studio.draw_colour_bar()  # only need to do this once TBH
    draw_colour = None
    while editing:
        studio.clock.tick(60)
        # draw active editors
        for v in list(editors.values()):
            work.blit(v.surface, (v.rect.x, v.rect.y))
        # cover work surface with tint
        overlay.fill(studio.SCREEN_COLOUR)
        if focus_editor is not None:
            # except focused editor (if any)
            overlay.blit(highlight, focus_editor.rect)
        work.blit(overlay, (0, 0))

        studio.screen.blit(work, (0, 32))
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
                sheets.save_sprite_sheet(sprite_sheet, sprite_meta, save_filename)
            if event.type == pygame.KEYDOWN:
                if status_shown:
                    # if we show a status, dismiss with any key
                    status_shown = studio.clear_status_text()
                elif event.key == pygame.K_ESCAPE:
                    if focus_editor:
                        # escape resets current editor
                        focus_editor.get_sprite()
                        status_shown = studio.draw_status_text(
                            f'Reset edits to sprite {tuple(focus_editor.sprite)}', studio.STATUS_YELLOW)
                elif event.key == pygame.K_BACKQUOTE:
                    search_default = None
                    if focus_editor:
                        search_default = focus_editor.tag
                    search = studio.get_text_input('Enter tag to search: ', search_default)
                    jump_sprite = sheets.search_sprite(sprite_sheet, sprite_meta, search)
                    studio.clear_status_text()
                    if jump_sprite:
                        editors.clear()
                        editor_pos = pygame.Rect((16, 32), studio.EDITOR_SIZE)
                        focus_editor = Editor(jump_sprite, editor_pos, focus_editor)
                        editors[tuple(focus_editor.rect)] = focus_editor
                elif event.key == pygame.K_RETURN:
                    sprite_meta[tuple(focus_editor.sprite)] = focus_editor.save_sprite()
                    status_shown = studio.draw_status_text(
                        f'Saved sprite {sprite_meta[tuple(focus_editor.sprite)]}', studio.STATUS_GREEN)
                elif focus_editor and event.key == pygame.K_RIGHT:
                    # create next frame, carry tag to new frame if possible
                    focus_editor = next_sprite_column(focus_editor)
                    if focus_editor is None:
                        status_shown = studio.draw_status_text(f'No room on this row', studio.STATUS_RED)
                elif focus_editor and event.key == pygame.K_DOWN:
                    # create new frame down, tags should only run horizontally for animation
                    new_tag = studio.get_text_input('Enter tag for new series: ', None)
                    if new_tag:
                        focus_editor = next_sprite_row(focus_editor)
                        focus_editor.tag = new_tag
                    if focus_editor is None:
                        status_shown = studio.draw_status_text(f'No room on this column', studio.STATUS_RED)
                else:
                    studio.screen.blit(sprite_sheet, (0, 0))
                    new_filename = sheets.save_sprite_sheet(sprite_sheet, sprite_meta, save_filename)
                    status_shown = True
                    if new_filename is not None:
                        save_filename = new_filename
            if event.type == pygame.MOUSEBUTTONDOWN:
                # handle clicking on palette bar
                status_shown = studio.clear_status_text()
                studio.screen.blit(work, (0, 32))
                colour_choice = mouse_rect.collidedict(palette)
                focus_selection = mouse_rect.collidedict(editors)
                if colour_choice:
                    draw_colour = colour_choice[1]
                    status_shown = studio.draw_status_text('Current colour', draw_colour)
                if colour_choice is None and focus_selection is None:
                    draw_colour = None
                    focus_editor = None

        # check for drawing on the editor
        mouse_buttons = pygame.mouse.get_pressed()
        if mouse_buttons[0]:
            focus_selection = mouse_rect.collidedict(editors)
            if focus_selection:
                focus_editor = focus_selection[1]
                if draw_colour:
                    focus_editor.paint(draw_colour)
                    status_shown = studio.draw_status_text(f'ENTER to save or ESCAPE to reset', draw_colour)

    pygame.quit()
