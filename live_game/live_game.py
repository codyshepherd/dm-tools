#!/usr/bin/env python3

import click
import curses

from game.game import Game

BOX1 = None
BOX1_TITLE = "Initiative Tracker"
BOX1_WIDTH = 0
BOX2 = None
BOX2_TITLE = "Menu"
BOX2_WIDTH = 0
BOX3 = None
BOX3_TITLE = "Log"
BOX3_WIDTH = 0
INPUT_PANEL = None

BOX_BUFFER_SPACES = 4
BOX_PADDING = 2
GAME_STATE = None
HEIGHT = 0
MAX_BUFFER_LEN = 128
WIDTH = 0
YAML_DIR = 'yamls'

COMMANDS = {
    'Set Initiative': lambda: set_initiative(),
    'Cycle Initiative': lambda: handle_next(),
    'Sort Initiative': lambda: sort_init_list(),
}

NAV_KEYS = [
    'KEY_UP',
    'KEY_DOWN',
    'KEY_RIGHT',
    'KEY_LEFT',
]

ESC_KEY = 'q'


@click.command()
@click.option('--pcs', type=click.Path(dir_okay=False, writable=True,
              readable=True), default='pcs.yaml',
              help='name of alternate PCs file')
@click.option('--yaml-dir', type=click.Path(exists=True, dir_okay=True,
              file_okay=False, writable=True, readable=True), default='yamls',
              help='path to alternate yaml dir')
def start(pcs, yaml_dir):

    try:
        stdscr = curses.initscr()
        curses.start_color()
        stdscr.immedok(True)

        # The following options need to be reversed if they are enabled
        stdscr.keypad(True)     # curses handles cursor & nav keys
        curses.noecho()   # turns off echoing of keys to screen
        curses.cbreak()   # react to keys instantly, don't wait for Enter

        main(stdscr, pcs, yaml_dir)
    finally:
        # Terminate application
        curses.nocbreak()
        curses.echo()
        stdscr.keypad(False)
        curses.endwin()


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


def set_initiative():
    cursor_index = 0
    key = ''

    final_keys = ['\n', ESC_KEY]
    while key not in final_keys:
        render_box_highlight_text(BOX1, HEIGHT, BOX1_WIDTH, BOX1_TITLE,
                                  GAME_STATE.initiative_list, cursor_index)
        BOX1.move(BOX_BUFFER_SPACES + cursor_index, BOX_PADDING)
        key = BOX1.getkey()

        if key in NAV_KEYS:
            cursor_index = navkey_to_index(key, GAME_STATE.initiative_list,
                                           cursor_index)

    if key == ESC_KEY:
        return 'ESC'

    choice = GAME_STATE.initiative_list[cursor_index]
    items = get_input().split()
    if len(items) < 1:
        return 'no input'
    first_item = items[0]
    if not first_item.isdigit():
        return 'non-integer input'
    else:
        name = ' '.join(choice.split()[1:])
        GAME_STATE.set_initiative(name, first_item)

    return f'{name} {first_item}'


def get_input():
    INPUT_PANEL.move(1, 1)
    c = INPUT_PANEL.getkey()
    ret = ''
    while c != '\n' and len(ret) < MAX_BUFFER_LEN:
        if c == 'KEY_BACKSPACE':
            ret = ret[:-1]
        else:
            ret += c
        INPUT_PANEL.addstr(1, 1, ret)
        c = INPUT_PANEL.getkey()
        render_input_panel()
    INPUT_PANEL.refresh()
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


def main(stdscr, pcs, yaml_dir):
    global BOX1
    global BOX1_WIDTH
    global BOX2
    global BOX2_WIDTH
    global BOX3
    global BOX3_WIDTH
    global GAME_STATE
    global HEIGHT
    global INPUT_PANEL
    global MAX_BUFFER_LEN
    global WIDTH

    kwargs = {}
    YAML_DIR = yaml_dir
    kwargs['pcs_yaml'] = '{}/{}'.format(YAML_DIR, pcs)

    GAME_STATE = Game(**kwargs)

    HEIGHT, WIDTH = stdscr.getmaxyx()
    HEIGHT -= BOX_PADDING
    WIDTH -= BOX_PADDING
    MAX_BUFFER_LEN = WIDTH
    BOX1_WIDTH = (WIDTH // 3) - BOX_PADDING
    BOX2_WIDTH = (WIDTH // 3) - BOX_PADDING
    BOX2_WIDTH = (WIDTH // 3) - BOX_PADDING

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
        # stdscr.clear()    # TODO: I'm a bit unsure where these calls should
        # stdscr.refresh()  # really go to reduce choppiness
        h, y = stdscr.getmaxyx()
        if h != HEIGHT and y != WIDTH:
            HEIGHT, WIDTH = h, y
            HEIGHT -= BOX_PADDING
            WIDTH -= BOX_PADDING
            MAX_BUFFER_LEN = WIDTH
            BOX1_WIDTH = (WIDTH // 3) - BOX_PADDING
            BOX2_WIDTH = (WIDTH // 3) - BOX_PADDING
            BOX3_WIDTH = (WIDTH // 3) - BOX_PADDING

            INPUT_PANEL.resize(3, WIDTH)
            BOX1.resize(HEIGHT-BOX_PADDING, BOX1_WIDTH)
            BOX2.resize(HEIGHT-BOX_PADDING, BOX2_WIDTH)
            BOX3.resize(HEIGHT-BOX_PADDING, BOX3_WIDTH)
            INPUT_PANEL.resize(3, WIDTH)
            BOX1.mvwin(0, 0)
            BOX2.mvwin(0, BOX1_WIDTH+1)
            BOX3.mvwin(0, BOX1_WIDTH+BOX2_WIDTH+BOX_PADDING)
            INPUT_PANEL.mvwin(HEIGHT-1, 0)

        render_box(BOX1, HEIGHT, BOX1_WIDTH, BOX1_TITLE,
                   GAME_STATE.initiative_list)
        render_box_highlight_text(BOX2, HEIGHT, BOX2_WIDTH, BOX2_TITLE,
                                  cmds_list, cursor_index)
        render_box(BOX3, HEIGHT, BOX3_WIDTH, BOX3_TITLE,
                   keystrokes_list)
        render_input_panel()

        BOX2.move(BOX_BUFFER_SPACES + cursor_index, BOX_PADDING)
        key = BOX2.getkey()

        if key in NAV_KEYS:
            cursor_index = navkey_to_index(key, cmds_list, cursor_index)
        elif key == '\n':
            choice = cmds_list[cursor_index]
            extra = COMMANDS[choice]()
            if extra != 'ESC':
                keystrokes_list = max_len_append(' '.join([choice, extra]),
                                                 keystrokes_list,
                                                 key_list_max_len)


if __name__ == '__main__':
    start()
