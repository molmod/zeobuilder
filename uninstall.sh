#! /bin/sh
# This is a very simplistic uninstall scipt. Use with care!

if [ -z $1 ] && [ "$1" = "--system" ]; then
  rm -v /usr/bin/zeobuilder
  rm -vr /usr/share/zeobuilder
  rm -vr /usr/lib/python*/site-packages/zeobuilder
else
  rm -v $HOME/bin/zeobuilder
  rm -vr $HOME/share/zeobuilder
  rm -vr $HOME/lib/zeobuilder
fi
