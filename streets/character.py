import glob
import pickle
import pygame
from pygame import image
from sprite import sprites


CHARACTER_SIZE = (64, 128)


def load_animations():
    sheet_list = glob.glob('sprite/*.png')
    animation_set = {}
    for filename in sheet_list:
        sheet_image = image.load(filename)
        metaname = filename[:-3]+'meta'
        pickle_file = open(metaname, 'rb')
        sheet_meta = pickle.load(pickle_file)
        pickle_file.close()

        sheet_animations = {}
        tag_list = list(sheet_meta.values())
        pos_list = list(sheet_meta.keys())
        for index in range(len(tag_list)):
            sprite_series = sheet_animations.get(tag_list[index])
            if not sprite_series:
                sprite_series = []
                sheet_animations[tag_list[index]] = sprite_series
            lil_pic = pygame.Surface(sprites.SPRITE_SIZE)
            lil_pic.blit(sheet_image, (0, 0), pos_list[index])
            sprite = pygame.transform.scale(lil_pic, CHARACTER_SIZE)
            sprite_series.append(sprite)
        animation_set[filename[:-4]] = sheet_animations
    return animation_set


animations = load_animations()


if __name__ == '__main__':
    print(animations)
