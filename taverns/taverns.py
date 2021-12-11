import os
import random
import sys

import click
import numpy

from functools import partial

# append the path of the parent directory
sys.path.append("..")

import plebs.plebs as plebs_module
from plebs import (
  name_gen as ng,
  pockets,
)
from taverns.name_gen import name_gen


OUT_DIR = os.path.dirname(__file__)
CONTENT_DIR = os.path.join(OUT_DIR, 'content/')
LOCAL_DIR = 'taverns/'

NAME_GEN_FUNCTIONS = {
  'adj_noun': name_gen.name_gen_adj_noun,
  'petname': ng.name_gen.name_gen_petname,
}

def tavern_name(**kwargs):
  gen_arg = kwargs.get('name_gen', 'adj_noun')
  gen_func = NAME_GEN_FUNCTIONS.get(gen_arg, name_gen.name_gen_adj_noun)

  return gen_func(**kwargs)


def tavern_quest(**kwargs):
  quests_file = kwargs.get('quests', 'quests.txt')
  path = os.path.join(CONTENT_DIR, quests_file)

  with open(path, 'r') as fh:
    quests = fh.read()
  quests = quests.split('\n')

  return numpy.random.choice(quests)


def tavern(**kwargs):
  t = {}

  for f in FUNCTIONS.keys():
    func = FUNCTIONS[f]
    print(func)
    val = func(**kwargs)
    kwargs[f] = val
    t[f] = val
  return t

FUNCTIONS = {
  "name": tavern_name,
  "npcs": partial(plebs_module._plebs, number=random.randint(0,5)),
  "proprietor": partial(plebs_module._plebs, number=1),
  "quest": tavern_quest,
}


def _taverns(number: int=1, **kwargs):

  ts = []
  for _ in range(number):
    ts.append(tavern(**kwargs))

  return ts


@click.command()
@click.option('--generator', '-g', type=click.Choice(NAME_GEN_FUNCTIONS.keys()),
  default=list(NAME_GEN_FUNCTIONS.keys())[0],
  help="The name generator function to use")
@click.option('--number', '-n', type=int, default=1,
  help="The number of taverns to generate")
def taverns(generator, number):
  kwargs = {'name_gen': generator}
  taverns_list = []
  for _ in range(number):
    taverns_list.append(tavern(**kwargs))

  print(plebs_module.stringify(taverns_list))

if __name__ == '__main__':
  taverns(obj={})