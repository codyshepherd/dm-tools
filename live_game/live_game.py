#!/usr/bin/env python3

import click
import curses
import curses.ascii
import os
import pathlib
import sys

from live_game.game.game import Game, Character

STDSCR = None

INIT_BOX = None
INIT_BOX_TITLE = "Initiative Tracker"
INIT_BOX_WIDTH = 0
INIT_LIST_LOWER_INDEX = 0
INIT_LIST_UPPER_INDEX = 0
STATUS_BOX = None
STATUS_BOX_TITLE = "Status"
STATUS_BOX_WIDTH = 0
STATUS_CURSOR_MAX_UPPER = 0
STATUS_ENTRY_LENGTH = 6
MENU_BOX = None
MENU_BOX_TITLE = "Menu"
MENU_BOX_WIDTH = 0
MENU_BOX_HEIGHT = 0
MENU_TEXT = ''
LOG_BOX = None
LOG_BOX_TITLE = "Log"
LOG_BOX_WIDTH = 0
LEGEND_BOX = None
LEGEND_BOX_TITLE = "Legend"
LEGEND_BOX_WIDTH = 0
LEGEND_BOX_HEIGHT = 0
LEGEND_BOX_TEXT = ''
LEGEND_TEXT_LOW = 0
LEGEND_TEXT_HIGH = 0
HELP_PANEL = None
INPUT_PANEL = None

BOX_BUFFER_SPACES = 4
BOX_BOTTOM_BUFFER = 3
BOX_HEIGHT_PADDING = 5
BOX_PADDING = 2
GAME_STATE = None
HEIGHT = 0
MAX_BUFFER_LEN = 128
WIDTH = 0
BASE_DIR = os.path.expanduser('dm-tools/live_game/')
PCS_FILENAME = 'pcs.yaml'
WRITE_CHANGES = True
YAML_DIR = 'yamls/'

CUR_BOX = None
CUR_BOX_OPTIONS = None
CUR_BOX_TEXT = None
CUR_BOX_TITLE = None
CURSOR_INDEX = 0

INIT_OPTION_TUPLES = {
    'a': (lambda: add_character(), 'Add Character'),
    'x': (lambda: clear_init(), 'Clear Initiative'),
    't': (lambda: defer_initiative(), 'Defer Turn'),
    'n': (lambda: handle_next(), 'Next Character'),
    'r': (lambda: remove_character(), 'Remove Character'),
    's': (lambda: sort_init_list(), 'Sort List'),
    '1-99': (lambda: set_initiative(), 'Set Initiative'),
    'l': (lambda: scroll_legend_down(), 'Scroll Legend'),
}

STATUS_OPTION_TUPLES = {
    'a': (lambda: add_character(), 'Add Character'),
    'c': (lambda: add_condition(), 'Condition Add'),
    'd': (lambda: delete_condition(), 'Delete Condition'),
    'h': (lambda: set_hp(), 'Set HP'),
    '-/+': (lambda: set_hp(), 'Edit temp HP'),
}

ALL_OPTIONS_TUPLES = {**INIT_OPTION_TUPLES, **STATUS_OPTION_TUPLES}

HELP_TEXT = {
    'Add': 'Enter name of combatant',
    'Cancel': 'Hit `\u0331 (backtick) to Cancel',
    'Conditions': 'Enter a condition',
    'Hp': 'Enter a number to set max HP; prepend -/+ to adjust temp HP',
    'Quit': 'Hit q\u0331 to Quit',
    'Remove': 'Select condition icon to remove',
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
    display_help_text('; '.join([HELP_TEXT['Add'], HELP_TEXT['Cancel']]))
    name = get_input(helptext=HELP_TEXT['Add'])
    if len(name) < 1:
        return "no input"

    GAME_STATE.add_character(name)
    return f'Add {name}'


def add_condition():
    display_help_text('; '.join([HELP_TEXT['Conditions'], HELP_TEXT['Cancel']]))
    name = GAME_STATE.initiative_list[CURSOR_INDEX]
    name = ' '.join(name.split()[1:])
    cond = get_input(helptext=HELP_TEXT['Conditions'])
    if len(cond) < 1:
        cond += "no input"
        status = 'failure'
    elif cond not in GAME_STATE.condition_emoji.keys():
        cond += " unknown"
        status = 'failure'
    else:
        status = GAME_STATE.set_condition(name, cond)
    return f'added condition {cond} to {name} {status}'


def adjust_box_indices(box, lower_val, upper_val):
    # TODO: add this functionality for init box
    '''
    global STATUS_LIST_LOWER_INDEX
    global STATUS_LIST_UPPER_INDEX
    if box == INIT_BOX:
        pass
    elif box == STATUS_BOX:
        STATUS_LIST_LOWER_INDEX = lower_val
        STATUS_LIST_UPPER_INDEX = upper_val
    '''
    pass


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
    if len(GAME_STATE.initiative_list) < 1:
        return 'no combatants present'
    init_and_name_list = GAME_STATE.initiative_list[0].split()
    name = ' '.join(init_and_name_list[1:])
    GAME_STATE.defer_initiative()
    INIT_BOX.clear()
    return f'defer: {name}'


def delete_condition():
    display_help_text('; '.join([HELP_TEXT['Remove'], HELP_TEXT['Cancel']]))
    name = GAME_STATE.initiative_list[CURSOR_INDEX]
    name = ' '.join(name.split()[1:])
    conds = GAME_STATE.pcs[name].conditions

    if len(conds) < 1:
        return f'No conditions to remove for {name}'

    # move cursor to condiitons array
    conds_string = conds.strip()[3:]
    bang_len = 6
    
    cond_to_remove = nav_conditions(name, conds)
    if cond_to_remove == '':
        return f'Remove condition from {conds} for {name} canceled'
    cond_name = GAME_STATE.remove_condition(name, cond_to_remove)
    STATUS_BOX.clear()
    return f'remove condition {cond_name} from {name}'


def display_help_text(text):
    HELP_PANEL.clear()
    if len(text) > MAX_BUFFER_LEN:
        text = text[:MAX_BUFFER_LEN]

    HELP_PANEL.addstr(0, BOX_PADDING, text, curses.A_STANDOUT)
    HELP_PANEL.refresh()


def execute_box_choice(text):
    if text is None or len(text) < 1:
        return 'no input to execute'
    elif text.isdigit():
        text = text.split()[0]
        if len(GAME_STATE.initiative_list) < 1:
            return 'no combatants present'
        name = GAME_STATE.initiative_list[CURSOR_INDEX]
        name = ' '.join(name.split()[1:])
        GAME_STATE.set_initiative(name, text)
        return f'Set initiative: {name} {text}'
    elif text[0] in ['-', '+']:
        return set_hp(text)
    elif text == 'l':
        return scroll_legend_down()
    elif text == 'L':
        return scroll_legend_up()
    elif text.lower() in ALL_OPTIONS_TUPLES.keys():
        if len(GAME_STATE.initiative_list) < 1 and text.lower() != 'a':
            return 'no combatants present'
        return ALL_OPTIONS_TUPLES[text.lower()][0]()


def get_input(keys=None, helptext=''):

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


def legend_box_text():
    status_icons = [i + ': ' + s.capitalize() for (i, s) in \
                    zip(Game.attribute_icons, Character.legend_attributes)]
    conditions = ['Conditions', '---'] + \
     [i + ': ' + s.capitalize() for (i, s) in \
      zip(Game.condition_emoji.values(), Game.condition_emoji.keys())]

    modified_kv = [(k,v) for (k,v) in Game.damage_types.items() if k != "bludgeoning, piercing, and slashing from nonmagical weapons that aren't silvered"]
    modified_kv[-2] = ('Nonsilvered nonmagical', modified_kv[-2][1])
    modified_kv[-1] = ('Nonmagical', modified_kv[-1][1])
     
    damage = ['Dmg Types', '---'] + \
     [i + ': ' + s.capitalize() for (s, i) in modified_kv]

    return status_icons + [' '] + conditions + [' '] + damage


def max_len_append(new_item, the_list, max_len):
    ln = len(the_list)
    diff = ln - max_len
    if diff >= 0:
        the_list = the_list[diff+1:]
    the_list.append(new_item)
    return the_list


def nav_conditions(name, conds):
    global STATUS_BOX
    buf = 0
    index = 0
    horiz_buffer = 6 # two spaces of indent plus length of '!: '
    conditions_index_for_top_entry = 2
    STATUS_BOX.move(BOX_BUFFER_SPACES + conditions_index_for_top_entry,
                    BOX_PADDING + horiz_buffer)
    key = STATUS_BOX.getkey()
    string = conds
    len_string = len(string)
    while key not in FINAL_KEYS:
        if key in RIGHT_LEFT_KEYS:
            if key == 'KEY_RIGHT' and index < len_string-1:
                if string[index] != ' ':
                    buf += 2
                else:
                    buf += 1
                index += 1
            elif key == 'KEY_LEFT' and index > 0:
                if string[index] != ' ':
                    buf -= 1
                else:
                    buf -= 2
                index -= 1
        STATUS_BOX.move(BOX_BUFFER_SPACES + conditions_index_for_top_entry,
                             BOX_PADDING+horiz_buffer+buf)
        key = STATUS_BOX.getkey()
    if key == ENTER_KEY:
        if string[index] == ' ':
            return string[index-1]
        return string[index]
    else:
        return ''


def navkey_to_index(keystroke, menu_list, cursor_index, box):
    len_list = len(menu_list)
    relevant_lower = INIT_LIST_LOWER_INDEX
    relevant_upper = INIT_LIST_UPPER_INDEX
    relevant_max = STATUS_CURSOR_MAX_UPPER

    if keystroke == 'KEY_UP' and cursor_index <= 0:
        box.clear()
        if relevant_lower <= 0:
            if len_list < relevant_max:
                return len_list-1
            else:
                adjust_box_indices(box, len_list-1-relevant_max, len_list)
                box.clear()
                return relevant_max
        else:
            adjust_box_indices(box, relevant_lower-1, relevant_upper-1)
            box.clear()
            return 0
    elif keystroke == 'KEY_DOWN' and (cursor_index >= len_list-1 or \
         (len_list == relevant_max+1 and cursor_index >= relevant_upper-1) or \
         (len_list > relevant_max+1 and cursor_index >= relevant_max and relevant_upper == len_list)):
        adjust_box_indices(box, 0, relevant_max+1)
        box.clear()
        return 0
    elif keystroke == 'KEY_DOWN' and cursor_index >= relevant_max and \
            relevant_upper < len_list:
        adjust_box_indices(box, relevant_lower+1, relevant_upper+1)
        box.clear()
        return cursor_index
    elif keystroke == 'KEY_UP':
        return cursor_index - 1
    elif keystroke == 'KEY_DOWN':
        return cursor_index + 1
    else:
        return cursor_index


def remove_character(name=None):
    if len(GAME_STATE.initiative_list) < 1:
        return f'no combatants to remove'

    global CURSOR_INDEX
    if name is None or name not in GAME_STATE.pc_names:
        init_and_name_list = GAME_STATE.initiative_list[CURSOR_INDEX].split()
        name = ' '.join(init_and_name_list[1:])

    GAME_STATE.remove_character(name)
    if CURSOR_INDEX >= len(GAME_STATE.initiative_list):
        CURSOR_INDEX = len(GAME_STATE.initiative_list)-1
    INIT_BOX.clear()
    STATUS_BOX.clear()
    return f'remove: {name}'


def render_box(box, height, width, title, strings):
    box.box()
    box.addstr(1, BOX_PADDING, title)
    box.addstr(BOX_PADDING, 1, ''.join('-' for i in range(width-BOX_PADDING)))
    start = BOX_BUFFER_SPACES
    for string in strings:
        if start == height-BOX_BOTTOM_BUFFER:
            break
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


def scroll_legend_down():
    global LEGEND_TEXT_LOW
    global LEGEND_TEXT_HIGH

    LEGEND_TEXT_LOW += 1
    LEGEND_TEXT_HIGH += 1

    if LEGEND_TEXT_HIGH > len(LEGEND_BOX_TEXT):
        LEGEND_TEXT_LOW = 0
        LEGEND_TEXT_HIGH = LEGEND_BOX_HEIGHT - BOX_PADDING - BOX_HEIGHT_PADDING
    elif LEGEND_TEXT_LOW < 0:
        LEGEND_TEXT_HIGH = len(LEGEND_BOX_TEXT)
        LEGEND_TEXT_LOW = LEGEND_TEXT_HIGH - (LEGEND_BOX_HEIGHT - \
            (BOX_PADDING + BOX_HEIGHT_PADDING))

    LEGEND_BOX.clear()


def scroll_legend_up():
    global LEGEND_TEXT_LOW
    global LEGEND_TEXT_HIGH

    LEGEND_TEXT_LOW -= 1
    LEGEND_TEXT_HIGH -= 1

    if LEGEND_TEXT_HIGH > len(LEGEND_BOX_TEXT):
        LEGEND_TEXT_LOW = 0
        LEGEND_TEXT_HIGH = LEGEND_BOX_HEIGHT - BOX_PADDING - BOX_HEIGHT_PADDING
    elif LEGEND_TEXT_LOW < 0:
        LEGEND_TEXT_HIGH = len(LEGEND_BOX_TEXT)
        LEGEND_TEXT_LOW = LEGEND_TEXT_HIGH - (LEGEND_BOX_HEIGHT - \
            (BOX_PADDING + BOX_HEIGHT_PADDING))

    LEGEND_BOX.clear()


def set_hp(text=None):
    display_help_text('; '.join([HELP_TEXT['Hp'], HELP_TEXT['Cancel']]))
    if len(GAME_STATE.initiative_list) < 1:
        return 'no combatants present'
    name = GAME_STATE.initiative_list[CURSOR_INDEX]
    name = ' '.join(name.split()[1:])

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
    else:
        change_type = 'set max'

    GAME_STATE.update_hp(name, change, change_type, WRITE_CHANGES)

    STATUS_BOX.clear()
    return ' '.join([name, change_str])


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
    global STATUS_CURSOR_MAX_UPPER
    global MENU_BOX
    global MENU_BOX_WIDTH
    global MENU_BOX_HEIGHT
    global MENU_TEXT
    global LOG_BOX
    global LOG_BOX_WIDTH
    global LEGEND_BOX
    global LEGEND_BOX_TITLE
    global LEGEND_BOX_WIDTH
    global LEGEND_BOX_HEIGHT
    global LEGEND_BOX_TEXT
    global LEGEND_TEXT_LOW
    global LEGEND_TEXT_HIGH
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
    MENU_BOX_TEXT = sorted([' '.join([k, v[1]]) for k, v in
                     ALL_OPTIONS_TUPLES.items()])
    MENU_BOX_WIDTH = max([len(s) for s in MENU_BOX_TEXT]) + BOX_BUFFER_SPACES
    INIT_BOX_WIDTH = 40
    STATUS_BOX_WIDTH = 40
    LEGEND_BOX_TEXT = legend_box_text()
    LOG_BOX_WIDTH = WIDTH - MENU_BOX_WIDTH - INIT_BOX_WIDTH - \
                    STATUS_BOX_WIDTH - 3

    HELP_PANEL = curses.newwin(1, WIDTH, HEIGHT-2, 0)

    MENU_BOX_HEIGHT = len(MENU_BOX_TEXT) + BOX_PADDING + BOX_HEIGHT_PADDING
    MENU_BOX = curses.newwin(MENU_BOX_HEIGHT-BOX_PADDING, MENU_BOX_WIDTH, 0,
                             0)
    MENU_BOX.immedok(True)
    MENU_BOX.keypad(True)

    INPUT_PANEL = curses.newwin(3, WIDTH, HEIGHT-1, 0)
    INPUT_PANEL.immedok(True)
    INPUT_PANEL.keypad(True)

    INIT_BOX = curses.newwin(HEIGHT-BOX_PADDING, INIT_BOX_WIDTH, 0,
                             MENU_BOX_WIDTH + 1)
    INIT_BOX.immedok(True)
    INIT_BOX.keypad(True)

    LEGEND_BOX_WIDTH = MENU_BOX_WIDTH
    LEGEND_BOX_HEIGHT = HEIGHT - MENU_BOX_HEIGHT + BOX_PADDING
    LEGEND_TEXT_HIGH = LEGEND_BOX_HEIGHT - BOX_PADDING - BOX_HEIGHT_PADDING
    if LEGEND_TEXT_HIGH > len(LEGEND_BOX_TEXT):
        LEGEND_TEXT_HIGH = len(LEGEND_BOX_TEXT)
    LEGEND_BOX = curses.newwin(LEGEND_BOX_HEIGHT-BOX_PADDING,
                               LEGEND_BOX_WIDTH, HEIGHT - LEGEND_BOX_HEIGHT,
                               0)

    LEGEND_BOX.immedok(True)
    LEGEND_BOX.keypad(True)

    STATUS_BOX = curses.newwin(HEIGHT-BOX_PADDING, STATUS_BOX_WIDTH, 0,
                               MENU_BOX_WIDTH + INIT_BOX_WIDTH + 2)
    STATUS_BOX.immedok(True)
    STATUS_BOX.keypad(True)
    STATUS_BOX.scrollok(True)
    STATUS_BOX.idlok(True)
    STATUS_CURSOR_MAX_UPPER = HEIGHT - (BOX_HEIGHT_PADDING + BOX_BOTTOM_BUFFER)

    CUR_BOX = INIT_BOX
    CUR_BOX_OPTIONS = INIT_OPTION_TUPLES
    CUR_BOX_TEXT = GAME_STATE.initiative_list
    CUR_BOX_TITLE = INIT_BOX_TITLE

    keystrokes_list = []
    key_list_max_len = HEIGHT-8
    LOG_BOX = curses.newwin(HEIGHT-BOX_PADDING, LOG_BOX_WIDTH, 0,
                            INIT_BOX_WIDTH +
                            STATUS_BOX_WIDTH +
                            MENU_BOX_WIDTH + 
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
            LOG_BOX_WIDTH = WIDTH - MENU_BOX_WIDTH - INIT_BOX_WIDTH - \
                            STATUS_BOX_WIDTH - 15
            LEGEND_BOX_HEIGHT = HEIGHT - MENU_BOX_HEIGHT + BOX_PADDING

            HELP_PANEL.resize(1, WIDTH)
            INPUT_PANEL.resize(3, WIDTH)
            INIT_BOX.resize(HEIGHT-BOX_PADDING, INIT_BOX_WIDTH)

            STATUS_BOX.resize(HEIGHT-BOX_PADDING, STATUS_BOX_WIDTH)
            LOG_BOX.resize(HEIGHT-BOX_PADDING, LOG_BOX_WIDTH)
            LEGEND_BOX.resize(LEGEND_BOX_HEIGHT, LEGEND_BOX_WIDTH)
            HELP_PANEL.resize(1, WIDTH)
            INPUT_PANEL.resize(3, WIDTH)

            MENU_BOX.mvwin(0, 0)
            INIT_BOX.mvwin(0, MENU_BOX_WIDTH + 2)
            STATUS_BOX.mvwin(0, INIT_BOX_WIDTH + MENU_BOX_WIDTH + 4)
            LOG_BOX.mvwin(0, INIT_BOX_WIDTH +
                          STATUS_BOX_WIDTH +
                          MENU_BOX_WIDTH + 
                          5)

            LEGEND_TEXT_LOW = 0
            LEGEND_TEXT_HIGH = LEGEND_BOX_HEIGHT - BOX_PADDING - BOX_HEIGHT_PADDING
            LEGEND_BOX.mvwin(MENU_BOX_HEIGHT - BOX_PADDING, 0)
            HELP_PANEL.mvwin(HEIGHT-2, 0)
            INPUT_PANEL.mvwin(HEIGHT-1, 0)
            clear_refresh_all()

        if len(GAME_STATE.initiative_list) > 0:
            name = GAME_STATE.initiative_list[CURSOR_INDEX]
            name = ' '.join(name.split()[1:])
            GAME_STATE.promote_pc_in_status_list(name)

        STATUS_BOX.clear()
        render_box(MENU_BOX, MENU_BOX_HEIGHT, MENU_BOX_WIDTH, MENU_BOX_TITLE,
                   MENU_BOX_TEXT)
        render_box(INIT_BOX, HEIGHT, INIT_BOX_WIDTH, INIT_BOX_TITLE,
                   GAME_STATE.initiative_list)
        render_box(STATUS_BOX, HEIGHT, STATUS_BOX_WIDTH, STATUS_BOX_TITLE,
                   GAME_STATE.pcs_status_list[:STATUS_CURSOR_MAX_UPPER+1])
        render_box(LOG_BOX, HEIGHT, LOG_BOX_WIDTH, LOG_BOX_TITLE,
                   keystrokes_list)
        render_box(LEGEND_BOX, LEGEND_BOX_HEIGHT, LEGEND_BOX_WIDTH,
                   LEGEND_BOX_TITLE,
                   LEGEND_BOX_TEXT[LEGEND_TEXT_LOW:LEGEND_TEXT_HIGH])
        render_input_panel()
        display_help_text(HELP_TEXT['Quit'])

        CUR_BOX.move(BOX_BUFFER_SPACES + CURSOR_INDEX, BOX_PADDING)
        key = CUR_BOX.getkey()

        if key in UP_DOWN_KEYS:
            CURSOR_INDEX = navkey_to_index(key, GAME_STATE.initiative_list,
                                           CURSOR_INDEX, INIT_BOX)
        elif key.lower() == 'q':
            sys.exit(0)
        elif key in RIGHT_LEFT_KEYS:
            continue
        elif key.lower() in ALL_OPTIONS_TUPLES.keys():
            printout = execute_box_choice(key)
            keystrokes_list = max_len_append(printout, keystrokes_list,
                                             key_list_max_len)
        else:
            text = get_input(key)

            printout = execute_box_choice(text)
            keystrokes_list = max_len_append(printout, keystrokes_list,
                                             key_list_max_len)
        LOG_BOX.clear()
        LOG_BOX.refresh()


@click.command()
@click.option('--pcs', '-p', type=click.Path(dir_okay=False,
              writable=True, readable=True), default=f'{BASE_DIR}{YAML_DIR}{PCS_FILENAME}',
              help='name of alternate PCs file')
@click.option('--session-dir', '-d', type=click.Path(dir_okay=True,
              file_okay=False, writable=True, readable=True),
              default=f'{BASE_DIR}{YAML_DIR}',
              help='path to alternate directory for writing session files')
@click.option('--write-changes/--no-write-changes',
              help="Write HP and status changes to original yaml",
              default=True)
def start(pcs, session_dir, write_changes):
    global STDSCR
    global YAML_DIR

    if not os.path.exists(BASE_DIR):
        pathlib.Path(BASE_DIR).mkdir(parents=True, exist_ok=True)
    if not os.path.exists(session_dir):
        pathlib.Path(session_dir).mkdir(parents=True, exist_ok=True)
        YAML_DIR = session_dir
        with open(f'{session_dir}{PCS_FILENAME}', 'w+') as fh:
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
