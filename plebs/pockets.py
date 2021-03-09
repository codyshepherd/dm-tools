#!/usr/bin/env python3
import click
import os

from plebs.plebs import gen_items

OUT_DIR = os.path.dirname(__file__)


@click.command()
@click.option('-n', '--number', type=int,
              help="The number of items to generate", default=1)
@click.option('-y', '--yaml-dump', is_flag=True,
              help="Dump to yaml")
def pockets(number, yaml_dump):

    items = gen_items(**{'num_items': int(number)})

    string = '\n'.join(items)
    print(string)
    if yaml_dump:
        pass


if __name__ == '__main__':
    pockets()
