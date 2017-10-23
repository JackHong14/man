import re
import configlib


class Version:

    MAJOR = 0
    MINOR = 1
    PATCH = 2

    def __init__(self, major: int, minor: int, patch: int):
        self.version = [major, minor, patch]
        self.last_version = None
        self.need_revert = True

    def __str__(self):
        return '%d.%d.%d' % tuple(self.version)

    def vstr(self):
        return 'v' + str(self)

    def __setitem__(self, key, value):
        self.version[key] = value
        for importance in range(key + 1, 3):
            self.version[importance] = 0

    def __getitem__(self, item):
        return self.version[item]

    def __enter__(self):
        self.last_version = self.version[:]
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.need_revert:
           self.version = self.last_version
           self.last_version = None

        self.need_revert = True



class VersionType(configlib.ConfigType):

    name = 'version'

    def save(self, value: Version):
        return str(value)

    def is_valid(self, value):
        return isinstance(value, Version)

    def load(self, value: str):
        match = re.match('v?(\d+)\.(\d+)\.(\d+)', value)
        if match:
            return Version(int(match.group(1)), int(match.group(2)), int(match.group(3)))
        raise ValueError


class ManConfig(configlib.Config):
    """
    This configuration is used for each lib to describe it.
    """

    __config_path__ = './manconfig.json'  # always in the directory where invocated

    libname = ''
    description = ''
    fullname = ''
    email = ''
    github_username = ''
    pypi_username = ''
    version = Version(0, 0, 0)
    __version_type__ = VersionType()

    package_data = dict()
    __package_data_type__ = configlib.Python(dict)

    data_files = []
    __data_files_type__ = configlib.Python(list)

    packages = []
    __packages_type__ = configlib.Python(list)

    dependancies = []
    __dependancies_type__ = configlib.Python(list)
