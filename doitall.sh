#!/bin/bash

# The get_uspto_data.sh files should be executed independently and
# then verified that all of the files were downloaded correctly.

NUM_PY_THREADS=4
# create the 1976-2001 XML files
cd dat_to_xml
./run_it.sh $NUM_PY_THREADS
# clean up the 2002 and later XML files
cd ../xml_rewrite
./run_it.sh $NUM_PY_THREADS
# get the output xml files together
cd ../
mv dat_to_xml/xml_files/*.bz2  outputs/xml_output/xml_with_inventors/
mv xml_rewrite/rewriter/original_xml_files/*.bz2  outputs/xml_output/xml_with_inventors/
mv dat_to_xml/modified_xml_files/*.bz2  outputs/xml_output/xml_without_inventors/
mv xml_rewrite/rewriter/modified_xml_files/*.bz2  outputs/xml_output/xml_without_inventors/
python -m preprocessing outputs/xml_output/xml_with_inventors $NUM_PY_THREADS
# gather together the information needed for city misspellings, etc
# cd create_GBD_metadata
# ./run_it.sh ../outputs/xml_output/xml_with_inventors
# cd ../
# get the files ready to go to CARRA
# cd for_carra
# ./run_it.sh $NUM_PY_THREADS
# get together some basic information for each patent
# cd ../
# cd patent_metadata
# ./run_it.sh $NUM_PY_THREADS
# cd ../
# mv preprocessing/carra_files/out_data/*.csv outputs/for_carra
mv *.json outputs/json_output
mv preprocessing/patent_metadata/prdn_metadata.csv outputs/csv_output/
