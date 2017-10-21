import configlib

class Config(configlib.Config):

    __config_path__ = 'manconfig.json'

    libname = ''
    github_username = ''

    package_data = dict()
    __package_data_type__ = configlib.Python(dict)

    data_files = []
    __data_files_type__ = configlib.Python(list)

    packages = []
    __packages_type__ = configlib.Python(list)

    dependancies = []
    __dependancies_type__ = configlib.Python(list)


if __name__ == '__main__':
    c = Config()
    configlib.update_config(Config)
