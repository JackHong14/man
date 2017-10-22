import glob
import os

from setuptools import setup

VERSION_FILE = os.path.join(os.path.abspath(os.path.dirname(__file__)), '{libname}', 'version')


if __name__ == '__main__':

    try:
        with open('readme.rst') as f:
            long_description = f.read()
    except FileNotFoundError:
        long_description = 'Configuration for python made easy'

    import manconfig
    config = manconfig.Config()

    setup(
        name='{libname}',
        version=config.version,
        packages=config.packages,
        url='https://github.com/{github_username}/{libname}',
        license='MIT',
        author='{fullname}',
        author_email='{email}',
        description='{description}',
        long_description=long_description,
        install_requires=config.dependancies,
        package_data=config.package_data,
        data_files=[(dir, list(set(file for patern in pats for file in glob.glob(patern, recursive=True)))) for (dir, pats) in config.data_files]
    )
