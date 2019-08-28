#!/usr/bin/env python3

import click
import curses
import curses.ascii
import os
import sys

from game.game import Game

STDSCR = None

INIT_BOX = None
INIT_BOX_TITLE = "Initiative Tracker"
INIT_BOX_WIDTH = 0
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
BASE_DIR = os.path.expanduser('.dm-tools')
PCS_FILENAME = 'pcs.yaml'
WRITE_CHANGES = True
YAML_DIR = 'yamls'

CUR_BOX = None
CUR_BOX_OPTIONS = None
CUR_BOX_TEXT = None
CUR_BOX_TITLE = None
CURSOR_INDEX = 0

INIT_OPTION_TUPLES = {
    'a': (lambda: add_character(), 'Add Character'),
    'c': (lambda: clear_init(), 'Clear Initiative'),
    'd': (lambda: defer_initiative(), 'Defer Turn'),
    'n': (lambda: handle_next(), 'Next Character'),
    'r': (lambda: remove_character(), 'Remove Character'),
    's': (lambda: sort_init_list(), 'Sort List'),
}

STATUS_OPTION_TUPLES = {
    'a': (lambda: add_character(), 'Add Character'),
    'r': (lambda: remove_char_statusbox_wrapper(), 'Remove Character'),
}

HELP_TEXT = {
    'Add': 'Add Character: Enter name',
    'Cancel': 'Hit `\u0331 (backtick) to Cancel',
    'Quit': 'Hit q\u0331 to Quit',
    INIT_BOX_TITLE: '  '.join([k+'\u0331: {}'.format(v[1]) for k,v in
                               INIT_OPTION_TUPLES.items()]),
    STATUS_BOX_TITLE: '  '.join([k+'\u0331: {}'.format(v[1]) for k,v in
                                 STATUS_OPTION_TUPLES.items()]),
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


def add_character():
    name = get_input(helptext=HELP_TEXT['Add'])
    if len(name) < 1:
        return "no input"

    GAME_STATE.add_character(name)
    INIT_BOX.clear()
    STATUS_BOX.clear()
    return f'Add {name}'


def clear_help_text():
    HELP_PANEL.clear()
    HELP_PANEL.addstr(0, BOX_PADDING, '')
    HELP_PANEL.refresh()


def clear_init():
    GAME_STATE.clear_init()
    INIT_BOX.clear()
    return 'Clear Initiative'


def clear_refresh_all():
    STDSCR.clear()
    STDSCR.refresh()
    INPUT_PANEL.clear()
    INPUT_PANEL.refresh()
    HELP_PANEL.clear()
    HELP_PANEL.refresh()
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
    INIT_BOX.clear()
    INIT_BOX.refresh()
    return f'defer: {name}'


def display_help_text(text):
    HELP_PANEL.clear()
    if len(text) > MAX_BUFFER_LEN:
        text = text[:MAX_BUFFER_LEN]

    HELP_PANEL.addstr(0, BOX_PADDING, text, curses.A_STANDOUT)
    HELP_PANEL.refresh()


def edit_status(text=None):

    choice = GAME_STATE.pcs_status_list[CURSOR_INDEX]
    choice_list = choice.split()
    choice_part = choice_list[0]

    if choice_part == 'Name:':
        # update name
        return 'Name change not implemented yet'
    elif choice_part in Game.hearts:
        # get HP update
        if text is None or len(text) < 1:
            change = get_input()
        else:
            change = text
        if not is_integer(change) and not is_float(change):
            return 'non-integer input'

        change_type = None
        change_str = change
        if change[0] == '-' or change[0] == '+':
            change_type = change[0]
            change = change[1:]
        elif is_float(change):
            change_type = 'set max'
        name = get_status_owner()

        GAME_STATE.update_hp(name, change, change_type, WRITE_CHANGES)

        STATUS_BOX.clear()
        return ' '.join([name, change_str])

    elif choice_part == Game.bang:
        # add condition
        return 'Managing conditions not implemented'
    else:
        # remove condition
        return 'Managing conditions not implemented'


def execute_box_choice(text):
    if text is None or len(text) < 1:
        return 'no input to execute'
    if CUR_BOX == INIT_BOX:
        return execute_init_box_choice(text)
    elif CUR_BOX == STATUS_BOX:
        return execute_status_box_choice(text)


def execute_init_box_choice(text):
    if text is None or len(text) < 1:
        return 'no input'
    elif text.isdigit():
        text = text.split()[0]
        name = GAME_STATE.initiative_list[CURSOR_INDEX]
        name = ' '.join(name.split()[1:])
        GAME_STATE.set_initiative(name, text)
        return f'Set initiative: {name} {text}'
    elif text.lower() in INIT_OPTION_TUPLES.keys():
        return INIT_OPTION_TUPLES[text.lower()][0]()


def execute_status_box_choice(text):
    global CUR_BOX_TEXT
    if text is None or len(text) < 1:
        return 'no input'
    elif is_integer(text) or is_float(text):
        return edit_status(text)
    elif text.lower() in STATUS_OPTION_TUPLES.keys():
        returntext = STATUS_OPTION_TUPLES[text.lower()][0]()
        CUR_BOX_TEXT = GAME_STATE.pcs_status_list
        return returntext


def get_input(keys=None, helptext=''):
    display_help_text('; '.join([HELP_TEXT['Cancel'], helptext]))

    INPUT_PANEL.move(1, 1)
    INPUT_PANEL.clear()
    ret = '' if keys is None or keys in FINAL_KEYS else keys
    INPUT_PANEL.addstr(1, 1, ret)
    render_input_panel()
    key = INPUT_PANEL.getkey()
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
        INPUT_PANEL.clear()
        return ''
    INPUT_PANEL.clear()
    return ret


def get_status_owner():
    tmp_index = CURSOR_INDEX
    part = GAME_STATE.pcs_status_list[tmp_index].split()[0]
    while part != 'Name:':
        tmp_index -= 1
        part = GAME_STATE.pcs_status_list[tmp_index].split()[0]
    line = GAME_STATE.pcs_status_list[tmp_index]
    return ' '.join(line.split()[1:])


def handle_next():
    GAME_STATE.next_initiative()
    INIT_BOX.clear()
    INIT_BOX.refresh()
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


def remove_character(name=None):
    global CURSOR_INDEX
    if name is None or name not in GAME_STATE.pc_names:
        init_and_name_list = GAME_STATE.initiative_list[CURSOR_INDEX].split()
        name = ' '.join(init_and_name_list[1:])

    GAME_STATE.remove_character(name)
    if CUR_BOX == INIT_BOX:
        CUR_BOX_TEXT = GAME_STATE.initiative_list
    else:
        CUR_BOX_TEXT = GAME_STATE.pcs_status_list
    if CURSOR_INDEX >= len(CUR_BOX_TEXT):
        CURSOR_INDEX = len(CUR_BOX_TEXT)-1
    INIT_BOX.clear()
    STATUS_BOX.clear()
    return f'remove: {name}'


def remove_char_statusbox_wrapper():
    choice = GAME_STATE.pcs_status_list[CURSOR_INDEX]
    choice_list = choice.split()
    choice_part = choice_list[0]

    if choice_part == 'Name:':
        return remove_character(' '.join(choice_list[1:]))
    elif choice_part in Game.hearts or choice_part == f'{Game.bang}:':
        name = get_status_owner()

        return remove_character(name)


def render_box(box, height, width, title, strings):
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


def sort_init_list():
    GAME_STATE.sort_init_list()
    INIT_BOX.clear()
    return 'sort init descending'


def main(pcs, write_changes):
    global STDSCR
    global INIT_BOX
    global INIT_BOX_WIDTH
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
    global WRITE_CHANGES
    global CUR_BOX
    global CUR_BOX_OPTIONS
    global CUR_BOX_TEXT
    global CUR_BOX_TITLE
    global CURSOR_INDEX

    kwargs = {}
    kwargs['pcs_yaml'] = pcs

    GAME_STATE = Game(**kwargs)

    if not write_changes:
        WRITE_CHANGES = False

    HEIGHT, WIDTH = STDSCR.getmaxyx()
    HEIGHT -= BOX_PADDING
    WIDTH -= BOX_PADDING
    MAX_BUFFER_LEN = WIDTH
    INIT_BOX_WIDTH = 40
    STATUS_BOX_WIDTH = 40
    LOG_BOX_WIDTH = (WIDTH // 3) - BOX_PADDING

    HELP_PANEL = curses.newwin(1, WIDTH, HEIGHT-2, 0)

    INPUT_PANEL = curses.newwin(3, WIDTH, HEIGHT-1, 0)
    INPUT_PANEL.immedok(True)
    INPUT_PANEL.keypad(True)

    INIT_BOX = curses.newwin(HEIGHT-BOX_PADDING, INIT_BOX_WIDTH, 0, 0)
    INIT_BOX.immedok(True)
    INIT_BOX.keypad(True)

    STATUS_BOX = curses.newwin(HEIGHT-BOX_PADDING, STATUS_BOX_WIDTH, 0,
                               INIT_BOX_WIDTH + 2)
    STATUS_BOX.immedok(True)
    STATUS_BOX.keypad(True)

    CUR_BOX = INIT_BOX
    CUR_BOX_OPTIONS = INIT_OPTION_TUPLES
    CUR_BOX_TEXT = GAME_STATE.initiative_list
    CUR_BOX_TITLE = INIT_BOX_TITLE

    keystrokes_list = []
    key_list_max_len = HEIGHT-8
    LOG_BOX = curses.newwin(HEIGHT-BOX_PADDING, LOG_BOX_WIDTH, 0,
                            INIT_BOX_WIDTH +
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

            STATUS_BOX.resize(HEIGHT-BOX_PADDING, STATUS_BOX_WIDTH)
            LOG_BOX.resize(HEIGHT-BOX_PADDING, LOG_BOX_WIDTH)
            HELP_PANEL.resize(1, WIDTH)
            INPUT_PANEL.resize(3, WIDTH)

            INIT_BOX.mvwin(0, 0)
            STATUS_BOX.mvwin(0, INIT_BOX_WIDTH +
                             2)
            LOG_BOX.mvwin(0, INIT_BOX_WIDTH +
                          STATUS_BOX_WIDTH +
                          3)
            HELP_PANEL.mvwin(HEIGHT-2, 0)
            INPUT_PANEL.mvwin(HEIGHT-1, 0)
            clear_refresh_all()

        render_box(INIT_BOX, HEIGHT, INIT_BOX_WIDTH, INIT_BOX_TITLE,
                   GAME_STATE.initiative_list)
        render_box(STATUS_BOX, HEIGHT, STATUS_BOX_WIDTH, STATUS_BOX_TITLE,
                   GAME_STATE.pcs_status_list)
        render_box(LOG_BOX, HEIGHT, LOG_BOX_WIDTH, LOG_BOX_TITLE,
                   keystrokes_list)
        render_input_panel()

        CUR_BOX.move(BOX_BUFFER_SPACES + CURSOR_INDEX, BOX_PADDING)
        display_help_text('; '.join([
                                    HELP_TEXT['Quit'],
                                    HELP_TEXT[CUR_BOX_TITLE],
                                    ]))
        key = CUR_BOX.getkey()

        if key in UP_DOWN_KEYS:
            CURSOR_INDEX = navkey_to_index(key, CUR_BOX_TEXT, CURSOR_INDEX)
        elif key.lower() == 'q':
            sys.exit(0)
        elif key in RIGHT_LEFT_KEYS:
            if key == "KEY_LEFT":
                if CUR_BOX == STATUS_BOX:
                    CUR_BOX = INIT_BOX
                    CUR_BOX_OPTIONS = INIT_OPTION_TUPLES
                    CUR_BOX_TEXT = GAME_STATE.initiative_list
                    CUR_BOX_TITLE = INIT_BOX_TITLE
                    if CURSOR_INDEX >= len(CUR_BOX_TEXT):
                        CURSOR_INDEX = len(CUR_BOX_TEXT)-1
            else:
                if CUR_BOX == INIT_BOX:
                    CUR_BOX = STATUS_BOX
                    CUR_BOX_OPTIONS = STATUS_OPTION_TUPLES
                    CUR_BOX_TEXT = GAME_STATE.pcs_status_list
                    CUR_BOX_TITLE = STATUS_BOX_TITLE
                    if CURSOR_INDEX >= len(CUR_BOX_TEXT):
                        CURSOR_INDEX = len(CUR_BOX_TEXT)-1
        elif key in CUR_BOX_OPTIONS.keys():
            printout = execute_box_choice(key)
            keystrokes_list = max_len_append(printout, keystrokes_list,
                                             key_list_max_len)
        else:
            text = get_input(key)

            printout = execute_box_choice(text)
            keystrokes_list = max_len_append(printout, keystrokes_list,
                                             key_list_max_len)


@click.command()
@click.option('--pcs', '-p', type=click.Path(dir_okay=False,
              writable=True, readable=True), default='{}/{}/{}'.format(
                  BASE_DIR, YAML_DIR, PCS_FILENAME),
              help='name of alternate PCs file')
@click.option('--session-dir', '-d', type=click.Path(dir_okay=True,
              file_okay=False, writable=True, readable=True),
              default='{}/{}'.format(BASE_DIR, YAML_DIR),
              help='path to alternate directory for writing session files')
@click.option('--write-changes/--no-write-changes',
              help="Write HP and status changes to original yaml",
              default=True)
def start(pcs, session_dir, write_changes):
    global STDSCR

    if not os.path.exists(BASE_DIR):
        os.mkdir(BASE_DIR)
    if not os.path.exists(session_dir):
        os.mkdir(session_dir)
        YAML_DIR = session_dir
        with open('{}/{}'.format(session_dir, PCS_FILENAME), 'w+') as fh:
            fh.write('')
    if not os.path.exists(pcs):
        print("The file provided to --pcs must exist")
        sys.exit(1)

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

        main(pcs, write_changes)
    finally:
        # Terminate application
        curses.nocbreak()
        curses.echo()
        STDSCR.keypad(False)
        curses.endwin()


if __name__ == '__main__':
    start()
