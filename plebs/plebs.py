#!/usr/bin/env python3
import click
import numpy
import pprint
import random
import yaml

from name_gen import name_gen
from dice import roll
from functools import reduce
from itertools import chain


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
        return set_gender
    genders_tuples = kwargs.get('genders', [('male', .5), ('female', .5)])
    genders = [t[0] for t in genders_tuples]
    probs = [t[1] for t in genders_tuples]

    choice = numpy.random.choice(genders, p=probs)
    return choice


def gen_hp(**kwargs):
    hit_die = kwargs.get('hit_die', (1, 6))
    return reduce(lambda x, y: x+y, roll(*hit_die), 0)


def gen_items(**kwargs):
    content_dir = kwargs.get('content_dir', 'content')
    items_file = kwargs.get('items', 'items.txt')
    path = '/'.join([content_dir, items_file])
    num_items = kwargs.get('num_items', None)

    max_items = int(kwargs.get('max_items', 5))
    if num_items is None:
        num_items = numpy.random.randint(0, max_items)

    with open(path, 'r') as fh:
        items = fh.read()
    items = items.split('\n')
    num = len(items)-1

    pleb_items = list()
    for i in range(num_items):
        choice = numpy.random.randint(0, num)
        pleb_items.append(items[choice])

    if len(pleb_items) < 1:
        return "none"
    return pleb_items


def gen_name(**kwargs):
    name_gen_function = name_gen.name_gen_prob

    gen = kwargs.get('name_generator', 'prob')

    if gen == 'alt':
        name_gen_function = name_gen.name_gen_alternator
    elif gen == 'norm':
        name_gen_function = name_gen.name_gen_normcore
    elif gen == 'pairs':
        name_gen_function = name_gen.name_gen_pairs
    elif gen == 'phoneme':
        name_gen_function = name_gen.name_gen_phonemes
    elif gen == 'pet':
        name_gen_function = name_gen.name_gen_petname

    fn = {'first_last': 'first'}
    ln = {'first_last': 'last'}

    name = ' '.join(
        [name_gen_function(**dict(chain(kwargs.items(), fn.items()))),
         name_gen_function(**dict(chain(kwargs.items(), ln.items())))]
    )

    with open('names_generated.txt', 'a+') as fh:
        fh.write(name + '\n')

    return name


def return_race(**kwargs):
    return kwargs['race']


def gen_profession(**kwargs):
    content_dir = kwargs.get('content_dir', 'content')
    professions_file = kwargs.get('professions', 'professions.txt')
    path = '/'.join([content_dir, professions_file])
    with open(path, 'r') as fh:
        profs = fh.read()
    profs = profs.split('\n')
    num = len(profs)-1
    choice = numpy.random.randint(0, num)
    return profs[choice]


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
    for f in FUNCTIONS.keys():
        func = FUNCTIONS[f]
        val = func(**kwargs)
        kwargs[f] = val
        p[f] = val
    return p

def stringify(d, pad=''):
    if isinstance(d, str) or isinstance(d, int) or isinstance(d, float):
        return pad + str(d)
    elif isinstance(d, list):
        return '\n'.join([stringify(i, pad) for i in d])
    if isinstance(d, dict):
        string = ''
        for k, v in d.items():
            enter = ''
            k = stringify(k, pad)
            v = stringify(v, pad + ' ')
            if '\n' in v:
                enter = '\n'
            string += f'{k}:{enter}{v}\n'
        return string


FUNCTIONS = {
  'age': gen_age,
  'gender': gen_gender,
  'hp': gen_hp,
  'name': gen_name,
  'race': return_race,
  'stats': gen_stats,
  'items': gen_items,
  'profession': gen_profession,
}


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
@click.option('-g', '--name-generator',
              type=click.Choice([
                  'alt',
                  'norm',
                  'pairs',
                  'pet',
                  'phoneme',
                  'prob',
               ]),
              help="The algorithm to use for generating names",
              default='phoneme')
def plebs(number, config_yaml, yaml_dump, name_generator):
    with open(config_yaml, 'r') as fh:
        config = yaml.safe_load(fh)

    config['name_generator'] = name_generator

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

    string = stringify(ps)
    print(string)
    if yaml_dump:
        with open('plebs.txt', 'w+') as fh:
            fh.write(string)


if __name__ == '__main__':
    plebs()
