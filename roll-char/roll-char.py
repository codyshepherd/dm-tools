#!/usr/bin/env python3
import click
import copy
import random

import numpy
import yaml

NO_SUBRACE_LIST = ['human', 'half-elf', 'half-orc']
NUM_STATS = 6


def gen_race(race=None, subrace=None):
    race = race.capitalize() if race is not None else race
    subrace = subrace.capitalize() if subrace is not None else subrace

    with open('pc_content/races.yaml', 'r') as fh:
        races_list = yaml.safe_load(fh)

    if race is None or race not in \
      [x['race']['name'] for x in races_list]:
        selected_race_dict = numpy.random.choice(races_list)['race']
    else:
        selected_race = list(filter(lambda x: x['race']['name'] == race, races_list))
        selected_race_dict = selected_race[0]['race']

    if selected_race_dict['name'].lower() in NO_SUBRACE_LIST:
        return yaml.safe_dump(selected_race_dict)

    if subrace is None or subrace not in \
      [x['subrace']['name'] for x in selected_race_dict['subraces']]:
        selected_subrace = numpy.random.choice(selected_race_dict['subraces'])
    else:
        selected_subrace = list(
            filter(
                lambda x: x['subrace']['name'] == subrace,
                selected_race_dict['subraces']))[0]

    final_dict = copy.deepcopy(selected_race_dict)
    del final_dict['subraces']

    for k,v in selected_subrace['subrace'].items():
        if k == 'name':
            final_dict[k] = ' '.join([v, final_dict[k]])
        elif type(v) != list:
            final_dict[k] = v
        else:
            final_dict[k] = final_dict.get(k, []) + v

    return yaml.safe_dump(final_dict)

@click.command()
def roll_char():
    for i in range(NUM_STATS):
        rolls = sorted([random.randint(1, 6) for x in range(4)])[1:]
        print(sum(rolls))

    print(gen_race())


if __name__ == '__main__':
    roll_char()
