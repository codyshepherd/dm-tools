'''
This is the module that stores and manages all of the game state for
a live-game session.
'''

import re
import yaml

import live_game.api.api as api
from string import digits
from typing import Dict, List


class Character(object):
    '''
    Functions and fields for instantiating character / combatant info
    for a live-game session
    '''
    attributes = [
            'name',
            'hp',
            'tmp_hp',
            'init_bonus',
            'conditions',
            'immunities',
            'resistances',
            'vulnerabilities',
    ]

    legend_attributes = [attributes[1]] + attributes[3:]

    def __init__(self, argsdict):
        # Set class attributes based on key value pairs passed in
        for k, v in argsdict.items():
            setattr(self, k, v)
        # Set defaults for specific attributes if not present in the argsdict
        for att in Character.attributes:
            if argsdict.get(att, None) is None:
                if att == 'tmp_hp' and argsdict.get('hp', None) is not None:
                    setattr(self, att, argsdict['hp'])
                elif att == 'tmp_hp' and getattr(self, 'hp', None) is not None:
                    setattr(self, att, self.hp)
                elif att in Character.attributes[1:3]:
                    hp = argsdict.get('hp', 1)
                    hp = hp if hp > 0 else 1
                    setattr(self, att, str(hp))
                elif att == 'init_bonus':
                    bonus = int(argsdict.get('init_bonus', 0))
                    setattr(self, att, bonus)
                else:
                    setattr(self, att, '')

    def edit_name(self, newname: str) -> None:
        '''
        Sets name attribute to argument

        :param newname: a string to which to set the character name

        :return: None
        '''
        setattr(self, 'name', newname)

    def set_init_bonus(self, bonus: int) -> None:
        '''
        Sets initiative bonus to value

        :param bonus: an integer value to which to set the character's
                      initiative bonus

        :return: None
        '''
        setattr(self, 'init_bonus', bonus)


class Game(object):
    '''
    Functions and fields for storing and managing all of the game state for
    a live-game session.

    Emoji indicators are defined in this class because the concepts they
    represent are implemented and stored as unicode strings, therefore
    their representation is also their implementation
    '''

    # Define unicode code points for each state category and value
    red_heart = chr(0x1f493)
    init = chr(0x1f300)
    yellow_heart = chr(0x1f49b)
    green_heart = chr(0x1f49a)
    skull = chr(0x1f480)
    hearts = [red_heart, yellow_heart, green_heart, skull]
    bang = chr(0x1f535)
    immunity = chr(0x26d4)
    resistance = chr(0x1f6d1)
    vulnerability = chr(0x1f494)

    attribute_icons = [red_heart, init, bang, immunity, resistance,
                       vulnerability]

    condition_emoji = {
        'blinded': chr(0x1f441),
        'charmed': chr(0x1f495),
        'deafened': chr(0x1f442),
        'fatigued': chr(0x27b0),
        'frightened': chr(0x1f3c3),
        'grappled': chr(0x270a),
        'incapacitated': chr(0x274c),
        'invisible': chr(0x1f440),
        'paralyzed': chr(0x26a1),
        'petrified': chr(0x1f48e),
        'poisoned': chr(0x1f92e),
        'prone': chr(0x1f938),
        'restrained': chr(0x1f517),
        'stunned': chr(0x1f4ab),
        'unconscious': chr(0x1f4a4),
        'exhaustion': chr(0x27bf),
        'inspiration': chr(0x2b50),
    }

    # Note that the keys in this dict are named as such so they can work nicely
    # with the fields in API calls via live-game.api
    damage_types = {
        'acid': chr(0x1f9ea),
        'bludgeoning': chr(0x1f528),
        'cold': chr(0x2744),
        'fire': chr(0x1f525),
        'force': chr(0x1f4a5),
        'lightning': chr(0x1f329),
        'necrotic': chr(0x2620),
        'piercing': chr(0x1f3f9),
        'poison': chr(0x1f922),
        'psychic': chr(0x1f9e0),
        'radiant': chr(0x1f31e),
        'slashing': chr(0x1f5e1),
        'thunder': chr(0x1f50a),
        "bludgeoning, piercing, and slashing damage from nonmagical weapons that aren't silvered": chr(0x1f6e0),    # noqa: E501
        "bludgeoning, piercing, and slashing from nonmagical weapons": chr(0x1f52a),                                # noqa: E501
        "bludgeoning, piercing, and slashing from nonmagical weapons that aren't silvered": chr(0x1f6e0),           # noqa: E501
    }

    def __init__(self, **kwargs):
        self.api = api.Api()        # The object for talking to the web API
        self.pcs_yaml = kwargs.get('pcs_yaml')  # the path for the save file

        self.initiative = {}        # type: Dict[str, str] # a dict storing player initiative scores # noqa: E501
        self.initiative_list = []   # type: List[str] # a list of strings for displaying the current state of the turn # noqa: E501
        self.pc_names = []          # type: List[str] # the names of all combatants # noqa: E501
        self.pcs = {}               # type: Dict[str, Character] # a dict of all current combatants # noqa: E501
        self.pcs_status_list = []   # type: List[str] # a list of strings for displaying the current status of all combatants # noqa: E501

        self.load_pcs()

    def add_character(self, name: str) -> None:
        '''
        Update game state to add a new combatant, and write to the save file

        :param name: the name of the combatant to add

        :return: None
        '''
        hp = self.api.monster_hp(name)
        imms = self.api.monster_immunities(name)
        init_b = self.api.monster_init_bonus(name)
        res = self.api.monster_resistances(name)
        vuln = self.api.monster_vulnerabilities(name)

        # Append a numeric value to the combatant's name if it is a repeat
        # of a combatant that already exists
        while name in self.pcs.keys():
            last_digit_string = ''.join(filter(str.isdigit, name))
            if len(last_digit_string) > 0:
                name = name.rstrip(digits)
                last_digit = int(last_digit_string)
                name = name + str(last_digit + 1)
            else:
                name = name + '1'

        character = Character({
            'name': name,
            'hp': hp,
            'immunities': imms,
            'init_bonus': init_b,
            'resistances': res,
            'vulnerabilities': vuln,
            'conditions': '',
        })

        self.pcs[name] = character

        self.pc_names.append(name)
        self.initiative[name] = 0
        self.update_initiative_list()
        self.make_pcs_status_list()
        self.write_state()

    def clear_init(self) -> None:
        '''
        Sets the active initiative score for all combatants to 0
        '''
        for char in self.pcs.keys():
            self.set_initiative(char, 0)
            self.sort_initiative_list()

    def defer_initiative(self) -> None:
        '''
        Moves the combatant whose turn it is to the end of the turn by taking
        the head of the initiative list and placing it just before the
        combatant with the highest initiative score.

        Has no effect if there is one or fewer combatants present.

        Has no effect if the combatant whose turn it is is already the last
        in the turn order
        '''
        if len(self.initiative_list) < 2:
            return

        head_init_value = int(self.initiative_list[0].split()[0])
        next_init_value = int(self.initiative_list[1].split()[0])
        if head_init_value < next_init_value:
            return

        end_of_turn_index = 0
        while head_init_value >= next_init_value:
            end_of_turn_index += 1
            head_init_value = int(self.initiative_list[end_of_turn_index].split()[0])  # noqa: E501
            if end_of_turn_index+1 < len(self.initiative_list):
                next_init_value = int(self.initiative_list[end_of_turn_index+1].split()[0])  # noqa: E501
            else:
                next_init_value = 999

        start_next_index = end_of_turn_index + 1
        head_portion = self.initiative_list[1:start_next_index]
        tail_portion = []
        if start_next_index < len(self.initiative_list):
            tail_portion = self.initiative_list[start_next_index:]
        new_list = head_portion + [self.initiative_list[0]] + tail_portion
        self.initiative_list = new_list

    def load_pcs(self) -> None:
        '''
        Read in saved game state from the pcs_yaml file
        '''
        with open(self.pcs_yaml, 'r') as fh:
            raw = yaml.load(fh, Loader=yaml.Loader)

        if raw is None:
            raw = ''

        for item in raw:
            char = item['character']
            char_name = char['name']
            self.initiative[char_name] = '0'
            self.pc_names.append(char_name)
            self.pcs[char_name] = Character(char)
            conds = char.get('conditions', '')
            self.pcs[char_name].conditions = conds

        self.sort_initiative_list()
        self.make_pcs_status_list()

    def make_pcs_status_list(self) -> None:
        '''
        Construct and update the game's combatant status list for display.

        This function sorts combatants according to Python's dict sorting
        logic. i.e. there may be no order to the sorting; to move a combatant
        to the top of the list, a follow-on call to promote_pc_in_status_list
        should be made.
        '''
        ret_list = []

        for name in self.pc_names:
            heart = Game.green_heart

            ch = self.pcs[name]
            hp = getattr(ch, 'hp')
            tmp_hp = getattr(ch, 'tmp_hp')
            frac = float(tmp_hp) / float(hp)
            frac_text = f'{tmp_hp}/{hp}'
            init_bonus = getattr(ch, 'init_bonus', '')
            conditions = getattr(ch, 'conditions', '')
            immunities = getattr(ch, 'immunities', '')
            resistances = getattr(ch, 'resistances', '')
            vulnerabilities = getattr(ch, 'vulnerabilities', '')

            if frac < 1.0 and frac >= 0.5:
                heart = Game.yellow_heart
            elif frac < 0.5 and frac != 0.0:
                heart = Game.red_heart
            elif frac == 0.0:
                heart = Game.skull

            ret_list.append(f'Name: {name}')
            ret_list.append(f'  {heart} : {frac_text}')
            ret_list.append(f'  {Game.init}: {init_bonus}')
            ret_list.append(f'  {Game.bang}: {conditions}')
            ret_list.append(f'  {Game.immunity}: {immunities}')
            ret_list.append(f'  {Game.resistance}: {resistances}')
            ret_list.append(f'  {Game.vulnerability}: {vulnerabilities}')

        self.pcs_status_list = ret_list

    def next_initiative(self) -> None:
        '''
        Move to the next combatant in turn order by moving HEAD to the tail
        of the list
        '''
        first = self.initiative_list[0]
        rest = self.initiative_list[1:]
        self.initiative_list = rest + [first]

    def promote_pc_in_status_list(self, name: str) -> None:
        '''
        Move a combatant by name to the top of the status list

        :param name: a string regex representing the name of the combatant
                     to be promoted
        :return: None
        '''
        chars_items = []
        remaining_items = []
        found = False
        for line in self.pcs_status_list:
            if re.search(rf'\b{name}\b', line) or \
               (found and 'Name' not in line):
                found = True
                chars_items.append(line)
            else:
                found = False
                remaining_items.append(line)

        self.pcs_status_list = chars_items + remaining_items

    def remove_character(self, name: str) -> None:
        '''
        Remove a combatant from the game state and write update to the save
        file

        :param name: a string representing the name of the combatant to remove
        :return: None
        '''
        if self.pcs.get(name, None) is not None:
            del self.pcs[name]
            del self.initiative[name]
            self.pc_names.remove(name)
            self.update_initiative_list()
            self.make_pcs_status_list()
            self.write_state()

    def remove_condition(self, name: str, cond: str) -> str:
        '''
        Remove a condition from a combatant's status

        :param name: a string representing the name of the combatant from which
                     to remove the condition
        :param cond: a single character string containing the unicode character
                     to remove
        :return: a string communicating success or failure, intended for the
                 UI Log
        '''
        for k, v in Game.condition_emoji.items():
            if v == cond:
                conditions = self.pcs[name].conditions
                conditions = ' '.join([c for c in conditions if (c != ' ' and c != cond)]).strip()  # noqa: E501
                self.pcs[name].conditions = conditions
                self.make_pcs_status_list()
                self.promote_pc_in_status_list(name)
                self.write_state()
                return k
        return f'{cond} not found'

    def set_condition(self, name: str, cond: str) -> str:
        '''
        Add a condition to a combatant's status.

        :param name: a string representing the name of the combatant to which
                     to add the condition
        :param cond: a string representing the (full) name of the condition
                     to add
        :return: a string communicating success or failure, intended for the
                 UI log
        '''
        cond = cond.lower()
        if cond not in Game.condition_emoji:
            return 'condition not found'
        if name not in self.pcs.keys():
            return f'{name} not found'
        emoji = Game.condition_emoji[cond]
        conds = self.pcs[name].conditions
        if emoji not in conds:
            conds = ' '.join([conds, emoji]).strip()
            self.pcs[name].conditions = conds
            self.make_pcs_status_list()
            self.promote_pc_in_status_list(name)
            self.write_state()
        return 'success'

    def set_init_bonus(self, name: str, value: int) -> str:
        '''
        Set the initiative bonus value for a combatant

        :param name: the name string for the combatant
        :param value: the integer value of the initiative bonus
        :return: a success/fail string for display in the log
        '''
        char = self.pcs.get(name, None)

        if char is None:
            return f'{name} not found'

        char.set_init_bonus(value)

        self.make_pcs_status_list()
        self.promote_pc_in_status_list(name)
        self.write_state()

        return f'{name} {value}'

    def set_initiative(self, name_expr: str, value: int) -> None:
        '''
        Set the initiative value, ignoring initiative bonus, for a combatant

        :param name_expr: a regex string for the combatant
        :param value: the integer value of the initiative score
        :return: None
        '''
        for name in self.pc_names:
            if re.match(name_expr, name):
                self.initiative[name] = str(value)

        self.update_initiative_list()

    def sort_initiative_list(self) -> None:
        '''
        Construct and update the game's initiative list for display in reverse
        sorted order.

        This function effectively re-sets a turn by re-sorting all combatants
        '''
        self.initiative_list = sorted([
            '{} {}'.format(self.initiative[name], name) for name in
            self.pc_names], key=lambda x: int(x.split(' ')[0]), reverse=True)

    def update_hp(self,
                  name: str,
                  change: int,
                  update_type: str,
                  target: str,
                  write_changes: bool
                  ) -> None:
        '''
        Update the hit points of a combatant. This function handles updates
        to the combatant's maximum hp as to their temporary hp.

        :param name: the name of the combatant
        :param change: an integer representing the value of the change to hp
        :param update_type: a string indicating the desired type of update;
                       should be one of ['+', '-', 'set'] to
                       indicate addition, subtraction, or setting of hp
        :param target: either 'max' or 'temp' indicating which hp value should
                       be adjusted
        :param write_changes: whether the changes should be written to the save
                       file or not
        :return: None
        '''

        tmp_hp = int(self.pcs[name].tmp_hp)

        if update_type == '-':
            change = change * -1

        if target == 'max':
            if update_type == 'set':
                self.pcs[name].hp = str(change)
                if tmp_hp > change:
                    self.pcs[name].tmp_hp = str(change)
            else:
                hp = int(self.pcs[name].hp)
                final = hp + change
                self.pcs[name].hp = str(final)
                if tmp_hp > final:
                    self.pcs[name].tmp_hp = str(final)
        else:
            if update_type == 'set':
                self.pcs[name].tmp_hp = str(change)
            else:
                self.pcs[name].tmp_hp = str(tmp_hp + change)

        self.make_pcs_status_list()
        self.promote_pc_in_status_list(name)

        if write_changes:
            self.write_state()

    def update_initiative_list(self):
        '''
        Add any recently-added combatants to the initiative list

        :return: None
        '''
        newlist = []
        added = []
        for item in self.initiative_list:
            name = ' '.join(item.split(' ')[1:])
            if name in self.pc_names:
                init = self.initiative[name]
                newlist.append(f'{init} {name}')
                added.append(name)

        for name in self.pc_names:
            if name not in added:
                newlist.append(f'0 {name}')

        self.initiative_list = newlist

    def write_state(self):
        '''
        Write game state to the save file.

        Does not include temp hp or initiative scores

        :return: None
        '''
        new = []
        for name in self.pcs.keys():
            entry = {}
            character = {}
            character['name'] = name
            character['hp'] = self.pcs[name].hp
            character['conditions'] = self.pcs[name].conditions
            character['immunities'] = self.pcs[name].immunities
            character['init_bonus'] = self.pcs[name].init_bonus
            character['resistances'] = self.pcs[name].resistances
            character['vulnerabilities'] = self.pcs[name].vulnerabilities
            entry['character'] = character
            new.append(entry)

        with open(self.pcs_yaml, 'w+') as fh:
            yaml.dump(new, fh)


class Rules(object):
    '''
    This class stores any 5e rules that might need to be referenced to
    compute game state
    '''

    ability_score_modifiers = {
        1: -5,
        2: -4,
        3: -4,
        4: -3,
        5: -3,
        6: -2,
        7: -2,
        8: -1,
        9: -1,
        10: 0,
        11: 0,
        12: 1,
        13: 1,
        14: 2,
        15: 2,
        16: 3,
        17: 3,
        18: 4,
        19: 4,
        20: 5,
        21: 5,
        22: 6,
        23: 6,
        24: 7,
        25: 7,
        26: 8,
        27: 8,
        28: 9,
        29: 9,
        30: 10,
    }
