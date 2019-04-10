#!/usr/bin/env python3

import click
import datetime
import logging
import os
import random
import yaml

from typing import Text     # noqa

# roll dice
# display party
#   initiative
#   conditions
YAML_DIR = 'yamls'


class Game(object):

    def __init__(self, **kwargs):
        self.pcs_yaml = kwargs.get('pcs_yaml')

        self.sessions_yaml = kwargs.get('sessions_yaml')

        self.load_pcs()

        if self.chars == {}:
            raise Exception("No characters found.")

        self.load_session_notes()

    def load_pcs(self):
        with open(self.pcs_yaml, 'r') as fh:
            try:
                self.chars = yaml.load(fh, Loader=yaml.Loader)
            except yaml.YAMLError as exc:
                logging.exception(exc)

    def load_session_notes(self):
        if not os.path.exists(self.sessions_yaml):
            with open(self.sessions_yaml, 'w+') as fh:
                fh.write('- session:\n    date: {}\n    notes:'.format(
                    datetime.datetime.now().strftime('%Y%m%d%H%M')))

        with open(self.sessions_yaml, 'r') as fh:
            try:
                self.session_notes = yaml.load(fh, Loader=yaml.Loader)
            except yaml.YAMLError as exc:
                logging.exception(exc)

    @property
    def chars_display(self):
        # type: () -> List[Text]
        lst = []
        for char in self.chars:
            if not char['character']['active']:
                continue
            ch = char['character']

            def checkname(x):
                return x['item']['name'] if x['item'] is not None else \
                        'No Entry'

            items = ch['items']
            itemstring = ''
            if len(items) > 0:
                itemstring = '\n'.join(list(map(checkname, items)))

            lst += '{}\nItems:\n{}\n\nConditions:\nPermanent:\n{}\nTemporary:\n{}===\n\n'.format(
                  ch['name'],
                  itemstring,
                  ch['conditions']['permanent'],
                  ch['conditions']['temporary'],
                  )

        return ''.join(lst)

    @staticmethod
    def roll(num, die):
        # type: (int, int) -> (Text, int)
        total = 0
        rolls = ''

        for i in range(num):
            roll = random.randint(1, die)
            total += roll
            rolls += str(roll) + ', '

        return rolls, total


@click.command()
@click.option('--pcs', type=click.Path(dir_okay=False, writable=True,
              readable=True), default='pcs.yaml',
              help='name of alternate PCs file')
@click.option('--session', type=click.Path(dir_okay=False, writable=True,
              readable=True), default='session.yaml',
              help='name of alternate session file')
@click.option('--yaml-dir', type=click.Path(exists=True, dir_okay=True,
              file_okay=False, writable=True, readable=True), default='yamls',
              help='path to alternate yaml dir')
def live_game(pcs, session, yaml_dir):
    kwargs = {}
    if yaml_dir is not None:
        YAML_DIR = yaml_dir
    if session is not None:
        kwargs['sessions_yaml'] = '{}/{}'.format(YAML_DIR, session)
    if pcs is not None:
        kwargs['pcs_yaml'] = '{}/{}'.format(YAML_DIR, pcs)
    try:
        game = Game(**kwargs)
        txt = game.chars_display
        print(txt)
    except Exception as exc:
        logging.exception(exc)


def main():
    live_game(obj={})


if __name__ == '__main__':
    main()
