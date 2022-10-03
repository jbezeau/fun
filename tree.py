import pygame

RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
GREY = (128, 128, 128)
BLACK = (0, 0, 0)
STATUS_GREEN = (64, 128, 64)
STATUS_RED = (128, 64, 64)

LV1_COLORS = [RED]
LV2_COLORS = [RED, GREEN]
LV3_COLORS = [RED, GREEN, BLUE]

POSITION_RECT = 0
POSITION_NODE = 1


# fun with data classes
class TreeSeed:
    def __init__(self, new_color):
        self.color = new_color
        self.branches = {}


# list of tree nodes
completed_trees = []

pygame.init()
screen = pygame.display.set_mode((960, 960), pygame.SCALED)
pygame.display.set_caption("tree()")
pygame.mouse.set_visible(True)

background = pygame.Surface(screen.get_size())
background = background.convert()
background.fill(BLACK)

text_surface = pygame.Surface((screen.get_width(), 28))
text_surface = text_surface.convert()
text_surface.fill(STATUS_GREEN)


def init_level():
    if pygame.font:
        large_font = pygame.font.Font(None, 96)
        end_text = f'LEVEL {level}'
        end_out = large_font.render(end_text, True, STATUS_GREEN)
        end_rect = end_out.get_rect(centerx=screen.get_width() // 2, centery=screen.get_height() // 2)
        background.blit(end_out, end_rect)

        small_font = pygame.font.Font(None, 24)
        score_text = f'{level} seed colors, click to continue'
        score_out = small_font.render(score_text, True, GREY)
        score_rect = score_out.get_rect(centerx=screen.get_width() // 2, centery=3 * (screen.get_height() // 4))
        background.blit(score_out, score_rect)
        screen.blit(background, (0, 0))
        pygame.display.flip()

        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    waiting = False
                if event.type == pygame.QUIT:
                    pygame.quit()
    match level:
        case 1:
            pygame.display.set_caption("tree(1)")
            return LV1_COLORS
        case 2:
            pygame.display.set_caption("tree(2)")
            return LV2_COLORS
        case 3:
            pygame.display.set_caption("tree(3)")
            return LV3_COLORS


def place_seed(pos, color, parent_pos, positions):
    new_seed = TreeSeed(color)
    positions[tuple(pos)] = new_seed
    if parent_pos is not None:
        # build tree
        parent_node = positions[tuple(parent_pos)]
        idx = len(parent_node.branches)
        parent_node.branches[idx] = new_seed

        # draw line
        line_start = (pos.left+5, pos.top+5)
        line_end = (parent_pos.left+5, parent_pos.top+5)
        pygame.draw.line(background, GREY, line_start, line_end)
    pygame.draw.rect(background, new_seed.color, pos)


def cycle_color(seed_node, color):
    next_idx = (seed_colors.index(color)+1) % len(seed_colors)
    next_color = seed_colors[next_idx]
    seed_node.color = next_color
    return next_color


def draw_cycle_color(seed_rect, next_color):
    pygame.draw.rect(background, next_color, seed_rect)


def edit_loop():
    clock = pygame.time.Clock()
    color = RED
    last_rect = None

    seed_positions = {}

    background.fill(BLACK)
    draw_status(len(seed_positions), node_limit)

    loop = True
    while loop:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 3 and len(seed_positions) > 0:
                    # return the root node of the tree
                    root_key = next(iter(seed_positions))
                    return seed_positions[root_key]

                # make a little square where the player clicks
                click_pos = pygame.mouse.get_pos()
                click_x = click_pos[0]-4
                click_y = click_pos[1]-4
                click_rect = pygame.Rect((click_x, click_y), (9, 9))
                click_seed = click_rect.collidedict(seed_positions)

                # see if the user hit a previous seed
                if click_seed is not None:
                    seed_clicked = pygame.Rect(click_seed[0])
                else:
                    seed_clicked = None

                if seed_clicked is None:
                    # if the click landed on nothing, place a new seed and connect it
                    if node_limit > len(seed_positions):
                        place_seed(click_rect, color, last_rect, seed_positions)
                        last_rect = click_rect
                        draw_status(len(seed_positions), node_limit)
                    else:
                        root_key = next(iter(seed_positions))
                        return seed_positions[root_key]
                elif seed_clicked == last_rect:
                    # clicks after first cycle the seed color
                    color = cycle_color(seed_positions[tuple(seed_clicked)], color)
                    draw_cycle_color(seed_clicked, color)
                else:
                    # if the click landed on a seed, make that current seed
                    last_rect = seed_clicked
            if event.type == pygame.QUIT:
                pygame.quit()
            screen.blit(background, (0, 0))
            screen.blit(text_surface, (0, 0))
        pygame.display.flip()

    # return the root node of the tree
    root_key = next(iter(seed_positions))
    return seed_positions[root_key]


def check_tree():
    # new tree can't contain any previous tree
    # TODO find some super-optimized graph library to do all this
    if len(completed_trees) == 0:
        return True
    for previous_tree in completed_trees:
        if match_root(root_node, previous_tree):
            return False
    return True


def match_root(seed_node, previous_root):
    # match every node of the tree against the root of previous tree
    if match_nodes(seed_node, previous_root):
        return True
    for leaf_key in seed_node.branches:
        if match_root(seed_node.branches[leaf_key], previous_root):
            return True
    return False


def match_nodes(seed_node, match_node):
    # match upward nodes of the tree against upward nodes of the previous tree
    remaining = match_node.branches.copy()
    if seed_node.color == match_node.color:
        for leaf_id, leaf_node in seed_node.branches.items():
            for match_leaf_id, match_leaf in match_node.branches.items():
                if match_nodes(leaf_node, match_leaf):
                    # take this branch out of the running for later iterations
                    # if seed has more branches than match we may have no match on some iterations
                    if remaining.get(match_leaf_id) is not None:
                        remaining.pop(match_leaf_id)
        if len(remaining) == 0:
            return True
    return False


def draw_status(seeds, limit):
    if pygame.font:
        small_font = pygame.font.Font(None, 24)
        status = f'Level {level}    Seeds {seeds}/{limit}    Completed Trees {len(completed_trees)}'
        text_output = small_font.render(status, True, (16, 16, 16))
        text_rect = text_output.get_rect(left=2, top=2)
        text_surface.fill(STATUS_GREEN)
        text_surface.blit(text_output, text_rect)


def level_complete():
    trees = len(completed_trees)
    match level:
        case 1:
            if 1 == trees:
                return True
        case 2:
            if 3 == trees:
                return True
    # the joke is that it's impossible to beat level 3
    return False


def level_score():
    print(f'Level {level} Score {len(completed_trees)}')


def final_score():
    if pygame.font:
        large_font = pygame.font.Font(None, 96)
        end_text = 'THE FOREST HAS DIED'
        end_out = large_font.render(end_text, True, STATUS_RED)
        end_rect = end_out.get_rect(centerx=screen.get_width() // 2, centery=screen.get_height() // 2)
        background.blit(end_out, end_rect)

        small_font = pygame.font.Font(None, 24)
        score_text = f'Final Score {total_score}'
        score_out = small_font.render(score_text, True, GREY)
        score_rect = score_out.get_rect(centerx=screen.get_width() // 2, centery=3 * (screen.get_height() // 4))
        background.blit(score_out, score_rect)
        screen.blit(background, (0, 0))
        pygame.display.flip()

        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    waiting = False
    print(score_text)


if __name__ == '__main__':
    level = 1
    node_limit = 1
    total_score = 0
    completed_trees = []
    playing = True

    seed_colors = init_level()
    while playing:
        root_node = edit_loop()
        playing = check_tree()
        background.fill(BLACK)
        if playing:
            node_limit += 1
            total_score += 1
            completed_trees.append(root_node)
        if level_complete():
            level_score()
            completed_trees = []
            node_limit = 1
            level += 1
            seed_colors = init_level()
        screen.blit(background, (0, 0))
        screen.blit(text_surface, (0, 0))
        pygame.display.flip()

    final_score()
    pygame.quit()
