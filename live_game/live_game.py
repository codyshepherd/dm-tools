#!/usr/bin/env python3

import click
import curses

from game.game import Game

YAML_DIR = 'yamls'
MAX_BUFFER_LEN = 128
GAME_STATE = None

NAV_KEYS = [
    'KEY_UP',
    'KEY_DOWN',
    'KEY_RIGHT',
    'KEY_LEFT',
]

COMMANDS = {
    'Set Initiative': lambda x: set_initiative(x),
    'Cycle Initiative': lambda x: handle_next(x),
    'Sort Initiative': lambda x: sort_init_list(x),
}


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
    diff = max_len - ln
    if diff <= 0:
        the_list = the_list[diff+1:]
    return the_list.append(new_item)


def handle_next(screen):
    GAME_STATE.next_initiative()
    return 'next'


def sort_init_list(screen):
    GAME_STATE.sort_init_list()
    return 'descending'


def set_initiative(window):
    argslist = get_input(window, 1, 1).split()

    if len(argslist) < 2:
        return

    name_exp = argslist[0]
    init_val = argslist[1]
    GAME_STATE.set_initiative(name_exp, init_val)
    return ' '.join(argslist)


def get_input(screen, y, x):
    screen.move(1, 1)
    c = screen.getkey()
    ret = ''
    while c != '\n' and len(ret) < MAX_BUFFER_LEN:
        if c == 'KEY_BACKSPACE':
            ret = ret[:-1]
        else:
            ret += c
        screen.addstr(y, x, ret)
        c = screen.getkey()
        render_input_panel(screen)
    return ret


def render_box_highlight_text(box, height, width, title, strings, index):
    box.clear()
    box.box()
    box.addstr(1, 2, title)
    box.addstr(2, 1, ''.join('-' for i in range(width-2)))
    start = 4
    for i, string in enumerate(strings):
        if i == index:
            box.addstr(start, 2, string, curses.A_STANDOUT)
        else:
            box.addstr(start, 2, string)
        start += 1


def render_box(box, height, width, title, strings):
    box.clear()
    box.box()
    box.addstr(1, 2, title)
    box.addstr(2, 1, ''.join('-' for i in range(width-2)))
    start = 4
    for string in strings:
        box.addstr(start, 2, string)
        start += 1


def render_input_panel(panel):
    panel.clear()
    panel.box()


def main(stdscr, pcs, yaml_dir):
    kwargs = {}
    YAML_DIR = yaml_dir
    kwargs['pcs_yaml'] = '{}/{}'.format(YAML_DIR, pcs)

    global GAME_STATE
    GAME_STATE = Game(**kwargs)

    stdscr.border(0)
    height, width = stdscr.getmaxyx()
    height -= 2
    width -= 2
    global MAX_BUFFER_LEN
    MAX_BUFFER_LEN = width

    input_panel = curses.newwin(3, width, height-1, 0)
    input_panel.keypad(True)

    box1_width = 40
    box1 = curses.newwin(height-2, box1_width, 0, 0)
    box1.immedok(True)

    cmds_list = list(COMMANDS.keys())
    cursor_index = 0
    box2_width = 40
    box2 = curses.newwin(height-2, box1_width, 0, box1_width+1)
    box2.immedok(True)
    box2.keypad(True)

    keystrokes_list = []
    key_list_max_len = height-8
    box3_width = 40
    box3 = curses.newwin(height-2, box1_width, 0, (box1_width*2)+1)
    box3.immedok(True)

    def navkey_to_index(keystroke):
        if keystroke == 'KEY_UP' and cursor_index <= 0:
            return len(cmds_list)-1
        elif keystroke == 'KEY_DOWN' and cursor_index >= len(cmds_list)-1:
            return 0
        elif keystroke == 'KEY_UP':
            return cursor_index - 1
        elif keystroke == 'KEY_DOWN':
            return cursor_index + 1
        else:
            return cursor_index

    while True:
        stdscr.clear()

        render_input_panel(input_panel)
        render_box(box1, height, box1_width, "Initiative Tracker",
                   GAME_STATE.initiative_list)
        render_box_highlight_text(box2, height, box2_width, "Menu",
                                  cmds_list, cursor_index)
        render_box(box3, height, box3_width, "Debug Panel",
                   keystrokes_list)

        stdscr.refresh()

        box2.move(4 + cursor_index, 2)
        key = box2.getkey()

        if key in NAV_KEYS:
            max_len_append(key, keystrokes_list, key_list_max_len)
            cursor_index = navkey_to_index(key)
        elif key == '\n':
            choice = cmds_list[cursor_index]
            extra = COMMANDS[choice](input_panel)
            max_len_append(' '.join([choice, extra]), keystrokes_list,
                           key_list_max_len)


if __name__ == '__main__':
    start()
