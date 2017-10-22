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

# The one to install with the module --> the one to manage my package
copy('man/man.py', 'man.py')

print('Done!')
