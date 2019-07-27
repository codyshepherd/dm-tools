import re
import yaml


class Character(object):

    def __init__(self, argsdict):
        for k, v in argsdict.items():
            setattr(self, k, v)


class Game(object):

    def __init__(self, **kwargs):
        self.pcs_yaml = kwargs.get('pcs_yaml')

        self.load_pcs()

        if self.pcs == {}:
            raise Exception("No characters found.")

    def load_pcs(self):
        self.initiative = {}
        self.pc_names = []
        self.pcs = {}
        with open(self.pcs_yaml, 'r') as fh:
            raw = yaml.load(fh, Loader=yaml.Loader)

        for item in raw:
            char = item['character']
            char_name = char['name']
            self.initiative[char_name] = '0'
            self.pc_names.append(char_name)
            self.pcs[char_name] = Character(char)

        self.make_initiative_list()

    def add_character(self, name):
        self.pcs[name] = {'name': name}
        self.pc_names.append(name)
        self.set_initiative(name, '0')

    def remove_character(self, name):
        if self.pcs.get(name, None) is not None:
            del self.pcs[name]
            self.pc_names.remove(name)
            self.make_initiative_list()

    def next_initiative(self):
        first = self.initiative_list[0]
        rest = self.initiative_list[1:]
        self.initiative_list = rest + [first]

    def sort_init_list(self):
        temp = sorted(self.initiative.keys(),
                      key=lambda x: int(self.initiative[x]),
                      reverse=True)
        self.initiative_list = ['{} {}'.format(self.initiative[k], k) for
                                k in temp]

    def make_initiative_list(self):
        self.initiative_list = [
            '{} {}'.format(self.initiative[name], name) for name in
            self.pc_names]

    def set_initiative(self, name_expr, value):
        for name in self.pc_names:
            if re.match(name_expr, name):
                self.initiative[name] = value

        self.make_initiative_list()

    @property
    def pcs_string(self):
        # type: () -> List[Text]
        lst = []
        for char in self.pcs:
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
