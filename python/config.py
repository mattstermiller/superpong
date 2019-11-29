import os
import re

_reSetting = re.compile(r'(\w+)=(.*)', re.IGNORECASE)


def load(filePath: str) -> dict:
    settings = {}
    if os.path.isfile(filePath):
        with open(filePath, 'r') as file:
            for line in file:
                match = _reSetting.match(line)
                if match:
                    name = match.group(1)
                    value = eval(match.group(2))
                    settings[name] = value
    return settings


def save(filePath: str, settings: dict):
    with open(filePath, 'w') as file:
        settings = list(settings.items())
        settings.sort()
        for setting in settings:
            file.write('{}={!r}\n'.format(*setting))


class Config:
    def __init__(self, fileName: str):
        self.fileName = fileName
        self.settings = {}
        self.subscriptions = {}

    def __getitem__(self, key):
        if key in self.settings:
            return self.settings[key]
        return None

    def __setitem__(self, key, value):
        self.settings[key] = value
        if key in self.subscriptions:
            for setter in self.subscriptions[key]:
                setter(value)

    def subscribe(self, key, setter):
        setter(self[key])
        if key not in self.subscriptions:
            self.subscriptions[key] = []
        self.subscriptions[key].append(setter)

    def load(self):
        self.settings.update(load(self.fileName))

    def save(self):
        save(self.fileName, self.settings)
