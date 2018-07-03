#!/bin/bash

for YEAR in {2002..2017}
do
    `wget -q -r -l1 -nd -P ./python_validation/inData/ --no-parent -A '*_wk*.zip' "https://bulkdata.uspto.gov/data/patent/grant/redbook/bibliographic/$YEAR/"`
done

for YEAR in {1976..2001}
do
    `wget -q -r -l1 -nd -P ./GBD_1976_2001_dat_to_xml/inData/ --no-parent -A "$YEAR.zip" "https://bulkdata.uspto.gov/data/patent/grant/redbook/bibliographic/$YEAR/"`
done
