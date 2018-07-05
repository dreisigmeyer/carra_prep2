#!/bin/bash

for YEAR in {2002..2017}
do
    COUNT=`ls python_validation/inData/*pgb"$YEAR"*_wk*.zip 2> /dev/null | wc -l`
    while [ "$COUNT" -lt 52 ]; do
        `wget -q -r -l1 -nd -P ./python_validation/inData/ --no-parent -A '*_wk*.zip' "https://bulkdata.uspto.gov/data/patent/grant/redbook/bibliographic/$YEAR/"`
        COUNT=`ls python_validation/inData/*pgb"$YEAR"*_wk*.zip 2> /dev/null | wc -l`
    done
done

for YEAR in {1976..2001}
do
    COUNT=`ls GBD_1976_2001_dat_to_xml/inData/"$YEAR".zip 2> /dev/null | wc -l`
    while [ "$COUNT" -lt 1 ]; do
        `wget -q -r -l1 -nd -P ./GBD_1976_2001_dat_to_xml/inData/ --no-parent -A "$YEAR.zip" "https://bulkdata.uspto.gov/data/patent/grant/redbook/bibliographic/$YEAR/"`
        COUNT=`ls GBD_1976_2001_dat_to_xml/inData/"$YEAR".zip 2> /dev/null | wc -l`
    done
done
