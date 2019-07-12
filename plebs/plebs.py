#!/usr/bin/env python3
import click
import names
import pprint
import random
import yaml

from dice import roll
from functools import reduce


STATS = [
    "str",
    "dex",
    "con",
    "int",
    "wis",
    "cha",
]

DEFAULT_RACES = [
    'Dragonborn',
    'Dwarf',
    'Elf',
    'Gnome',
    'Half-elf',
    'Halfling',
    'Half-Orc',
    'Human',
    'Tiefling',
]


def gen_age(**kwargs):
    youngest = kwargs.get('youngest', 16)
    oldest = kwargs.get('oldest', 80)
    return random.randint(youngest, oldest)


def gen_name(**kwargs):
    return names.get_full_name()


def return_race(**kwargs):
    return kwargs['race']


def gen_stats(**kwargs):
    stats = {}
    for stat in STATS:
        rolls = roll(4, 6)
        rolls.remove(min(rolls))
        stats[stat] = reduce(lambda x, y: x+y, rolls, -1)
    return stats


ATTRIBUTES = {
    "stats": gen_stats,
    "name": gen_name,
    "race": return_race,
    "age": gen_age,
}


def pleb(race, gender):
    kwargs = {
        'race': race,
        'gender': gender,
    }
    p = {}
    for attr in ATTRIBUTES.keys():
        p[attr] = ATTRIBUTES[attr](**kwargs)
    return p


@click.command()
# @click.argument('target', type=click.Path(exists=True))
# @click.argument('source-yaml', type=click.Path(exists=True))
@click.option('-n', '--number', type=int,
              help="The number of plebs to create", default=1)
@click.option('-r', '--races', type=str,
              help="Space separated list of races for plebs",
              default=' '.join(DEFAULT_RACES))
@click.option('-y', '--yaml-dump', is_flag=True,
              help="Dump to yaml")
def plebs(number, races, yaml_dump):
    ps = {}
    races_list = races.split()
    for i in range(number):
        race_num = random.randint(0, len(races_list)-1)
        p = pleb(races_list[race_num], None)
        ps[p['name']] = p
    if yaml_dump:
        with open('plebs.yaml', 'w+') as fh:
            fh.write(yaml.dump(ps))
    else:
        pprint.pprint(ps)


if __name__ == '__main__':
    plebs()
