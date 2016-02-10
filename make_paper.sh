#!/bin/bash

export LC_ALL=en_US.UTF-8
export LANG=en_US.UTF-8

DIR=$1

if [[ ! -d $DIR ]]; then
  echo "Usage: make_paper.sh source_dir"
  exit -1
fi

python2.7 publisher/build_paper.py $DIR
if [ "$?" -ne "0" ]; then
    echo "Error building paper $DIR. Aborting."
    exit 1
fi

#cd $OUTDIR
#$TEX2PDF > /dev/null && $TEX2PDF | (python2.7 $WD/publisher/page_count.py)
