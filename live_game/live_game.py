#!/usr/bin/env python3

import click
import curses
import re

from game.game import Game

YAML_DIR = 'yamls'
MAX_BUFFER_LEN = 128
GAME_STATE = None

HANDLERS = {
    'c': lambda x: handle_command(x),
    'n': lambda x: handle_next(x),
}

COMMANDS = {
    'i': lambda x: set_initiative(x),
    's': lambda x: sort_init_list(x),
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


def handle_next(screen):
    GAME_STATE.next_initiative()
    return 'n'


def sort_init_list(argslist):
    if len(argslist) < 1:
        return

    GAME_STATE.sort_init_list()


def set_initiative(argslist):
    if len(argslist) < 3:
        return

    name_exp = argslist[1]
    init_val = argslist[-1]
    GAME_STATE.set_initiative(name_exp, init_val)


def handle_command(screen):
    render_input_panel(screen)
    raw = get_input(screen, 1, 1)
    st = raw.split()
    if len(st) < 1:
        return ''
    cmd = st[0]
    if cmd in COMMANDS.keys():
        COMMANDS[cmd](st)
        return raw
    return ''


def get_input(screen, y, x):
    c = screen.getkey()
    ret = ''
    while c != '\n' and len(ret) < MAX_BUFFER_LEN:
        if c == 'KEY_BACKSPACE':
            ret = ret[:-1]
        else:
            ret += c
        screen.clear()
        screen.addstr(y, x, ret)
        c = screen.getkey()
    return ret


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
    panel.move(1, 1)


def main(stdscr, pcs, yaml_dir):
    kwargs = {}
    YAML_DIR = yaml_dir
    kwargs['pcs_yaml'] = '{}/{}'.format(YAML_DIR, pcs)

    global GAME_STATE
    GAME_STATE = Game(**kwargs)
    cmd_log = []

    stdscr.border(0)
    height, width = stdscr.getmaxyx()
    height -= 2
    width -= 2
    global MAX_BUFFER_LEN
    MAX_BUFFER_LEN = width

    input_panel = curses.newwin(3, width, height, 0)
    input_panel.keypad(True)

    box1_width = 40
    box1 = curses.newwin(height-2, box1_width, 0, 0)
    box1.immedok(True)

    box2_width = 40
    box2 = curses.newwin(height-2, box1_width, 0, box1_width+1)
    box2.immedok(True)

    stdscr.clear()
    while True:
        stdscr.clear()

        render_input_panel(input_panel)
        render_box(box1, height, box1_width, "Initiative Tracker",
                   GAME_STATE.initiative_list)
        render_box(box2, height, box2_width, "Commands", cmd_log)
        stdscr.refresh()
        key = input_panel.getkey()
        if key in HANDLERS.keys():
            cmd = HANDLERS[key](input_panel)
            if cmd != '' or cmd is not None:
                cmd_log.append(cmd)


if __name__ == '__main__':
    start()
