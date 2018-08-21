#!/bin/bash

# The get_uspto_data.sh files should be executed independently and
# then verified that all of the files were downloaded correctly.

# create the 1976-2001 XML files
cd dat_to_xml
./run_it.sh
# clean up the 2002 and later XML files and gather together the
# information needed for city misspellings, etc
cd ../xml_rewrite
./run_it.sh & PIDVAL=$!
cd ../
python -m create_GBD_metadata & PIDMETA=$!
wait $PIDVAL
wait $PIDMETA
# move data around
cp dat_to_xml/xml_files/*.bz2 for_carra/inData
cp xml_rewrite/rewriter/original_xml_files/*.bz2 for_carra/inData
cp create_GBD_metadata/*.json for_carra/parse_GBD/
mv create_GBD_metadata/*.json ./
# get the files ready to go to CARRA
# cd for_carra
# ./run_it.sh
# rm messages
# cd ../
# get together some basic information for each patent
cp dat_to_xml/xml_files/*.bz2 patent_metadata/inData
cp xml_rewrite/rewriter/original_xml_files/*.bz2 patent_metadata/inData
cd patent_metadata
./run_it.sh
cd ../
mv patent_metadata/prdn_metadata.csv ./
