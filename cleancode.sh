#!/bin/bash
echo Cleaning python code in \'`pwd`\' and subdirectories
for file in `find * | egrep '(\.py$)|(\.rst$)|(^scripts/)'`; do
  echo $file
  sed -i -e $'s/\t/    /' ${file}
  sed -i -e $'s/[ \t]\+$//' ${file}
done
exit 0
