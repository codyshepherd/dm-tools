import requests

import game.game as game

def convert_name(func):
    def convert(*args):
        name = args[1]
        name = name.lower().replace(' ', '-')
        return name

    def wrapper(*args, **kwargs):
        name = convert(*args)
        new_args = (args[0], name)
        return func(*new_args, **kwargs)
    return wrapper

class Api(object):
    base_url = 'http://dnd5eapi.co/api/'

    def __init__(self):
        self.monster_cache = {}

    def get_monster(self, name: str) -> bool:
        if name in self.monster_cache:
            return True

        url = self.base_url + 'monsters/' + name + '/'
        response = requests.get(url)
        if response.status_code != 200:
            return False

        self.monster_cache[name] = response.json()
        return True

    @convert_name
    def monster_hp(self, name: str) -> int:
        success = self.get_monster(name)

        if not success:
            return 1
        return self.monster_cache[name].get('hit_points', 1)

    @convert_name
    def monster_resistances(self, name: str) -> str:
        monster = self.monster_cache[name]
        res = monster.get('damage_resistances', [])

        res_list = ''
        for r in res:
            res_list += game.Game.damage_types[r]

        return res_list

    @convert_name
    def monster_vulnerabilities(self, name: str) -> str:
        monster = self.monster_cache[name]
        vuln = monster.get('damage_vulnerabilities', [])

        vuln_list = ''
        for v in vuln:
            vuln_list += game.Game.damage_types[v]

        return vuln_list
   
    @convert_name
    def monster_immunities(self, name: str) -> str:
        # we don't expect to have this function called without first calling
        # get_monster so exception is fine here
        monster = self.monster_cache[name]
        dmg_imm = monster.get('damage_immunities', [])
        cond_imm = monster.get('condition_immunities', [])

        imm_list = []
        for imm in dmg_imm:
            imm_list.append(game.Game.damage_types[imm])
        for imm in cond_imm:
            imm_name = imm['name'].lower()
            imm_list.append(game.Game.condition_emoji[imm_name])

        return ''.join(imm_list)
