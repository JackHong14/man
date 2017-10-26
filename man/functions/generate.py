try:
    from manconfig import ManConfig
except ModuleNotFoundError:
    from man.manconfig import ManConfig


def manifest(config: ManConfig):
    """Creates a MANIFEST.in that includes the packages includes in the config."""
    # we cont want the precompiled flags
    manif = [
        '# THIS FILE IS AUTOMATICALLY GENERATED. IT IS POINTLESS TO MODIFY IT',
        '',
        'global-exclude *.py[co]'
    ]

    # we includ all packages and everything under them
    for package in config.packages:
        manif.append('graft %s' % package)

    with open('MANIFEST.in', 'w') as f:
        f.write('\n'.join(manif))

    return '\n'.join(manif)

def setup(config: ManConfig):
    """
    Generates the setup.py with the informations in the config.

    The long_description is read from a file called `readme.rst` accessible in the curentdir.
    This saves the setup in a files called `setup.py` and returns it too
    """

    # an empty dict causes the build to crash
    scripts = f'scripts=dict(console_scripts={config.scripts}),' if config.scripts else ''

    setup = f"""# THIS FILE IS AUTOMATICALLY GENERATED. IT IS POINTLESS TO MODIFY IT

from setuptools import setup

try:
    with open('readme.rst') as f:
        long_description = f.read()
except FileNotFoundError:
    long_description = '{config.description}' 

setup(
    name='{config.libname}',
    version='{config.version}',
    packages={config.packages},
    url='https://github.com/{config.github_username}/{config.libname}',
    license='MIT',
    author='{config.fullname}',
    author_email='{config.email}',
    description='{config.description}',
    long_description=long_description,
    install_requires={config.dependancies},
    include_package_data=True,
    {scripts}
    keywords='{config.keywords}'
)
"""
    # data_files=[(dir, list(set(file for patern in pats for file in glob.glob(patern, recursive=True)))) for (dir, pats) in config.data_files],

    with open('setup.py', 'w') as f:
        f.write(setup)

    return setup

def requirements(config: ManConfig):
    """
    Generates the requirements from the given config.

    This saves them in requirements.txt and returns it.
    """

    req = ['# THIS FILE IS AUTOMATICALLY GENERATED. IT IS POINTLESS TO MODIFY IT', '']

    for r in config.dependancies:
        req.append(r)

    req = '\n'.join(req)

    with open('requirements.txt', 'w') as f:
        f.write(req)

    return req
