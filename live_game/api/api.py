import requests


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

    @convert_name
    def get_monster(self, name: str) -> bool:
        if name in self.monster_cache:
            return True

        url = self.base_url + 'monsters/' + name + '/'
        try:
            response = requests.get(url)
        except requests.exceptions.ConnectionError:
            return False
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
    def monster_init_bonus(self, name: str) -> int:
        import live_game.game.game as game
        monster = self.monster_cache.get(name, None)
        if monster is None:
            return 0
        dex = monster.get('dexterity', 10)
        init_b = game.Rules.ability_score_modifiers.get(dex, 0)
        return init_b

    @convert_name
    def monster_resistances(self, name: str) -> str:
        import live_game.game.game as game
        monster = self.monster_cache.get(name, None)
        if monster is None:
            return ''
        res = monster.get('damage_resistances', [])

        res_list = ''
        for r in res:
            res_list += game.Game.damage_types[r]
            if r != res[-1]:
                res_list += ' '

        return res_list

    @convert_name
    def monster_vulnerabilities(self, name: str) -> str:
        import live_game.game.game as game
        monster = self.monster_cache.get(name, None)
        if monster is None:
            return ''
        vuln = monster.get('damage_vulnerabilities', [])

        vuln_list = ''
        for v in vuln:
            vuln_list += game.Game.damage_types[v]
            if v != vuln[-1]:
                vuln_list += ' '

        return vuln_list

    @convert_name
    def monster_immunities(self, name: str) -> str:
        import live_game.game.game as game
        monster = self.monster_cache.get(name, None)
        if monster is None:
            return ''
        dmg_imm = monster.get('damage_immunities', [])
        cond_imm = monster.get('condition_immunities', [])

        imm_list = []
        for imm in dmg_imm:
            imm_list.append(game.Game.damage_types[imm])
            if imm != dmg_imm[-1] or len(cond_imm) > 0:
                imm_list.append(' ')
        for imm in cond_imm:
            imm_name = imm['name'].lower()
            imm_list.append(game.Game.condition_emoji[imm_name])
            if imm != cond_imm[-1]:
                imm_list.append(' ')

        return ''.join(imm_list)
