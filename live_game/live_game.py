#!/usr/bin/env python3

import click
import curses
import curses.ascii
import sys

from game.game import Game

STDSCR = None

INIT_BOX = None
INIT_BOX_TITLE = "Initiative Tracker"
INIT_BOX_WIDTH = 0
MENU_BOX = None
MENU_BOX_TITLE = "Menu"
MENU_BOX_HEIGHT = 0
MENU_BOX_WIDTH = 0
STATUS_BOX = None
STATUS_BOX_TITLE = "Status"
STATUS_BOX_WIDTH = 0
LOG_BOX = None
LOG_BOX_TITLE = "Log"
LOG_BOX_WIDTH = 0
HELP_PANEL = None
INPUT_PANEL = None

BOX_BUFFER_SPACES = 4
BOX_HEIGHT_PADDING = 5
BOX_PADDING = 2
GAME_STATE = None
HEIGHT = 0
MAX_BUFFER_LEN = 128
WIDTH = 0
YAML_DIR = 'yamls'

COMMANDS = {
    'Add Character': lambda: add_character(),
    'Remove Character': lambda: remove_character(),
    'Set Initiative': lambda: set_initiative(),
    'Cycle Initiative': lambda: handle_next(),
    'Defer Initiative': lambda: defer_initiative(),
    'Sort Initiative': lambda: sort_init_list(),
    'Edit Status': lambda: edit_status(),
    'Quit': lambda: sys.exit(0),
}

HELP_TEXT = {
    'Nav L Cancel': 'Hit ` or <- to Cancel',
    'Cancel': 'Hit ` to Cancel',
}

UP_DOWN_KEYS = [
    'KEY_UP',
    'KEY_DOWN',
]

RIGHT_LEFT_KEYS = [
    'KEY_RIGHT',
    'KEY_LEFT',
]

ENTER_KEY = '\n'
ESC_KEY = '`'
FINAL_KEYS = [ENTER_KEY, ESC_KEY]
INIT_CURSOR_INDEX = 0
STATUS_CURSOR_INDEX = 0


def add_character():
    name = get_input()
    if len(name) < 1:
        return "no input"

    GAME_STATE.add_character(name)
    return name


def clear_help_text():
    HELP_PANEL.clear()
    HELP_PANEL.addstr(0, BOX_PADDING, '')
    HELP_PANEL.refresh()


def clear_refresh_all():
    STDSCR.clear()
    STDSCR.refresh()
    INPUT_PANEL.clear()
    INPUT_PANEL.refresh()
    HELP_PANEL.clear()
    HELP_PANEL.refresh()
    MENU_BOX.clear()
    MENU_BOX.refresh()
    INIT_BOX.clear()
    INIT_BOX.refresh()
    STATUS_BOX.clear()
    STATUS_BOX.refresh()
    LOG_BOX.clear()
    LOG_BOX.refresh()


def defer_initiative():
    init_and_name_list = GAME_STATE.initiative_list[0].split()
    name = ' '.join(init_and_name_list[1:])
    GAME_STATE.defer_initiative()
    return name


def display_help_text(text):
    HELP_PANEL.clear()
    if len(text) > MAX_BUFFER_LEN:
        text = text[:MAX_BUFFER_LEN]

    HELP_PANEL.addstr(0, BOX_PADDING, text, curses.A_STANDOUT)
    HELP_PANEL.refresh()


def edit_status():
    display_help_text(HELP_TEXT['Nav L Cancel'])

    key = ''
    while key not in FINAL_KEYS + RIGHT_LEFT_KEYS:
        key = navigate_status()

    if key == ESC_KEY or key == RIGHT_LEFT_KEYS[1]:
        clear_help_text()
        return ESC_KEY

    choice = GAME_STATE.pcs_status_list[STATUS_CURSOR_INDEX]
    choice_list = choice.split()
    choice_part = choice_list[0]

    if choice_part == 'Name:':
        pass
    elif choice_part in Game.hearts:
        # get HP update
        change = get_input()
        if not is_integer(change) and not is_float(change):
            clear_help_text()
            return 'non-integer input'

        change_type = None
        change_str = change
        if change[0] == '-' or change[0] == '+':
            change_type = change[0]
            change = change[1:]
        elif is_float(change):
            change_type = 'set max'
        name = get_status_owner()

        GAME_STATE.update_hp(name, change, change_type)

        clear_help_text()
        return ' '.join([name, change_str])

    elif choice_part == Game.bang:
        # add condition
        pass
    else:
        # remove condition
        pass

    clear_help_text()
    return ''


def get_input():
    display_help_text(HELP_TEXT['Cancel'])

    INPUT_PANEL.move(1, 1)
    key = INPUT_PANEL.getkey()
    ret = ''
    while key not in FINAL_KEYS and len(ret) < MAX_BUFFER_LEN:
        if key == 'KEY_BACKSPACE':
            ret = ret[:-1]
        else:
            if len(key) == 1:
                ret += key
        INPUT_PANEL.addstr(1, 1, ret)
        key = INPUT_PANEL.getkey()
        INPUT_PANEL.clear()
        render_input_panel()
    clear_help_text()
    if key == ESC_KEY:
        return ''
    return ret


def get_status_owner():
    tmp_index = STATUS_CURSOR_INDEX
    part = GAME_STATE.pcs_status_list[tmp_index].split()[0]
    while part != 'Name:':
        tmp_index -= 1
        part = GAME_STATE.pcs_status_list[tmp_index].split()[0]
    line = GAME_STATE.pcs_status_list[tmp_index]
    return ' '.join(line.split()[1:])


def handle_next():
    GAME_STATE.next_initiative()
    INIT_BOX.clear()
    return ' '.join(GAME_STATE.initiative_list[0].split()[1:])


def is_float(s):
    try:
        if not any([c == '.' for c in s]):
            return False
        float(s)
        return True
    except ValueError:
        return False


def is_integer(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


def max_len_append(new_item, the_list, max_len):
    ln = len(the_list)
    diff = ln - max_len
    if diff >= 0:
        the_list = the_list[diff+1:]
    the_list.append(new_item)
    return the_list


def navigate_initiative():
    global INIT_BOX
    global INIT_CURSOR_INDEX
    INIT_BOX.clear()

    key = ''

    while key not in FINAL_KEYS + RIGHT_LEFT_KEYS:
        render_box_highlight_text(INIT_BOX, HEIGHT, INIT_BOX_WIDTH,
                                  INIT_BOX_TITLE, GAME_STATE.initiative_list,
                                  INIT_CURSOR_INDEX)
        INIT_BOX.move(BOX_BUFFER_SPACES + INIT_CURSOR_INDEX, BOX_PADDING)
        key = INIT_BOX.getkey()

        if key in UP_DOWN_KEYS:
            INIT_CURSOR_INDEX = navkey_to_index(key,
                                                GAME_STATE.initiative_list,
                                                INIT_CURSOR_INDEX)

    return key


def navigate_status():
    global STATUS_BOX
    global STATUS_CURSOR_INDEX
    STATUS_BOX.clear()

    key = ''

    while key not in FINAL_KEYS + RIGHT_LEFT_KEYS:
        render_box_highlight_text(STATUS_BOX, HEIGHT, STATUS_BOX_WIDTH,
                                  STATUS_BOX_TITLE, GAME_STATE.pcs_status_list,
                                  STATUS_CURSOR_INDEX)
        STATUS_BOX.move(BOX_BUFFER_SPACES + STATUS_CURSOR_INDEX, BOX_PADDING)
        key = STATUS_BOX.getkey()

        if key in UP_DOWN_KEYS:
            STATUS_CURSOR_INDEX = navkey_to_index(key,
                                                  GAME_STATE.pcs_status_list,
                                                  STATUS_CURSOR_INDEX)

    return key


def navkey_to_index(keystroke, menu_list, cursor_index):
    if keystroke == 'KEY_UP' and cursor_index <= 0:
        return len(menu_list)-1
    elif keystroke == 'KEY_DOWN' and cursor_index >= len(menu_list)-1:
        return 0
    elif keystroke == 'KEY_UP':
        return cursor_index - 1
    elif keystroke == 'KEY_DOWN':
        return cursor_index + 1
    else:
        return cursor_index


def remove_character():
    global INIT_CURSOR_INDEX
    display_help_text(HELP_TEXT['Nav L Cancel'])
    key = ''
    while key not in FINAL_KEYS + RIGHT_LEFT_KEYS[1:]:
        key = navigate_initiative()

    if key == ESC_KEY or key == RIGHT_LEFT_KEYS[1]:
        clear_help_text()
        return ESC_KEY

    init_and_name_list = GAME_STATE.initiative_list[INIT_CURSOR_INDEX].split()
    name = ' '.join(init_and_name_list[1:])

    GAME_STATE.remove_character(name)
    INIT_CURSOR_INDEX = 0
    clear_help_text()
    INIT_BOX.clear()
    return name


def render_box(box, height, width, title, strings):
    # box.clear()
    # box.refresh()
    box.box()
    box.addstr(1, BOX_PADDING, title)
    box.addstr(BOX_PADDING, 1, ''.join('-' for i in range(width-BOX_PADDING)))
    start = BOX_BUFFER_SPACES
    for string in strings:
        try:
            if len(string) >= width-BOX_BUFFER_SPACES:
                box.addstr(start,
                           BOX_PADDING, string[:width-BOX_BUFFER_SPACES])
            else:
                box.addstr(start, BOX_PADDING, string)
        except Exception:
            continue
        start += 1


def render_box_highlight_text(box, height, width, title, strings, index):
    box.box()
    box.addstr(1, BOX_PADDING, title)
    box.addstr(BOX_PADDING, 1, ''.join('-' for i in range(width-BOX_PADDING)))
    start = BOX_BUFFER_SPACES
    for i, string in enumerate(strings):
        if len(string) >= width-BOX_BUFFER_SPACES:
            string = string[:width-BOX_BUFFER_SPACES]
        if i == index:
            box.addstr(start, BOX_PADDING, string, curses.A_STANDOUT)
        else:
            box.addstr(start, BOX_PADDING, string)
        start += 1


def render_input_panel():
    INPUT_PANEL.box()


def set_initiative():
    display_help_text(HELP_TEXT['Nav L Cancel'])

    key = ''
    while key not in FINAL_KEYS + RIGHT_LEFT_KEYS:
        key = navigate_initiative()

    if key == ESC_KEY or key == RIGHT_LEFT_KEYS[1]:
        clear_help_text()
        return ESC_KEY

    choice = GAME_STATE.initiative_list[INIT_CURSOR_INDEX]
    items = get_input().split()
    if len(items) < 1:
        clear_help_text()
        return 'no input'
    first_item = items[0]
    if not first_item.isdigit():
        clear_help_text()
        return 'non-integer input'
    else:
        name = ' '.join(choice.split()[1:])
        GAME_STATE.set_initiative(name, first_item)

    clear_help_text()
    return f'{name} {first_item}'


def sort_init_list():
    GAME_STATE.sort_init_list()
    INIT_BOX.clear()
    return 'descending'


def main(pcs, yaml_dir):
    global STDSCR
    global INIT_BOX
    global INIT_BOX_WIDTH
    global MENU_BOX
    global MENU_BOX_HEIGHT
    global MENU_BOX_WIDTH
    global STATUS_BOX
    global STATUS_BOX_WIDTH
    global LOG_BOX
    global LOG_BOX_WIDTH
    global GAME_STATE
    global HEIGHT
    global HELP_PANEL
    global INPUT_PANEL
    global MAX_BUFFER_LEN
    global WIDTH

    kwargs = {}
    YAML_DIR = yaml_dir
    kwargs['pcs_yaml'] = '{}/{}'.format(YAML_DIR, pcs)

    GAME_STATE = Game(**kwargs)

    HEIGHT, WIDTH = STDSCR.getmaxyx()
    HEIGHT -= BOX_PADDING
    WIDTH -= BOX_PADDING
    MAX_BUFFER_LEN = WIDTH
    INIT_BOX_WIDTH = 40
    MENU_BOX_WIDTH = max([len(x) for x in COMMANDS.keys()]) + BOX_BUFFER_SPACES
    MENU_BOX_HEIGHT = len(COMMANDS.keys()) + BOX_HEIGHT_PADDING
    STATUS_BOX_WIDTH = 40
    LOG_BOX_WIDTH = (WIDTH // 3) - BOX_PADDING

    HELP_PANEL = curses.newwin(1, WIDTH, HEIGHT-2, 0)

    INPUT_PANEL = curses.newwin(3, WIDTH, HEIGHT-1, 0)
    INPUT_PANEL.immedok(True)
    INPUT_PANEL.keypad(True)

    MENU_BOX = curses.newwin(MENU_BOX_HEIGHT, MENU_BOX_WIDTH, 0, 0)
    MENU_BOX.immedok(True)
    MENU_BOX.keypad(True)

    INIT_BOX = curses.newwin(HEIGHT-BOX_PADDING, INIT_BOX_WIDTH, 0,
                             MENU_BOX_WIDTH+1)
    INIT_BOX.immedok(True)
    INIT_BOX.keypad(True)

    STATUS_BOX = curses.newwin(HEIGHT-BOX_PADDING, STATUS_BOX_WIDTH, 0,
                               MENU_BOX_WIDTH + INIT_BOX_WIDTH + 2)
    STATUS_BOX.immedok(True)
    STATUS_BOX.keypad(True)

    cmds_list = list(COMMANDS.keys())
    cursor_index = 0
    keystrokes_list = []
    key_list_max_len = HEIGHT-8
    LOG_BOX = curses.newwin(HEIGHT-BOX_PADDING, LOG_BOX_WIDTH, 0,
                            INIT_BOX_WIDTH +
                            MENU_BOX_WIDTH +
                            STATUS_BOX_WIDTH +
                            3)
    LOG_BOX.immedok(True)
    LOG_BOX.keypad(True)

    while True:
        STDSCR.refresh()
        h, y = STDSCR.getmaxyx()
        if curses.is_term_resized(h, y):
            HEIGHT, WIDTH = h, y
            HEIGHT -= BOX_PADDING
            WIDTH -= BOX_PADDING
            MAX_BUFFER_LEN = WIDTH

            INIT_BOX_WIDTH = 40 if WIDTH > 120 else (WIDTH // 3) - BOX_PADDING
            STATUS_BOX_WIDTH = 40 if WIDTH > 120 else (WIDTH // 3) - \
                BOX_PADDING
            LOG_BOX_WIDTH = (WIDTH // 3) - BOX_PADDING

            HELP_PANEL.resize(1, WIDTH)
            INPUT_PANEL.resize(3, WIDTH)
            INIT_BOX.resize(HEIGHT-BOX_PADDING, INIT_BOX_WIDTH)
            MENU_BOX.resize(MENU_BOX_HEIGHT, MENU_BOX_WIDTH)
            STATUS_BOX.resize(HEIGHT-BOX_PADDING, STATUS_BOX_WIDTH)
            LOG_BOX.resize(HEIGHT-BOX_PADDING, LOG_BOX_WIDTH)
            HELP_PANEL.resize(1, WIDTH)
            INPUT_PANEL.resize(3, WIDTH)

            MENU_BOX.mvwin(0, 0)
            INIT_BOX.mvwin(0, MENU_BOX_WIDTH+1)
            STATUS_BOX.mvwin(0, INIT_BOX_WIDTH +
                             MENU_BOX_WIDTH +
                             2)
            LOG_BOX.mvwin(0, INIT_BOX_WIDTH +
                          MENU_BOX_WIDTH +
                          STATUS_BOX_WIDTH +
                          3)
            HELP_PANEL.mvwin(HEIGHT-2, 0)
            INPUT_PANEL.mvwin(HEIGHT-1, 0)
            clear_refresh_all()

        render_box_highlight_text(MENU_BOX, HEIGHT, MENU_BOX_WIDTH,
                                  MENU_BOX_TITLE, cmds_list, cursor_index)
        render_box(INIT_BOX, HEIGHT, INIT_BOX_WIDTH, INIT_BOX_TITLE,
                   GAME_STATE.initiative_list)
        render_box(STATUS_BOX, HEIGHT, STATUS_BOX_WIDTH, STATUS_BOX_TITLE,
                   GAME_STATE.pcs_status_list)
        render_box(LOG_BOX, HEIGHT, LOG_BOX_WIDTH, LOG_BOX_TITLE,
                   keystrokes_list)
        render_input_panel()

        MENU_BOX.move(BOX_BUFFER_SPACES + cursor_index, BOX_PADDING)
        key = MENU_BOX.getkey()

        if key in UP_DOWN_KEYS:
            cursor_index = navkey_to_index(key, cmds_list, cursor_index)
        elif key == ENTER_KEY or RIGHT_LEFT_KEYS[0]:
            choice = cmds_list[cursor_index]
            extra = COMMANDS[choice]()
            if choice == 'Set Initiative' or choice == 'Edit Status':
                while extra != ESC_KEY:
                    keystrokes_list = max_len_append(' '.join([choice, extra]),
                                                     keystrokes_list,
                                                     key_list_max_len)
                    extra = COMMANDS[choice]()
            else:
                keystrokes_list = max_len_append(' '.join([choice, extra]),
                                                 keystrokes_list,
                                                 key_list_max_len)


@click.command()
@click.option('--pcs', type=click.Path(dir_okay=False, writable=True,
              readable=True), default='pcs.yaml',
              help='name of alternate PCs file')
@click.option('--yaml-dir', type=click.Path(exists=True, dir_okay=True,
              file_okay=False, writable=True, readable=True), default='yamls',
              help='path to alternate yaml dir')
def start(pcs, yaml_dir):
    global STDSCR

    try:
        STDSCR = curses.initscr()
        curses.start_color()
        curses.use_default_colors()
        curses.init_color(curses.COLOR_RED, 255, 0, 0)
        STDSCR.immedok(True)

        # The following options need to be reversed if they are enabled
        STDSCR.keypad(True)     # curses handles cursor & nav keys
        curses.noecho()   # turns off echoing of keys to screen
        curses.cbreak()   # react to keys instantly, don't wait for Enter

        main(pcs, yaml_dir)
    finally:
        # Terminate application
        curses.nocbreak()
        curses.echo()
        STDSCR.keypad(False)
        curses.endwin()


if __name__ == '__main__':
    start()
