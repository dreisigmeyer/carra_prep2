#!/bin/bash

for YEAR in {2002..2015}
do
    `wget -q -r -l1 --no-parent -A '*_wk*.zip' "https://bulkdata.uspto.gov/data/patent/grant/redbook/bibliographic/$YEAR/"`
done
