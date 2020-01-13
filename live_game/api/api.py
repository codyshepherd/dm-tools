import requests

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

    def monster_hp(self, name: str) -> int:
        name = name.lower().replace(' ', '-')
        success = self.get_monster(name)

        if not success:
            return 1
        return self.monster_cache[name].get('hit_points', 1)
