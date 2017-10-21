import glob
import os
import subprocess
import sys

import click
import configlib
import pypandoc

from setup import get_version, save_version

TYPES = ['major', 'minor', 'patch']
TEST = False


class Config(configlib.Config):
    __config_path__ = os.path.join(os.path.dirname(__file__), 'config.json')

    libname = ''
    github_username = ''
    fullname = ''
    email = ''
    pypi_username = ''

    package_data = dict()
    __package_data_type__ = configlib.Python(dict)

    data_files = []
    __data_files_type__ = configlib.Python(list)

    packages = []
    __packages_type__ = configlib.Python(list)

    dependancies = []
    __dependancies_type__ = configlib.Python(list)


CONFIG = Config()


def copy_template(FORMATERS: Config, dir):
    DIR = os.path.abspath(os.path.dirname(__file__))
    LIBTEMPLATE_DIR = os.path.join(DIR, 'libtemplate')
    LIB_DIR = os.path.abspath(os.path.join(dir, FORMATERS.libname))

    # copy all the lib template formating with the given data
    for directory, subdirs, files in os.walk(LIBTEMPLATE_DIR):

        dest_directory = directory[len(LIBTEMPLATE_DIR) + 1:].format(**FORMATERS.__dict__)
        dest_directory = os.path.join(LIB_DIR, dest_directory)

        click.secho('Creating directory %s' % dest_directory, fg='yellow')
        os.mkdir(dest_directory)

        for file in files:
            template_name = os.path.join(directory, file)
            out_name = os.path.join(dest_directory, file)

            click.echo('Creating file      %s' % out_name)
            with open(template_name) as f:
                text = f.read()

            try:
                text = text.format(**FORMATERS.__dict__)
            except Exception as e:
                print(directory, file)
                print(FORMATERS.__dict__)
                print(e, e.args, e.__traceback__, file=sys.stderr)
                raise

            with open(out_name, 'w') as f:
                f.write(text)


def whats_next(FORMATERS):
    import functools
    s = click.style
    code = functools.partial(s, fg='green')
    link = functools.partial(s, fg='yellow', underline=True)
    bullet = lambda i: '    ' * i + '- '

    click.echo('\n' * 2)

    text = [
        s("You are almost done !", fg='cyan', bold=True),
        '',
        'Here are the few steps that you still need to do:',
        bullet(1) + 'Add your encrypted password for pypi to .travis.yml. For that:',
            bullet(2) + 'Open ' + code('bash', fg='green'),
            bullet(2) + 'Run ' + code('travis encrypt --add deploy.password'),
        bullet(1) + 'Activate the continuous integration for this repo in Travis:',
            bullet(2) + 'Open ' + link('https://travis-ci.org/profile/%s' % FORMATERS.github_username),
            bullet(2) + 'Switch %s/%s to on' % (FORMATERS.github_username, FORMATERS.libname),
        bullet(1) + 'Write some code',
        bullet(1) + 'Add the dependancies:',
            bullet(2) + 'Run ' + code('man add dep pyconfiglib 1.*'),
            bullet(2) + 'Run ' + code('man add click'),
        bullet(1) + 'Create your first release:',
            bullet(2) + 'With ' + code('man release major'),
        bullet(1) + 'Read more about ' + code('man') + ' to manage your project after the creation:',
            bullet(2) + 'Run ' + code('man --help'),
            bullet(2) + 'Read ' + link('https://github.com/ddorn/man'),
        '',
        ''
    ]

    text[0] = text[0].center(len(max(text, key=len)))

    for line in text:
        click.echo(line)

    if click.confirm('Do you want to open travis in you browser ?', default=True):
        import webbrowser
        webbrowser.open('https://travis-ci.org/profile/%s' % FORMATERS.github_username)


def run(cmd: str, test=False):
    click.secho('$ ', fg='green', bold=1, nl=0)
    click.secho(cmd, fg='cyan', bold=1)

    # if cmd.startswith('man '):
    #     cmd = cmd.replace('man', 'python ' + __file__, 1)

    if not test:
        process = subprocess.Popen(cmd)
        out, err = process.communicate()
        return process.returncode
    return 0


@click.group()
@click.option('--test', is_flag=True)
@click.version_option(get_version())
def man(test):
    global TEST
    TEST = test


@man.command()
@click.argument('importance', type=click.Choice(TYPES))
@click.argument('message', nargs=-1)
@click.option('--test', is_flag=True)
def release(importance, message, test):
    """Deploy a project: update version, add tag, and push."""

    global TEST
    TEST = TEST or test

    # read and parsing the version
    version = get_version()
    click.secho('Current version: %s' % version, fg='green')
    version = list(map(int, version.split('.')))
    last_version = version[:]

    def revert_version():
        save_version(*last_version)
        click.secho('Version reverted to %s' % get_version(), fg='yellow')

    importance = TYPES.index(importance)
    # we increase major/minor/path as chosen
    version[importance] += 1
    # en reset the ones after
    for i in range(importance + 1, 3):
        version[i] = 0

    # save the version
    save_version(*version)

    # converting the readme in markdown to the one in rst
    try:
        rst = pypandoc.convert_file('readme.md', 'rst')
    except OSError:
        pypandoc.download_pandoc()
        rst = pypandoc.convert_file('readme.md', 'rst')
    # pandoc put a lot of carriage return at the end, and we don't want them
    rst = rst.replace('\r', '')
    # save the converted readme
    with open('readme.rst', 'w') as f:
        f.write(rst)
    click.echo('Readme converted.')

    # uninstall the previous version because the test imports it :/
    run('pip uninstall %s --yes' % CONFIG.libname)

    # make sure it passes the tests
    if run('pytest') != 0:
        click.secho("The tests doesn't pass.", fg='red')
        revert_version()
        return

    # make sure I can install it
    if run('py setup.py install --user clean --all') != 0:
        click.secho('Failed to install the updated library.', fg='red')
        revert_version()
        return

    version = get_version()

    # default message if nothing was provided
    message = ' '.join(message) if message else 'Release of version %s' % version

    # we need to commit and push the change of the version number before everything
    # if we don't, travis will not have the right version and will fail to deploy

    run('git commit -a -m "changing version number"'.format(message=message), test)
    run('git push origin', test)

    if click.confirm('Are you sure you want to create a new release (v%s)?' % version):
        # creating a realase with the new version
        run('git tag v%s -a -m "%s"' % (version, message), test)
        run('git push origin --tags', test)

        click.secho('Version changed to ' + version, fg='green')
    else:
        revert_version()
        return

    if test:
        # We do not want to increase the version number at each test
        revert_version()


@man.command()
@click.argument('dir', default='.')
def new_lib(dir):
    CONFIG.libname = click.prompt('Name of your library')
    CONFIG.description = click.prompt('Short description')
    CONFIG.fullname = click.prompt('Full name', default=CONFIG.fullname)
    CONFIG.email = click.prompt('E-Mail', default=CONFIG.email)
    CONFIG.github_username = click.prompt("Github username", default=CONFIG.github_username)
    CONFIG.pypi_username = click.prompt('PyPi username', default=CONFIG.pypi_username)
    CONFIG.__save__()

    try:
        copy_template(CONFIG, dir)
    except Exception as e:
        print(repr(e))
        click.echo('Something went wrong.')
        if click.confirm('Do you want to delete the directory %s' % CONFIG.libname):
            run('rm -rf %s' % CONFIG.libname)
        return

    LIB_DIR = os.path.abspath(os.path.join(dir, CONFIG.libname))
    run('cd %s' % CONFIG.libname, True)
    os.chdir(LIB_DIR)
    click.echo(os.path.abspath(os.curdir))

    # initialize man
    run('py man.py add pkg %s' % CONFIG.libname)
    run('py man.py add pkg-data %s/version' % CONFIG.libname)
    run('py man.py add file manconfig.*')

    # initilize git repo
    run('git init .')
    run('git add .')
    run('git commit -m "initial commit"')
    run(
        """curl -u '{github_username}' https://api.github.com/user/repos -d '{open}"name":"{libname}", "description": "{description}"{close}' """.format(
            **CONFIG.__dict__, open='{', close='}'))
    run('git remote add origin https://github.com/{github_username}/{libname}'.format(**CONFIG.__dict__))
    run('git push origin master')

    whats_next(CONFIG)


def staticmethod(func):
    return func


class MyCLI(click.MultiCommand):
    aliases = {
        'file': ['file', 'f'],
        'pkgdata': ['pkg-data', 'pkgdata', 'data', 'pd'],
        'pkg': ['pkg', 'package'],
        'dependancy': ['dependancy', 'dep']
    }

    def list_commands(self, ctx):
        return sorted([aliases[0] for aliases in self.aliases.values()])

    def get_command(self, ctx, name):
        for cmd_name, aliases in self.aliases.items():
            if name in aliases:
                return getattr(self, cmd_name)


class AddCli(MyCLI):
    @click.command()
    @click.argument('lib')
    @click.argument('version', default='')
    @staticmethod
    def dependancy(lib, version):
        import importlib
        try:
            modul = importlib.import_module(lib)
        except ModuleNotFoundError:
            click.secho('The library %s does not exist or is not installed.' % lib, fg='red')
            return

        if not version:
            ver = modul.__version__
            click.echo('The current version of %s is %s' % (lib, click.style(ver, fg='green')))

            default = 'Not specified'
            version = click.prompt('Version', default=default)
            version = '' if version == default else version

        if version and not version.startswith(('==', '>', '<', '!=')):  # ✓
            version = '==' + version

        dep = '%s%s' % (lib, version)

        if dep in CONFIG.dependancies:
            click.secho('%s is already in the dependancies' % dep, fg='red')  # ✓
            return

        CONFIG.dependancies.append(dep)
        with open('requirements.txt', 'a') as f:
            f.write(dep)
        click.secho('Added dependancy %s' % dep, fg='green')

    @click.command()
    @click.argument('patern')
    @staticmethod
    def file(patern):
        """
        Add a non code file to the data_files of setup.py.
        You can provide a glob patern and all the matchnig files will be added.
        """

        filenames = glob.glob(patern)

        if not filenames:
            click.secho('Not matching files for patern "%s".' % patern, fg='red')
            return

        for filename in filenames:
            filename = os.path.relpath(filename, os.path.dirname(__file__))
            directory = os.path.relpath(os.path.dirname(filename) or '.', os.path.dirname(__file__))
            directory = '' if directory == '.' else directory

            # it seems that package_data doesn't work for files inside packages, so we check if this file is in a pkg
            for pkg in CONFIG.packages:
                if directory.startswith(pkg):
                    # If it is, ask if we use pkg insead
                    click.echo('This file is included in the package ' + click.style(pkg, fg='yellow') + '.')
                    if click.confirm('Do you want to use ' + click.style('add pgk-data', fg='yellow') + ' instead ?'):
                        run('man add pkg-data "%s" "%s"' % (pkg, os.path.relpath(filename, pkg)))
                    else:
                        click.secho('The file "%s" was not included' % filename, fg='red')
                    break
            else:
                # we add the file if it wasn't in a pkg
                for i, (direc, files) in enumerate(CONFIG.data_files):
                    if direc == directory:
                        if filename not in files:
                            files.append(filename)
                            click.secho('Added "%s" in "%s".' % (filename, directory), fg='green')
                        else:
                            click.secho('The file "%s" was already included in "%s".' % (filename, directory),
                                        fg='yellow')
                        break
                else:
                    CONFIG.data_files.append((directory, [filename]))
                    click.secho('Added "%s" in "%s".' % (filename, directory), fg='green')

    @click.command()
    @click.argument('patern')
    @staticmethod
    def pkgdata(patern):

        # try to find which package it's in. We start we the longest names in case
        # it is in a sub package, we want to add it in the subpackage
        # I don't really know if it matters but well
        for package in sorted(CONFIG.packages, key=len, reverse=True):
            if patern.startswith(package):
                break
        else:
            click.secho("This file doesn't seems to be included in a defined package.")
            if click.prompt('Do you want to add it as a regular file ?', default=True):
                run('man add file %s' % patern)
            return

        patern = patern[len(package) + 1:]  # remove the package
        pkg_data = CONFIG.package_data
        if package in pkg_data:
            if patern in pkg_data[package]:
                click.secho('The patern "%s" was already included in the package "%s".' % (patern, package),
                            fg='yellow')
                return
            pkg_data[package].append(patern)
        else:
            pkg_data[package] = [patern]

        click.secho('Added patern "%s" in package "%s".' % (patern, package), fg='green')

    @click.command()
    @click.argument('pkg-dir')
    @staticmethod
    def pkg(pkg_dir: str):
        """
        Registers a package.

        A package is somthing people will be import by doing `import mypackage` or
        `import mypackage.mysubpackage`. They must have a __init__.py file.

        Examples:

            man add pkg mypackage

            man add pkg mypackage/mysubpackage
        """

        pkg_dir = pkg_dir.replace('\\', '/')
        parts = [part for part in pkg_dir.split('/') if part]  # thus removing thinks like final slash...
        pkg_name = '.'.join(parts)

        if pkg_name in CONFIG.packages:
            click.secho('The package %s is already in the packages list.' % pkg_dir, fg='yellow')
            return

        if not all(part.isidentifier() for part in parts):
            click.secho('The name "%s" is not a valid package name or path.' % pkg_dir, fg='red')
            return

        new_pkg = False
        if not os.path.isdir(pkg_dir):  # dir + exists
            click.secho('It seems there is no directory matching your package path', fg='yellow')
            if not click.confirm('Do you want to create the package %s ?' % pkg_dir, default=True):
                return
            # creating dir
            os.makedirs(pkg_dir, exist_ok=True)
            click.secho('Package created !', fg='green')
            new_pkg = True

        if new_pkg or not os.path.exists(os.path.join(pkg_dir, '__init__.py')):
            if not new_pkg:
                click.secho('The package is missing an __init__.py.', fg='yellow')
            if new_pkg or click.confirm('Do you want to add one ?', default=True):
                # creating __init__.py
                with open(os.path.join(pkg_dir, '__init__.py'), 'w') as f:
                    f.write('"""\nPackage %s\n"""' % pkg_name)
                click.secho('Added __init__.py in %s' % pkg_dir, fg='green')

        CONFIG.packages.append(pkg_name)
        click.secho('The package %s was added to the package list.' % pkg_name, fg='green')


class RemoveCLI(MyCLI):
    ...


@man.command(cls=AddCli)
def add():
    """Add something to your project."""


@man.command(cls=RemoveCLI)
def remove():
    """Remove something from your project."""


if __name__ == '__main__':
    with CONFIG:
        man()