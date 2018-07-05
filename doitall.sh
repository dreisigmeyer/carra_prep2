#!/bin/bash

source activate carra_prep
./get_uspto_data.sh
cd GBD_1976_2001_dat_to_xml
./runit.sh
cd ../python_validation
./runit.sh & PIDVAL=$!
cd ../
python -m create_GBD_metadata & PIDMETA=$!
wait $PIDVAL
wait $PIDMETA
cp create_GBD_metadata/*.json CARRA_2014/parse_GBD/
mv create_GBD_metadata/*.json ./
cd CARRA_2014
./run_it.sh
rm messages
cd ../patent_metadata
./run_it.sh
cd ../
mv patent_metadata/prdn_metadata.csv ./
