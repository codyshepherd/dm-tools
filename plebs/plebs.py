#!/usr/bin/env python3
import click
import names
import numpy
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


def gen_age(**kwargs):
    youngest = kwargs.get('youngest', 16)
    oldest = kwargs.get('oldest', 45)
    return random.randint(youngest, oldest)


def gen_gender(**kwargs):
    set_gender = kwargs.get('gender', None)
    if set_gender is not None:
        print(f"gender already set in gen_gender: {set_gender}")
        return set_gender
    print("no gender set yet in gen_gender")
    genders_tuples = kwargs.get('genders', [('male', .5), ('female', .5)])
    genders = [t[0] for t in genders_tuples]
    probs = [t[1] for t in genders_tuples]

    choice = numpy.random.choice(genders, p=probs)
    print(f"gender choice: {choice}")
    return choice


def gen_hp(**kwargs):
    hit_die = kwargs.get('hit_die', (1, 6))
    return reduce(lambda x, y: x+y, roll(*hit_die), 0)


def gen_name(**kwargs):
    g = kwargs.get('gender', None)
    if g is None:
        print("Gender not set, calling gen_gender")
        g = gen_gender(**kwargs)

    if g in ['male', 'female']:
        print(f"Gender set: {g}")
        gender_arg = g
    else:
        gender_arg = None

    print(f"generating name with gender_arg: {gender_arg}")
    return names.get_full_name(gender=gender_arg)


def return_race(**kwargs):
    return kwargs['race']


def gen_stats(**kwargs):
    stats = {}
    for stat in STATS:
        rolls = roll(4, 6)
        rolls.remove(min(rolls))
        stats[stat] = reduce(lambda x, y: x+y, rolls, -1)
    return stats


def pleb(race, **kwargs):
    kwargs['race'] = race
    p = {}
    for attr in ATTRIBUTES.keys():
        func = globals()[ATTRIBUTES[attr]]
        val = func(**kwargs)
        kwargs[attr] = val
        p[attr] = val
    return p


@click.command()
# @click.argument('target', type=click.Path(exists=True))
# @click.argument('source-yaml', type=click.Path(exists=True))
@click.option('-n', '--number', type=int,
              help="The number of plebs to create", default=1)
@click.option('-c', '--config-yaml', type=click.Path(exists=True),
              help="The path to a yaml config file",
              default='default-config.yaml')
@click.option('-y', '--yaml-dump', is_flag=True,
              help="Dump to yaml")
def plebs(number, config_yaml, yaml_dump):
    with open(config_yaml, 'r') as fh:
        config = yaml.load(fh)

    global ATTRIBUTES
    ATTRIBUTES = config['attributes']

    races_and_probs = config.get('races', ['Human', 1.0])
    races = [r[0] for r in races_and_probs]
    probs = [r[1] for r in races_and_probs]

    ps = {}
    for i in range(number):
        race = numpy.random.choice(races, p=probs)
        p = pleb(race, **config)
        ps[p['name']] = p
    if yaml_dump:
        with open('plebs.yaml', 'w+') as fh:
            fh.write(yaml.dump(ps))
    else:
        pprint.pprint(ps)


if __name__ == '__main__':
    plebs()
