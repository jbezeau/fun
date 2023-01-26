import pygame
import sprites
import sheets

WORK_SIZE = (1280, 896)


class Editor:
    # need to start bundling data together
    # connection between editor and sprite on sheet must be intimate
    def __init__(self, sprite, editor, copy_editor=None):
        # support animation
        self.animation = None
        self.frame_count = 0

        # sprite is the location we're working on in the sprite sheet
        self.sprite = sprite
        self.surface, self.tag = self.get_sprite()

        # new sprite location has no identity
        if self.tag is None:
            # copy image from parent editor
            if copy_editor is not None:
                self.surface.blit(copy_editor.surface, (0, 0))
                self.tag = copy_editor.tag

            l_meta = layer_meta[layer_display]
            l_tag = l_meta.get(tuple(self.sprite))
            # match tags with sprite from comparison layer
            if l_tag is not None:
                self.tag = l_tag

        self.rect = self.surface.get_rect()
        self.rect.x, self.rect.y = editor.x, editor.y

        # introduced to compensate for drawing surface being 32 px below top of window
        self.click_rect = pygame.Rect(self.rect)
        self.click_rect.y += 32

    def get_sprite(self):
        if self.animation:
            self.frame_count = (self.frame_count + 1) % (len(self.animation) * 10)
            frame = self.frame_count//10
            my_sprite = self.animation[frame]
        else:
            my_sprite = pygame.Rect(self.sprite)
        lil_editor = pygame.Surface(sprites.SPRITE_SIZE)
        lil_editor.blit(layer_sheets[layer_display], (0, 0), my_sprite)
        return pygame.transform.scale(lil_editor, sprites.EDITOR_SIZE), sprite_meta.get(tuple(self.sprite))

    def save_sprite(self):
        lil_editor = pygame.transform.scale(self.surface, sprites.SPRITE_SIZE)
        sprite_sheet.blit(lil_editor, self.sprite)
        tag = self.tag
        if tag is None:
            my_meta = layer_meta[layer_display]
            tag = my_meta[tuple(self.sprite)]
        self.tag = sprites.get_text_input('Sprite tag: ', tag)
        return self.tag

    def paint(self, colour):
        rel_x, rel_y = pygame.mouse.get_pos()
        px_x = rel_x-self.rect.x
        px_x = px_x - (px_x % sprites.EDITOR_PIXEL)

        # additional 32px Y offset from status bar at top of screen
        px_y = rel_y-self.rect.y-32
        px_y = px_y - (px_y % sprites.EDITOR_PIXEL)

        pixel = pygame.Surface((sprites.EDITOR_PIXEL, sprites.EDITOR_PIXEL))
        pixel.fill(colour)
        self.surface.blit(pixel, (px_x, px_y))

    def animate(self):
        if self.animation:
            self.reset()
        else:
            tag_list = list(sprite_meta.values())
            pos_list = list(sprite_meta.keys())
            index_list = []
            while tag_list.count(self.tag):
                i = tag_list.index(self.tag)
                index_list.append(pos_list[i])
                tag_list = tag_list[i+1:]
                pos_list = pos_list[i+1:]
            self.animation = index_list

    def reset(self):
        if self.animation:
            self.animation.clear()
        self.surface, _ = self.get_sprite()

    def draw(self):
        pygame.draw.rect(work, sprites.COLOUR_KEY, self.rect)
        if self.animation:
            draw_surface, _ = self.get_sprite()
        elif layer_display != 0:
            draw_surface, _ = self.get_sprite()
            work_overlay = pygame.Surface(WORK_SIZE)
            work_overlay.blit(self.surface, (0, 0))
            work_overlay.set_colorkey(sprites.COLOUR_KEY)
            work_overlay.set_alpha(128)
            draw_surface.blit(work_overlay, (0, 0))
        else:
            draw_surface = self.surface
        work.blit(draw_surface, (self.rect.x, self.rect.y))

    def flip(self, x_flip, y_flip):
        self.surface = pygame.transform.flip(self.surface, x_flip, y_flip)

    def rotate(self, angle):
        rotated = pygame.transform.rotate(self.surface, angle)
        self.surface.blit(rotated, (0, 0), pygame.Rect((30, 15), sprites.EDITOR_SIZE))


def next_sprite_column(editor):
    if editor is None:
        return None

    new_sprite_pos = pygame.Rect(editor.sprite)
    new_sprite_pos.x += sprites.SPRITE_SIZE[0]
    new_editor_pos = pygame.Rect(editor.rect)
    new_editor_pos.x += sprites.EDITOR_SIZE[0] + 32
    if sprites.SHEET_SIZE[0] > new_editor_pos.x + sprites.EDITOR_SIZE[0]:
        new_editor = Editor(new_sprite_pos, new_editor_pos, editor)
        editors[tuple(new_editor.click_rect)] = new_editor
        return new_editor
    return None


def next_sprite_row(editor):
    if editor is None:
        return None

    new_sprite_pos = pygame.Rect(editor.sprite)
    new_sprite_pos.y += sprites.SPRITE_SIZE[1]
    new_editor_pos = pygame.Rect(editor.rect)
    new_editor_pos.y += sprites.EDITOR_SIZE[1] + 32
    if sprites.SHEET_SIZE[1] > new_editor_pos.y + sprites.EDITOR_SIZE[1]:
        new_editor = Editor(new_sprite_pos, new_editor_pos, editor)
        editors[tuple(new_editor.click_rect)] = new_editor
        return new_editor
    return None


if __name__ == '__main__':
    pygame.display.set_caption('Sprite Editor')

    sprite_sheet, sprite_meta, save_filename = sheets.load_sprite_sheet()
    layer_sheets = {0: sprite_sheet}
    layer_meta = {0: sprite_meta}
    layer_display = 0

    editors = {}
    sprite_pos = pygame.Rect((0, 0), sprites.SPRITE_SIZE)
    editor_pos = pygame.Rect((16, 32), sprites.EDITOR_SIZE)
    focus_editor = Editor(sprite_pos, editor_pos)
    editors[tuple(focus_editor.click_rect)] = focus_editor

    overlay = pygame.Surface(WORK_SIZE)
    overlay = overlay.convert_alpha()
    overlay.set_alpha(127)
    overlay.set_colorkey(sprites.COLOUR_KEY)

    highlight = pygame.Surface(sprites.EDITOR_SIZE)
    highlight.fill(sprites.COLOUR_KEY)

    work = pygame.Surface(WORK_SIZE)

    # edit sheet or copy and edit new
    editing = True
    status_shown = False
    palette = sprites.draw_colour_bar()  # only need to do this once TBH
    draw_colour = None
    while editing:
        sprites.clock.tick(60)

        # draw active editors
        for v in list(editors.values()):
            v.draw()

        # cover work surface with tint
        overlay.fill(sprites.SCREEN_COLOUR)
        if focus_editor is not None:
            # except focused editor (if any)
            overlay.blit(highlight, focus_editor.rect)
        work.blit(overlay, (0, 0))

        sprites.screen.blit(work, (0, 32))
        pygame.display.flip()

        mouse_x, mouse_y = pygame.mouse.get_pos()
        if 32 > mouse_y:
            sprites.draw_colour_bar()

        # check for selecting a colour from the palette
        mouse_rect = pygame.Rect((mouse_x, mouse_y), (1, 1))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # exit but not immediately
                editing = False
                sheets.save_sprite_sheet(sprite_sheet, sprite_meta, save_filename)
            if event.type == pygame.KEYDOWN:
                mods = pygame.key.get_mods()

                if status_shown:
                    # if we show a status, dismiss with any key
                    status_shown = sprites.clear_status_text()

                elif event.key == pygame.K_ESCAPE:
                    # escape resets comparison layer selection
                    layer_display = 0

                    if focus_editor:
                        # escape resets current editor
                        focus_editor.reset()
                        status_shown = sprites.draw_status_text(
                            f'Reset edits to sprite {tuple(focus_editor.sprite)}', sprites.STATUS_YELLOW)

                elif event.key == pygame.K_BACKQUOTE:
                    # draw sprite sheet and search
                    search_default = None
                    if focus_editor:
                        search_default = focus_editor.tag
                    search = sprites.get_text_input('Enter tag to search: ', search_default)
                    jump_sprite = sheets.search_sprite(layer_sheets[layer_display], layer_meta[layer_display], search)
                    sprites.clear_status_text()
                    if jump_sprite:
                        editors.clear()
                        editor_pos = pygame.Rect((16, 32), sprites.EDITOR_SIZE)
                        focus_editor = Editor(jump_sprite, editor_pos, focus_editor)
                        editors[tuple(focus_editor.click_rect)] = focus_editor

                elif focus_editor and event.key == pygame.K_RETURN:
                    # save focused editor
                    sprite_meta[tuple(focus_editor.sprite)] = focus_editor.save_sprite()
                    status_shown = sprites.draw_status_text(
                        f'Saved sprite {sprite_meta[tuple(focus_editor.sprite)]}', sprites.STATUS_GREEN)

                elif focus_editor and event.key == pygame.K_UP:
                    # vertical flip sprite
                    focus_editor.flip(False, True)
                elif focus_editor and event.key == pygame.K_LEFT:
                    # horizontal flip sprite
                    if mods == 1 or mods == 2:
                        # rotate actually if shift held
                        focus_editor.rotate(15)
                    else:
                        focus_editor.flip(True, False)

                elif focus_editor and event.key == pygame.K_RIGHT:
                    # create next frame, carry tag to new frame if possible
                    if mods == 1 or mods == 2:
                        # rotate instead if holding shift
                        focus_editor.rotate(-15)
                    else:
                        focus_editor = next_sprite_column(focus_editor)
                        if focus_editor is None:
                            status_shown = sprites.draw_status_text(f'No room on this row', sprites.STATUS_RED)
                elif focus_editor and event.key == pygame.K_DOWN:
                    # create new frame down, tags should only run horizontally for animation
                    new_tag = sprites.get_text_input('Enter tag for new series: ', None)
                    if new_tag:
                        focus_editor = next_sprite_row(focus_editor)
                        focus_editor.tag = new_tag
                    if focus_editor is None:
                        status_shown = sprites.draw_status_text(f'No room on this column', sprites.STATUS_RED)

                elif focus_editor and event.key == pygame.K_SPACE:
                    # animation depends on metadata which is only relevant to base sheet
                    layer_display = 0
                    focus_editor.animate()

                elif pygame.K_9 >= event.key >= pygame.K_0:
                    # load additional sprite sheet for comparison
                    # sprite_sheet is mapped to actual 0, not pygame.K_0
                    if layer_sheets.get(event.key) is None:
                        # we can't load a new image to a layer that's already assigned
                        image, meta, name = sheets.load_sprite_sheet()
                        layer_sheets[event.key] = image
                        layer_meta[event.key] = meta

                    # once layer is loaded, toggle by tapping number key
                    if layer_display != event.key:
                        layer_display = event.key
                    else:
                        layer_display = 0

                elif not (event.key == pygame.K_LSHIFT or event.key == pygame.K_RSHIFT):
                    # save sheet on any uncaught keystroke
                    sprites.screen.blit(sprite_sheet, (0, 0))
                    new_filename = sheets.save_sprite_sheet(sprite_sheet, sprite_meta, save_filename)
                    status_shown = True
                    if new_filename is not None:
                        save_filename = new_filename
                        
            if event.type == pygame.MOUSEBUTTONDOWN:
                # handle clicking on palette bar
                status_shown = sprites.clear_status_text()
                sprites.screen.blit(work, (0, 32))
                colour_choice = mouse_rect.collidedict(palette)
                focus_selection = mouse_rect.collidedict(editors)
                if colour_choice:
                    draw_colour = colour_choice[1]
                    status_shown = sprites.draw_status_text('Current colour', draw_colour)
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
                    status_shown = sprites.draw_status_text(f'ENTER to save or ESCAPE to reset', draw_colour)
    pygame.quit()
