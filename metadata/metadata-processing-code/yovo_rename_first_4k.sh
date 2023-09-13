#!/bin/bash

cd $1
for f in *.wav; do tmp=`echo $f | awk -F. '{printf "%05d.%s\n", $1, $2}'`; mv "$f" "$tmp"; done;
cd -