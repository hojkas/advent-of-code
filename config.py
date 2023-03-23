import json


class Config:
    def __init__(self):
        with open('config.json', 'r') as f:
            self._config_json = json.load(f)

    def __getitem__(self, key):
        return self._config_json[key]

    def has_key(self, k):
        return k in self._config_json


