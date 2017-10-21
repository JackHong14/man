:: This script updates the two copies of man.py based on the one in libtemplate
@echo off
:: The one to manage my package
cp man/libtemplate/man.py man.py
:: The one to install with the module
cp man/libtemplate/man.py man/man.py
echo Done!
