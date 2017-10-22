"""
This script updates the two copies of man.py based on the one in libtemplate
"""

from manconfig import Config

config = Config()
def copy(from_, to):
    with open(from_) as f:
        text = f.read()
    # text = text.format(**config.__dict__)
    with open(to, 'w') as f:
        f.write(text)

# The one to manage my package
copy('man/libtemplate/man.py', 'man.py')
# The one to install with the module
copy('man/libtemplate/man.py', 'man/man.py')
# copy('man/libtemplate/manconfig.py', 'man/manconfig.py'

print('Done!')
