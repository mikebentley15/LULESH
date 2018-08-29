#!/bin/bash

BISECT_FILE=auto-bisect.csv
WORKING_COPY=/tmp/working-auto-bisect-numbers.txt
BISECT_COPY=/tmp/auto-bisect-numbers.txt
TO_DELETE_NUMS=/tmp/nums-to-delete.txt
TO_DELETE_FILE=/tmp/executables-to-delete.txt

tail -n +2 $BISECT_FILE | awk -F, '{ print $2 }' | sort -u > $WORKING_COPY
touch $BISECT_COPY
comm -23 $WORKING_COPY $BISECT_COPY > $TO_DELETE_NUMS
if [ $(cat $TO_DELETE_NUMS | wc -l) -gt 0 ]; then
  find $(printf "bisect-%02d\n" $(cat $TO_DELETE_NUMS)) \
    -type f -executable \
    > $TO_DELETE_FILE
  rm -f $(printf "bisect-%02d/obj/*.o\n" $(cat $TO_DELETE_NUMS))
  rm -f \
    /tmp/file-should-not-exist \
    $(cat $TO_DELETE_FILE)
  echo deleted $(cat $TO_DELETE_FILE | wc -l) executables
else
  echo deleted 0 executables
fi

rm -f $TO_DELETE_FILE $TO_DELETE_NUMS
mv -f $WORKING_COPY $BISECT_COPY

echo

head -n 1 $BISECT_FILE
tail -n 5 $BISECT_FILE

echo

echo $(grep SymbolTuple $BISECT_FILE | wc -l) \
     of \
     $(grep lib,src,sym $BISECT_FILE | wc -l) \
     runs were detectable and found a symbol
echo
echo $(echo '100.0*'$(grep lib,src,sym auto-bisect.csv | wc -l)'/4376.0' | bc)% done

