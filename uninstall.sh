#!/bin/bash
# This is a very simplistic uninstall scipt. Use with care!

if [ -n $1 ] && [ "$1" = "--system" ]; then
  rm -v /usr/bin/zeobuilder
  rm -vr /usr/share/zeobuilder
  rm -vr /usr/lib/python*/site-packages/zeobuilder
else
  if [ -z $PYTHONPATH ]; then
    echo 'WARNING: $PYTHONPATH is not defined, defaulting to \$HOME/lib/python'
    PYTHONPATH=$HOME/lib/python
  fi
  rm -v $HOME/bin/zeobuilder
  rm -vr $HOME/share/zeobuilder
  rm -vr $PYTHONPATH/zeobuilder
fi
