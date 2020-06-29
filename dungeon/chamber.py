import random

from enum import Enum
from typing import (
    List,
    Tuple,
    Union,
)

import util


DEFAULT_LXW = (20, 20)
DEFAULT_DIA = 40

class ChamberShape(object):

    values = util.get_yaml('yaml/starts.yaml', 'shapes')

    def __init__(self, value: str=None):
        if value is None or value not in self.values:
            self.type = self.values[0]
        else:
            self.type = value

class ChamberSizeType(Enum):
    LXW = 1
    DIA = 2

class ChamberSize(object):

    def __init__(self,
                 size_type: ChamberSizeType=ChamberSizeType.LXW,
                 value: Union[int, Tuple[int, int]]=DEFAULT_LXW):

        self.size_type = size_type
        if size_type == ChamberSizeType.LXW and type(value) != tuple:
            self.value = DEFAULT_LXW
        elif size_type == ChamberSizeType.DIA and type(value) != int:
            self.value = DEFAULT_DIA
        else:
            self.value = value

class ExitLocation(Enum):
    NORTH = 1
    SOUTH = 2
    EAST = 3
    WEST = 4

class ExitSize(Enum):
    TINY = 1
    SMALL = 2
    MEDIUM = 3
    LARGE = 4

class ExitType(Enum):
    DOOR = 1
    PASSAGE = 2
    SECRET = 3

class Exit(object):

    # lts -- location, type, size
    # locations: h,v (horizontal for north/south, vertical for east/west)
    # types: d,p,s
    # sizes: t,s,m,l
    strings = {
        'hdt': '.-',
        'hds': 'X-',
        'hdm': '><',
        'hdl': '/  \\',
        'hpt': 'o-',
        'hps': 'O-',
        'hpm': '()',
        'hpl': '(  )',
        'hst': '`-',
        'hss': '*-',
        'hsm': '**',
        'hsl': '****',
        'vdt': '.',
        'vds': 'x',
        'vdm': 'X',
        'vdl': '\\\n/',
        'vpt': 'o',
        'vps': 'O'
        'vpm'
        'vpl'
        'vst'
        'vss'
        'vsm'
        'vsl'

    }

    def __init__(self,
                 exit_type: ExitType=ExitType.PASSAGE,
                 exit_size: ExitSize=ExitSize.MEDIUM,
                 location: ExitLocation=random.choice(list(ExitLocation)),
                 out: bool=False):
        self.exit_type = exit_type
        self.exit_size = exit_size
        self.location = location
        self.out = out

class Chamber(object):

    # The default chamber is a square "starting area" with dungeon egress and a
    # single open passage into the dungeon

    def __init__(self,
                 shape: ChamberShape=None,
                 size: ChamberSize=None,
                 exits: List[Exit]=None):
        self.ident = util.global_count()
        self.shape = shape if shape is not None else ChamberShape()
        self.size = size if size is not None else ChamberSize()
        self.exits = exits if exits is not None else [Exit(out=True), Exit()]

    def exit_string(exit: Exit) -> str:
        ns = [ExitLocation.NORTH, ExitLocation.SOUTH]
        ew = [ExitLocation.EAST, ExitLocation.WEST]
        if exit.exit_type == ExitType.DOOR:
            if exit.location in ns:
                
        else:

    def render(self) -> str:
        if self.shape.type != 'circle':
            north_doors = [x for x in self.exits if x.location == ExitLocation.NORTH]
            
            return f'+----+\n|{self.ident}   |\n|    |\n+----+'

