#!/bin/bash

cd dat_to_xml
./get_uspto_data.sh
./run_it.sh
cd ../xml_rewrite
./get_uspto_data.sh
./run_it.sh & PIDVAL=$!
cd ../
python -m create_GBD_metadata & PIDMETA=$!
wait $PIDVAL
wait $PIDMETA
# cp dat_to_xml/xml_files/*.bz2 for_carra/inData
# cp xml_rewrite/rewriter/original_xml_files/*.bz2 for_carra/inData
# cp create_GBD_metadata/*.json for_carra/parse_GBD/
mv create_GBD_metadata/*.json ./
# cd for_carra
# ./run_it.sh
# rm messages
# cd ../
cp dat_to_xml/xml_files/*.bz2 patent_metadata/inData
cp xml_rewrite/rewriter/patent_metadata/*.bz2 for_carra/inData
cd patent_metadata
./run_it.sh
cd ../
mv patent_metadata/prdn_metadata.csv ./
