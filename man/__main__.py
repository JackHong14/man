import os
import subprocess

import click
import sys

from . import config

DIR = os.path.abspath(os.path.dirname(__file__))
LIBTEMPLATE_DIR = os.path.join(DIR, 'libtemplate')


def copy_template(FORMATERS: config.Config):
    LIB_DIR = os.path.abspath(FORMATERS.libname)

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


# noinspection PyTypeChecker
def main():

    FORMATERS = config.Config()
    FORMATERS.libname = click.prompt('Name of your library')
    FORMATERS.description = click.prompt('Short description')
    FORMATERS.fullname = click.prompt('Full name', default=FORMATERS.fullname)
    FORMATERS.email = click.prompt('E-Mail', default=FORMATERS.email)
    FORMATERS.github_username = click.prompt("Github username", default=FORMATERS.github_username)
    FORMATERS.pypi_username = click.prompt('PyPi username', default=FORMATERS.pypi_username)
    FORMATERS.__save__()

    try:
        copy_template(FORMATERS)
    except Exception as e:
        print(repr(e))
        click.echo('Something went wrong.')
        if click.confirm('Do you want to delete the directory %s' % FORMATERS.libname):
            run('rm -rf %s' % FORMATERS.libname)
        return

    run('cd %s' % FORMATERS.libname, True)
    os.chdir(FORMATERS.libname)
    click.echo(os.path.abspath(os.curdir))

    # initialize man
    run('py man.py add pkg %s' % FORMATERS.libname)
    run('py man.py add pkg-data %s/version' % FORMATERS.libname)
    run('py man.py add file manconfig.*')

    # initilize git repo
    run('git init .')
    run('git add .')
    run('git commit -m "initial commit"')
    run("""curl -u '{github_username}' https://api.github.com/user/repos -d '{open}"name":"{libname}", "description": "{description}"{close}' """.format(**FORMATERS.__dict__, open='{', close='}'))
    run('git remote add origin https://github.com/{github_username}/{libname}'.format(**FORMATERS.__dict__))
    run('git push origin master')

    whats_next(FORMATERS)


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

def run(cmd, test=False):

    click.secho('$ ', fg='green', bold=1, nl=0)
    click.secho(cmd, fg='cyan', bold=1)

    if not test:
        process = subprocess.Popen(cmd)
        out, err = process.communicate()
        return process.returncode
    return 0


if __name__ == '__main__':
    main()
