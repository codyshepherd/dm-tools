#!/usr/bin/env python3

import click
import curses
import curses.ascii

from game.game import Game

STDSCR = None

BOX1 = None
BOX1_TITLE = "Initiative Tracker"
BOX1_WIDTH = 0
BOX2 = None
BOX2_TITLE = "Menu"
BOX2_WIDTH = 0
BOX3 = None
BOX3_TITLE = "Log"
BOX3_WIDTH = 0
HELP_PANEL = None
INPUT_PANEL = None

BOX_BUFFER_SPACES = 4
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
    'Sort Initiative': lambda: sort_init_list(),
}

HELP_TEXT = {
    'Cancel': 'Hit ` to Cancel',        
}

NAV_KEYS = [
    'KEY_UP',
    'KEY_DOWN',
    'KEY_RIGHT',
    'KEY_LEFT',
]

ENTER_KEY = '\n'
ESC_KEY = '`'
FINAL_KEYS = [ENTER_KEY, ESC_KEY]
INIT_CURSOR_INDEX = 0


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


def display_help_text(text):
    if len(text) > MAX_BUFFER_LEN:
        text = text[:MAX_BUFFER_LEN]

    HELP_PANEL.addstr(0, BOX_PADDING, text, curses.A_STANDOUT)
    HELP_PANEL.refresh()


def clear_help_text():
    HELP_PANEL.clear()
    HELP_PANEL.refresh()


def add_character():
    name = get_input()
    if len(name) < 1:
        return "no input"

    GAME_STATE.add_character(name)
    return name


def remove_character():
    global INIT_CURSOR_INDEX
    display_help_text(HELP_TEXT['Cancel'])
    key = navigate(BOX1, BOX1_WIDTH, BOX1_TITLE)

    if key == ESC_KEY:
        return ESC_KEY

    init_and_name_list = GAME_STATE.initiative_list[INIT_CURSOR_INDEX].split()
    name = ' '.join(init_and_name_list[1:])

    GAME_STATE.remove_character(name)
    INIT_CURSOR_INDEX = 0
    clear_help_text()
    return name


def max_len_append(new_item, the_list, max_len):
    ln = len(the_list)
    diff = ln - max_len
    if diff >= 0:
        the_list = the_list[diff+1:]
    the_list.append(new_item)
    return the_list


def handle_next():
    GAME_STATE.next_initiative()
    return ' '.join(GAME_STATE.initiative_list[0].split()[1:])


def sort_init_list():
    GAME_STATE.sort_init_list()
    return 'descending'


def navigate(box, box_width, box_title):
    global INIT_CURSOR_INDEX

    key = ''

    while key not in FINAL_KEYS:
        render_box_highlight_text(box, HEIGHT, box_width, box_title,
                                  GAME_STATE.initiative_list,
                                  INIT_CURSOR_INDEX)
        box.move(BOX_BUFFER_SPACES + INIT_CURSOR_INDEX, BOX_PADDING)
        key = box.getkey()

        if key in NAV_KEYS:
            INIT_CURSOR_INDEX = navkey_to_index(key,
                                                GAME_STATE.initiative_list,
                                                INIT_CURSOR_INDEX)

    return key


def set_initiative():
    display_help_text(HELP_TEXT['Cancel'])

    key = navigate(BOX1, BOX1_WIDTH, BOX1_TITLE)

    if key == ESC_KEY:
        return ESC_KEY

    choice = GAME_STATE.initiative_list[INIT_CURSOR_INDEX]
    items = get_input().split()
    if len(items) < 1:
        return 'no input'
    first_item = items[0]
    if not first_item.isdigit():
        return 'non-integer input'
    else:
        name = ' '.join(choice.split()[1:])
        GAME_STATE.set_initiative(name, first_item)

    clear_help_text()
    return f'{name} {first_item}'


def get_input():
    display_help_text(HELP_TEXT['Cancel'])

    INPUT_PANEL.move(1, 1)
    key = INPUT_PANEL.getkey()
    ret = ''
    while key not in FINAL_KEYS and len(ret) < MAX_BUFFER_LEN:
        if key == 'KEY_BACKSPACE':
            ret = ret[:-1]
        else:
            ret += key
        INPUT_PANEL.addstr(1, 1, ret)
        key = INPUT_PANEL.getkey()
        render_input_panel()
    INPUT_PANEL.refresh()
    if key == ESC_KEY:
        return ''
    return ret


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


def render_box(box, height, width, title, strings):
    box.clear()
    box.refresh()
    box.box()
    box.addstr(1, BOX_PADDING, title)
    box.addstr(BOX_PADDING, 1, ''.join('-' for i in range(width-BOX_PADDING)))
    start = BOX_BUFFER_SPACES
    for string in strings:
        if len(string) >= width-BOX_BUFFER_SPACES:
            box.addstr(start, BOX_PADDING, string[:width-BOX_BUFFER_SPACES])
        else:
            box.addstr(start, BOX_PADDING, string)
        start += 1


def render_input_panel():
    INPUT_PANEL.clear()
    INPUT_PANEL.box()
    INPUT_PANEL.refresh()


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


def main(pcs, yaml_dir):
    global STDSCR
    global BOX1
    global BOX1_WIDTH
    global BOX2
    global BOX2_WIDTH
    global BOX3
    global BOX3_WIDTH
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
    BOX1_WIDTH = (WIDTH // 3) - BOX_PADDING
    BOX2_WIDTH = (WIDTH // 3) - BOX_PADDING
    BOX2_WIDTH = (WIDTH // 3) - BOX_PADDING

    HELP_PANEL = curses.newwin(1, WIDTH, HEIGHT-2, 0)

    INPUT_PANEL = curses.newwin(3, WIDTH, HEIGHT-1, 0)
    INPUT_PANEL.keypad(True)

    BOX1 = curses.newwin(HEIGHT-BOX_PADDING, BOX1_WIDTH, 0, 0)
    BOX1.immedok(True)
    BOX1.keypad(True)

    cmds_list = list(COMMANDS.keys())
    cursor_index = 0
    BOX2 = curses.newwin(HEIGHT-BOX_PADDING, BOX2_WIDTH, 0, BOX1_WIDTH+1)
    BOX2.immedok(True)
    BOX2.keypad(True)

    keystrokes_list = []
    key_list_max_len = HEIGHT-8
    BOX3 = curses.newwin(HEIGHT-BOX_PADDING, BOX3_WIDTH, 0,
                         BOX1_WIDTH+BOX2_WIDTH+BOX_PADDING)
    BOX3.immedok(True)
    BOX3.keypad(True)

    while True:
        h, y = STDSCR.getmaxyx()
        if h != HEIGHT and y != WIDTH:
            HEIGHT, WIDTH = h, y
            HEIGHT -= BOX_PADDING
            WIDTH -= BOX_PADDING
            MAX_BUFFER_LEN = WIDTH
            BOX1_WIDTH = (WIDTH // 3) - BOX_PADDING
            BOX2_WIDTH = (WIDTH // 3) - BOX_PADDING
            BOX3_WIDTH = (WIDTH // 3) - BOX_PADDING

            HELP_PANEL.resize(1, WIDTH)
            INPUT_PANEL.resize(3, WIDTH)
            BOX1.resize(HEIGHT-BOX_PADDING, BOX1_WIDTH)
            BOX2.resize(HEIGHT-BOX_PADDING, BOX2_WIDTH)
            BOX3.resize(HEIGHT-BOX_PADDING, BOX3_WIDTH)
            HELP_PANEL.resize(1, WIDTH)
            INPUT_PANEL.resize(3, WIDTH)
            BOX1.mvwin(0, 0)
            BOX2.mvwin(0, BOX1_WIDTH+1)
            BOX3.mvwin(0, BOX1_WIDTH+BOX2_WIDTH+BOX_PADDING)
            HELP_PANEL.mvwin(HEIGHT-2, 0)
            INPUT_PANEL.mvwin(HEIGHT-1, 0)

        render_box(BOX1, HEIGHT, BOX1_WIDTH, BOX1_TITLE,
                   GAME_STATE.initiative_list)
        render_box_highlight_text(BOX2, HEIGHT, BOX2_WIDTH, BOX2_TITLE,
                                  cmds_list, cursor_index)
        render_box(BOX3, HEIGHT, BOX3_WIDTH, BOX3_TITLE,
                   keystrokes_list)
        HELP_PANEL.clear()
        HELP_PANEL.refresh()
        render_input_panel()

        BOX2.move(BOX_BUFFER_SPACES + cursor_index, BOX_PADDING)
        key = BOX2.getkey()

        if key in NAV_KEYS:
            cursor_index = navkey_to_index(key, cmds_list, cursor_index)
        elif key == ENTER_KEY:
            choice = cmds_list[cursor_index]
            extra = COMMANDS[choice]()
            if choice == 'Set Initiative':
                while extra != ESC_KEY:
                    keystrokes_list = max_len_append(' '.join([choice, extra]),
                                                     keystrokes_list,
                                                     key_list_max_len)
                    extra = COMMANDS[choice]()
            else:
                keystrokes_list = max_len_append(' '.join([choice, extra]),
                                                 keystrokes_list,
                                                 key_list_max_len)


if __name__ == '__main__':
    start()
