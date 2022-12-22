import pygame
import streets.sprite.colours as co
import streets.characters.characters as ch


class Obstacle(pygame.sprite.Sprite):
    def __init__(self, pos, size):
        super(Obstacle, self).__init__()
        self.image = pygame.Surface(size)
        self.image.fill(co.GRAY3)
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = pos

    def collide(self, character, count):
        # check contact with obstacles in the environment
        contact_list = get_contact_pos(character.rect, self.rect)
        if contact_list.count(ch.CONTACT_CENTER) > 0 and contact_list.count(ch.CONTACT_LOW) > 0:
            new_y = self.rect.y - character.rect.height + ch.STAIR_HEIGHT
            if count > 1:
                # stand on highest obstacle if there's a transition
                character.rect.y = min(new_y, character.rect.y)
            else:
                character.rect.y = new_y
            if character.vel_y > 0:
                character.vel_y = 0
            if character.check('jump'):
                if character.vel_x > 0:
                    character.set_animation('right_walk')
                else:
                    character.set_animation('left_walk')
            if character.check('fall'):
                if character.vel_x > 0:
                    character.set_animation('right_squat')
                else:
                    character.set_animation('left_squat')
                character.vel_x = 0
        if contact_list.count(ch.CONTACT_HIGH) or contact_list.count(ch.CONTACT_WALL):
            character.vel_x = 0
            if contact_list.count(ch.CONTACT_RIGHT):
                character.rect.x = self.rect.x - character.rect.width
            elif contact_list.count(ch.CONTACT_LEFT):
                character.rect.x = self.rect.x + self.rect.width
            if character.check('left'):
                character.set_animation('left_stand')
            else:
                character.set_animation('right_stand')
        return contact_list


def get_contact_pos(char_rect, obj_rect):
    # depth param indicates how much sprite overlap we're looking for
    # return 4 values, all must be greater than 0 if there is a collision
    # value between 0 and character dimension represents degree to which object is imposing from
    # that side of the character's hit box

    top_contact = (obj_rect.y + obj_rect.height - char_rect.y)
    left_contact = (obj_rect.x + obj_rect.width - char_rect.x)
    right_contact = (char_rect.x + char_rect.width - obj_rect.x)
    bottom_contact = (char_rect.y + char_rect.height - obj_rect.y)

    contact = []
    if char_rect.height // 3 > bottom_contact:
        contact.append(ch.CONTACT_LOW)
    elif 2 * char_rect.height // 3 > bottom_contact:
        contact.append(ch.CONTACT_HIGH)
    elif char_rect.height // 3 > top_contact:
        contact.append(ch.CONTACT_HEAD)
    else:
        contact.append(ch.CONTACT_WALL)

    if char_rect.width // 3 > left_contact:
        contact.append(ch.CONTACT_LEFT)
    elif char_rect.width // 3 > right_contact:
        contact.append(ch.CONTACT_RIGHT)
    elif right_contact > char_rect.width // 3 and left_contact > char_rect.width // 3:
        contact.append(ch.CONTACT_CENTER)
    return contact
