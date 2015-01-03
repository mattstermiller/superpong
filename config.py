import re

_reSetting = re.compile(r'(\w+)=(.*)', re.IGNORECASE)


def load(filePath: str) -> dict:
    settings = {}
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
        for setting in settings.items():
            file.write('{0}={1}\n'.format(setting[0], repr(setting[1])))
