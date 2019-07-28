import re
import yaml


class Character(object):
    attributes = [
            'name',
            'hp',
            'tmp_hp',
            'conditions',
    ]

    def __init__(self, argsdict):
        for k, v in argsdict.items():
            setattr(self, k, v)
        for att in Character.attributes:
            if argsdict.get(att, None) is None:
                if att == 'tmp_hp' and argsdict.get('hp', None) is not None:
                    setattr(self, att, argsdict['hp'])
                else:
                    setattr(self, att, '')


class Game(object):
    red_heart = chr(0x1f493)
    yellow_heart = chr(0x1f49b)
    green_heart = chr(0x1f49a)
    hearts = [red_heart, yellow_heart, green_heart]
    bang = chr(0x1f535)

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
        self.make_pcs_status_list()

    def add_character(self, name):
        self.pcs[name] = {'name': name}
        self.pc_names.append(name)
        self.set_initiative(name, '0')

    def remove_character(self, name):
        if self.pcs.get(name, None) is not None:
            del self.pcs[name]
            del self.initiative[name]
            self.pc_names.remove(name)
            self.make_initiative_list()

    def defer_initiative(self):
        if len(self.initiative_list) < 2:
            return

        head_init_value = int(self.initiative_list[0].split()[0])
        next_init_value = int(self.initiative_list[1].split()[0])
        if head_init_value < next_init_value:
            return

        end_of_turn_index = 0
        while head_init_value >= next_init_value:
            end_of_turn_index += 1
            head_init_value = int(self.initiative_list[end_of_turn_index].split()[0])
            if end_of_turn_index+1 < len(self.initiative_list):
                next_init_value = int(self.initiative_list[end_of_turn_index+1].split()[0])
            else:
                next_init_value = 999

        start_next_index = end_of_turn_index + 1
        head_portion = self.initiative_list[1:start_next_index]
        tail_portion = []
        if start_next_index < len(self.initiative_list):
            tail_portion = self.initiative_list[start_next_index:]
        new_list = head_portion + [self.initiative_list[0]] + tail_portion
        self.initiative_list = new_list

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

    def make_pcs_status_list(self):
        # type: () -> List[Text]
        ret_list = []

        for name in self.pc_names:
            heart = Game.green_heart

            ch = self.pcs[name]
            hp = getattr(ch, 'hp')
            tmp_hp = getattr(ch, 'tmp_hp')
            frac = int(tmp_hp) // int(hp)
            frac_text = f'{tmp_hp}/{hp}'
            conditions = getattr(ch, 'conditions').split()

            if frac < 1:
                heart = Game.yellow_heart
            elif frac < (1//2):
                heart = Game.red_heart

            ret_list.append(f'Name: {name}')
            ret_list.append(f'  {heart} : {frac_text}')
            ret_list.append(f'  {Game.bang}:')
            for cond in conditions:
                ret_list.append(f'    {cond}')

        self.pcs_status_list = ret_list

    def update_hp(self, name, change, update_type):
        tmp_hp = int(self.pcs[name].tmp_hp)
        change_int = int(change)
        if update_type is None:
            self.pcs[name].tmp_hp = change
        elif update_type == '+':
            self.pcs[name].tmp_hp = str(tmp_hp + change_int)
        elif update_type == '-':
            self.pcs[name].tmp_hp = str(tmp_hp - change_int)
        else:
            return

        self.make_pcs_status_list()
