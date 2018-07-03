#!/bin/bash

cd inData
ls *.zip | xargs -n1 -i unzip -q {}
cd ../

./process_pre_2002GBD.py

for YEAR in {1976..2001}
do
    cat handCorrections/hand"$YEAR"0101_wk01.xml >> outData/abcd"$YEAR"0101_wk00.xml
done

cd outData
ls *.xml | xargs -n1 -i zip -q {}.zip {}
mv *.zip ../../python_validation/inData/
rm -f *.xml
cd ../inData
rm -f *.zip
rm -f *.dat
cd ../