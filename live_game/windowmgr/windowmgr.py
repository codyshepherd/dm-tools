import os
import re

from functools import reduce


def maybe_append(oldrow, newtext):
    # type: (string, string) -> (string, string)
    # returns newrow, remaining newtext

    # match for empty row
    empty = re.search(r'^.+[ ]*.+$', oldrow)
    if empty is None:
        return oldrow, newtext

    len_whitespace = len(oldrow)-2
    whitestring = ''.join([' ' for i in range(len_whitespace)])
    newtext_sub = newtext[:len_whitespace]
    rem_newtext = newtext[len_whitespace:]
    newrow = oldrow.replace(whitestring, newtext_sub)
    return newrow, rem_newtext


def append_text(wnum, text, **kwargs):
    window = kwargs.get(wnum, {})
    oldtext = window.get('text', '')
    window['text'] = oldtext + text + '\n'
    kwargs[wnum] = window
    return kwargs


def compose_frames(frames, **kwargs):
    split_frames = list(map(lambda l: l.split('\n'), frames))
    frames_len = len(split_frames[0])

    composed = ''
    for i in range(frames_len):
        composed += reduce(lambda l1, l2: l1 + l2[i], split_frames, '') + '\n'
    return composed


def frame(height, width, hchar, vchar):
    top_btm = ''.join([hchar for i in range(width)])
    mid = [vchar] + [' ' for i in range(width-2)] + [vchar]
    wframe = (top_btm + '\n' +
              '\n'.join([''.join(mid) for i in range(height-2)]) + '\n' +
              top_btm)
    return wframe


def render_window(**kwargs):
    rows, columns = os.popen('stty size', 'r').read().split()
    rows = int(rows) - 2
    columns = int(columns)

    three_col_width = columns // 3
    remainder = columns % 3
    widths = [three_col_width, three_col_width, three_col_width+remainder]
    composed = compose_frames([frame(rows, w, '-', '|') for w in widths],
                              **kwargs)
    # composed = compose_frames([frame(4, 4, '-', '|') for w in widths])
    print(composed)


if __name__ == '__main__':
    print(maybe_append('|   |', "lots of text"))
    # render_window()
