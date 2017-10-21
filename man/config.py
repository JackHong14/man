import os

import configlib

class Config(configlib.Config):

    __config_path__ = os.path.join(os.path.dirname(__file__), 'config.json')

    fullname = ''
    email = ''
    github_username = ''
    pypi_username = ''

if __name__ == '__main__':
    configlib.update_config(Config)
