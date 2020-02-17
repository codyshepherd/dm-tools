#!/usr/bin/env python3
import click
import numpy
import pprint
import random
import yaml

from plebs.plebs import gen_items
from functools import reduce
from itertools import chain
from plebs.name_gen import name_gen

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
        with open('plebs/pockets.txt', 'w+') as fh:
            fh.write(string)


if __name__ == '__main__':
    pockets()
