#!/bin/bash

./process_pre_2002GBD.py

for YEAR in {1976..2001}
do
    cat handCorrections/hand"$YEAR"0101_wk01.xml >> outData/abcd"$YEAR"0101_wk00.xml
done