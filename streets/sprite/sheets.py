import pygame
import pickle
import glob
import sprites


NEW = 'New Sheet'


def load_sprite_sheet():
    sheet_list = glob.glob('*.png')
    sprites.screen.fill((0, 0, 0))

    # list sprite sheets on screen
    sprites.draw_status_text('Select sprite sheet file', sprites.STATUS_GREEN)

    sheet_set = {}
    new_file = {}
    x, y = (2, 34)
    for sheet_name in sheet_list:
        sheet_text = sprites.font.render(sheet_name, True, sprites.TEXT_COLOUR)
        sheet_rect = sheet_text.get_rect()
        sheet_rect.x, sheet_rect.y = (x, y)
        sprites.screen.blit(sheet_text, (x, y))
        sheet_set[tuple(sheet_rect)] = sheet_name
        y += 24
        if y + sprites.font.get_height() > sprites.screen.get_height():
            y = 34
            x += sprites.screen.get_width()//8
    new_text = sprites.font.render(NEW, True, sprites.TEXT_COLOUR)
    new_rect = new_text.get_rect()
    new_rect.x, new_rect.y = (x, y)
    sprites.screen.blit(new_text, (x, y))
    new_file[tuple(new_rect)] = NEW

    # choose template sheet
    loading = True
    while loading:
        sprites.clock.tick(60)
        pygame.display.flip()
        for load_sheet_event in pygame.event.get():
            if load_sheet_event.type == pygame.QUIT:
                pygame.quit()
            if load_sheet_event.type == pygame.MOUSEBUTTONDOWN:
                select_mouse_pos = pygame.Rect(pygame.mouse.get_pos(), (1, 1))
                select_sheet = select_mouse_pos.collidedict(sheet_set)
                if select_sheet is not None:
                    png_name = select_sheet[1]
                    bin_name = png_name[:-3] + 'meta'
                    load_sheet = pygame.image.load(png_name)
                    try:
                        file = open(bin_name, 'rb')
                        load_meta = pickle.load(file)
                        file.close()
                    except FileNotFoundError:
                        load_meta = {}
                    sprites.screen.fill(sprites.SCREEN_COLOUR)
                    return load_sheet, load_meta, png_name[:-4]
                elif select_mouse_pos.collidedict(new_file):
                    # create new sheet on empty directory
                    new_sheet = pygame.Surface(sprites.SHEET_SIZE)
                    new_sheet.fill(sprites.COLOUR_KEY)
                    return new_sheet, {}, 'new_sheet'

    # we should never see this
    return None, None, None


def save_sprite_sheet(sheet, meta, filename):
    # prompt to save work on quit or key-down
    filename = sprites.get_text_input('Save file name: ', filename)
    if filename is not None:
        pygame.image.save(sheet, filename+'.png')
        file = open(filename+'.meta', 'wb')
        pickle.dump(meta, file)
        sprites.draw_status_text(f'{filename} saved', sprites.STATUS_GREEN)
    else:
        sprites.draw_status_text('Save Canceled', sprites.STATUS_YELLOW)
    return filename


def search_sprite(sheet, meta, tag):
    # draw the sheet
    searching = True
    selection = None
    while searching:
        sprites.screen.blit(sheet, (0, 0))

        if meta and tag:
            # standard tinted overlay
            overlay = pygame.Surface(sprites.SHEET_SIZE)
            overlay = overlay.convert_alpha()
            overlay.set_alpha(127)
            overlay.set_colorkey(sprites.COLOUR_KEY)
            overlay.fill(sprites.SCREEN_COLOUR)

            tag_list = list(meta.values())
            rect_list = list(meta.keys())
            for i in range(len(tag_list)):
                if tag in tag_list[i]:
                    pygame.draw.rect(overlay, sprites.COLOUR_KEY, rect_list[i])
            sprites.screen.blit(overlay, (0, 0))
        pygame.display.flip()

        selecting = True
        while selecting:
            sprites.clock.tick(60)
            for selecting_event in pygame.event.get():
                if selecting_event.type == pygame.QUIT:
                    # pass exit to calling context
                    selecting = False
                    searching = False
                if selecting_event.type == pygame.KEYDOWN:
                    # escape is a more sensible way to back out of search
                    if selecting_event.key == pygame.K_ESCAPE:
                        selecting = False
                        searching = False
                    else:
                        # enter new search term and redraw
                        tag = sprites.get_text_input('Enter tag to search: ', tag)
                        selecting = False
                if selecting_event.type == pygame.MOUSEBUTTONDOWN:
                    select_x, select_y = pygame.mouse.get_pos()
                    select_x -= select_x % sprites.SPRITE_SIZE[0]
                    select_y -= select_y % sprites.SPRITE_SIZE[1]
                    searching = False
                    selecting = False
                    selection = pygame.Rect((select_x, select_y), sprites.SPRITE_SIZE)
    return selection


if __name__ == '__main__':
    pygame.display.set_caption('Sprite Sheet Viewer')

    sprite_sheet, sprite_meta, save_filename = load_sprite_sheet()
    sprites.screen.blit(sprite_sheet, (0, 0))
    layer_images = {}
    layer_display = None
    pygame.display.set_caption(save_filename)

    waiting = True
    while waiting:
        sprites.clock.tick(60)
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                waiting = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                # click should refresh the screen in case anything goes weird
                if layer_display is not None:
                    # unsafe check, we just crash if layer is depopulated somehow
                    sprites.screen.blit(layer_images[layer_display], (0, 0))
                else:
                    sprites.screen.blit(sprite_sheet, (0, 0))

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKQUOTE:
                    # search depends on tags which only lines up with sprite sheet
                    sprites.screen.blit(sprite_sheet, (0, 0))
                    search = sprites.get_text_input('Enter tag to search ', None)
                    if search is not None:
                        result_rect = search_sprite(sprite_sheet, sprite_meta, search)
                        sprites.draw_status_text(f'Selection: {tuple(result_rect)}')
                elif pygame.K_9 >= event.key >= pygame.K_0:
                    # load additional sprite sheet for comparison
                    if layer_images.get(event.key) is None:
                        # we can't load a new image to a layer that's already assigned
                        layer_image, layer_meta, layer_name = load_sprite_sheet()
                        layer_images[event.key] = layer_image

                    # stacking images using alpha makes things dark so let's just toggle
                    if layer_display != event.key:
                        layer_display = event.key
                        sprites.screen.blit(layer_images[event.key], (0, 0))
                    else:
                        layer_display = None
                        sprites.screen.blit(sprite_sheet, (0, 0))

                else:
                    # save
                    new_filename = save_sprite_sheet(sprite_sheet, sprite_meta, save_filename)
                    if new_filename is not None:
                        save_sprite_sheet(new_filename)
                        waiting = False
    pygame.quit()
