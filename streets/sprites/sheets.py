import pygame
import pickle
import glob
import studio


def load_sprite_sheet():
    sheet_list = glob.glob('*.png')

    if len(sheet_list) == 0:
        # create new sheet on empty directory
        new_sheet = pygame.Surface(studio.SHEET_SIZE)
        new_sheet.fill(studio.COLOUR_KEY)
        return new_sheet, {}, 'new_sheet'

    # list sprite sheets on screen
    studio.draw_status_text('Select sprite sheet file', studio.STATUS_GREEN)

    sheet_set = {}
    x, y = (2, 34)
    for sheet_name in sheet_list:
        sheet_text = studio.font.render(sheet_name, True, studio.TEXT_COLOUR)
        sheet_rect = sheet_text.get_rect()
        sheet_rect.x, sheet_rect.y = (x, y)
        studio.screen.blit(sheet_text, (x, y))
        sheet_set[tuple(sheet_rect)] = sheet_name
        y += 24
        if y + studio.font.get_height() > studio.screen.get_height():
            y = 34
            x += studio.screen.get_width()//8

    # choose template sheet
    loading = True
    while loading:
        studio.clock.tick(60)
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
                    studio.screen.fill(studio.SCREEN_COLOUR)
                    return load_sheet, load_meta, png_name[:-4]
    # we should never see this
    return None, None, None


def save_sprite_sheet(sheet, meta, filename):
    # prompt to save work on quit or key-down
    filename = studio.get_text_input('Save file name: ', filename)
    if filename is not None:
        pygame.image.save(sheet, filename+'.png')
        file = open(filename+'.meta', 'wb')
        pickle.dump(meta, file)
        studio.draw_status_text(f'{filename} saved', studio.STATUS_GREEN)
    else:
        studio.draw_status_text('Save Canceled', studio.STATUS_YELLOW)
    return filename


def search_sprite(sheet, meta, tag):
    # draw the sheet
    searching = True
    selection = None
    while searching:
        studio.screen.blit(sheet, (0, 0))

        if meta and tag:
            # standard tinted overlay
            overlay = pygame.Surface(studio.SHEET_SIZE)
            overlay = overlay.convert_alpha()
            overlay.set_alpha(127)
            overlay.set_colorkey(studio.COLOUR_KEY)
            overlay.fill(studio.SCREEN_COLOUR)

            tag_list = list(meta.values())
            rect_list = list(meta.keys())
            for i in range(len(tag_list)):
                if tag in tag_list[i]:
                    pygame.draw.rect(overlay, studio.COLOUR_KEY, rect_list[i])
            studio.screen.blit(overlay, (0, 0))
        pygame.display.flip()

        selecting = True
        while selecting:
            studio.clock.tick(60)
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
                        tag = studio.get_text_input('Enter tag to search: ', tag)
                        selecting = False
                if selecting_event.type == pygame.MOUSEBUTTONDOWN:
                    select_x, select_y = pygame.mouse.get_pos()
                    select_x -= select_x % studio.SPRITE_SIZE[0]
                    select_y -= select_y % studio.SPRITE_SIZE[1]
                    searching = False
                    selecting = False
                    selection = pygame.Rect((select_x, select_y), studio.SPRITE_SIZE)
    return selection


if __name__ == '__main__':
    pygame.display.set_caption('Sprite Sheet Viewer')

    sprite_sheet, sprite_meta, save_filename = load_sprite_sheet()
    pygame.display.set_caption(save_filename)

    waiting = True
    while waiting:
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                waiting = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                studio.screen.blit(sprite_sheet, (0, 0))
            if event.type == pygame.KEYDOWN:
                studio.screen.blit(sprite_sheet, (0, 0))
                if event.key == pygame.K_BACKQUOTE:
                    search = studio.get_text_input('Enter tag to search ', None)
                    if search is not None:
                        result_rect = search_sprite(sprite_sheet, sprite_meta, search)
                        studio.draw_status_text(f'Selection: {tuple(result_rect)}')
                else:
                    new_filename = save_sprite_sheet(sprite_sheet, sprite_meta, save_filename)
                    if new_filename is not None:
                        save_sprite_sheet(new_filename)
                        waiting = False
    pygame.quit()
