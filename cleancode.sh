for file in `find * | grep "\.py$"`; do
  echo ${file}
  if grep -I -m 1 $'	' ${file}; then
    echo Tabs found in file ${file}!!
    #exit 1
  fi
  sed -i -e $'s/	/    /' ${file}
  if egrep -I -m 1 $'[ 	]+$' ${file}; then
    echo Trailing whitespace found in file ${file}!!
    #exit 1
  fi
  sed -i -e $'s/[ \t]\+$//' ${file}
done
exit 0
