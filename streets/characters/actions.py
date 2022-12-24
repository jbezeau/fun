import random
import pygame

# implement SR1 damage code
POWER = 0
LEVEL = 1
STAGING = 2

# wound levels
N = 0
L = 1
M = 3
S = 6
D = 10
WOUND_LEVELS = [N, L, M, S, D]

# character attributes
PWR = 'Power'
RES = 'Resist'
STUN = 'Stun'
WOUND = 'Wound'

# skill list
FIGHT = 'Fighting'
SHOOT = 'Shooting'


def idle(character, _):
    if character.is_animation_over():
        character.set_animation('right_stand', None, None)


# common actions for characters on the mean streets
def punch(attacker, target):
    if attacker.is_frame_num(2):
        # hit on frame 3
        damage = (attacker.stats[PWR], M, 1)
        dmg = fight(attacker, target, damage)
        _status(target, dmg, STUN)
    if attacker.is_animation_over():
        if attacker.check('left'):
            attacker.set_animation('left_stand', None, None)
        else:
            attacker.set_animation('right_stand', None, None)


def shoot(atk, tgt, dmg):
    attack_roll = _roll(atk.stats.get(SHOOT), 3)
    print(f'attack: {attack_roll}')
    if attack_roll > 0:
        # successful attack
        base_dmg = _stage(attack_roll, dmg)
        resist = -1 * _roll(tgt.stats[RES], dmg[POWER])
        wound = _stage(resist, base_dmg)
        return wound[LEVEL]
    else:
        print('miss')
    # zero damage
    return N


def fight(atk, tgt, dmg):
    if atk.rect.colliderect(tgt.rect):
        attack_roll = _roll(atk.stats.get(FIGHT), 3)
        defend_roll = _roll(tgt.stats.get(FIGHT), 3)
        print(f'attack: {attack_roll} vs {defend_roll}')
        if attack_roll > defend_roll:
            # successful attack
            base_dmg = _stage(attack_roll - defend_roll, dmg)
            resist = -1 * _roll(tgt.stats[RES], dmg[POWER])
            wound = _stage(resist, base_dmg)
            return wound[LEVEL]
        else:
            print('block')
    else:
        print('miss')
    # zero damage
    return N


def _status(char, lvl, dmg_type):
    current = char.stats.get(dmg_type)
    if current:
        lvl += current
    char.stats[dmg_type] = lvl
    print(f'damage: {dmg_type}={lvl}')


def _stage(hits, damage):
    # // rounds down instead of towards 0 which we have to fix
    steps = hits // damage[STAGING]
    lvl = WOUND_LEVELS.index(damage[LEVEL])

    if 0 > hits:
        # % also returns a positive number when we expect a negative
        if hits % damage[STAGING] > 0:
            steps += 1
        lvl = max(0, lvl + steps)
    else:
        lvl = min(len(WOUND_LEVELS)-1, lvl + steps)
    new_damage = (damage[POWER], WOUND_LEVELS[lvl], damage[STAGING])
    print(f'stage {damage} to {new_damage}')
    return new_damage


def _roll(dice, tn):
    if dice is None:
        return 0
    hits = 0
    for i in range(dice):
        r = random.randrange(6)
        if r == 6:
            r += random.randrange(6)
        if r >= tn:
            hits += 1
    return hits
