#! /bin/sh
# This is a very simplistic install scipt. Use with care!

if [ -z $1 ] && [ "$1" = "--system" ]; then
  ./uninstall.sh --system
  python setup.py install
  ./cleanfiles.sh
else
  ./uninstall.sh
  python setup.py install --home=$HOME
  ./cleanfiles.sh
  echo "Don't forget to add 'export PYTHONPATH=$HOME' to your .bashrc file."
fi
