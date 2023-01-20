import pygame
import streets.sprite.colours as co
import streets.characters.characters as ch


# environmental colours
CONCRETE = (128, 128, 128)


class Obstacle(pygame.sprite.Sprite):
    def __init__(self, pos, size, colour=CONCRETE):
        super(Obstacle, self).__init__()
        self.image = pygame.Surface(size)
        self.image.fill(co.GRAY3)
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = pos

    def collide(self, collision_obj, count):
        # vertical displacement
        contact_list = get_contact_pos(collision_obj.rect, self.rect)
        if contact_list.count(ch.CONTACT_CENTER) > 0 and contact_list.count(ch.CONTACT_LOW) > 0:
            new_y = self.rect.y - collision_obj.rect.height + ch.STAIR_HEIGHT
            if count > 1:
                # position on highest obstacle if there's competition
                collision_obj.rect.y = min(new_y, collision_obj.rect.y)
            else:
                collision_obj.rect.y = new_y
            if collision_obj.vel_y > 0:
                collision_obj.vel_y = 0

        # horizontal displacement
        if contact_list.count(ch.CONTACT_HIGH) or contact_list.count(ch.CONTACT_WALL):
            collision_obj.vel_x = 0
            if contact_list.count(ch.CONTACT_RIGHT):
                collision_obj.rect.x = self.rect.x - collision_obj.rect.width
            elif contact_list.count(ch.CONTACT_LEFT):
                collision_obj.rect.x = self.rect.x + self.rect.width

        return contact_list


def get_contact_pos(char_rect, obj_rect):
    # depth param indicates how much sprite overlap we're looking for
    # return 4 values, all must be greater than 0 if there is a collision
    # value between 0 and character dimension represents degree to which object is imposing from
    # that side of the character's hit box

    top_contact = (obj_rect.bottom - char_rect.top)
    left_contact = (obj_rect.right - char_rect.left)
    right_contact = (char_rect.right - obj_rect.left)
    bottom_contact = (char_rect.bottom - obj_rect.top)

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
