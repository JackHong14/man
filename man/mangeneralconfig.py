import configlib

class GeneralConfig(configlib.Config):
    """
    This configuration is used when creating new libs with `man create-lib`
    It help to provides defaults.
    """

    github_username = ''
    fullname = ''
    email = ''
    pypi_username = ''
