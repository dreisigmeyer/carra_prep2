#!/bin/bash

# The get_uspto_data.sh files should be executed independently and
# then verified that all of the files were downloaded correctly.

NUM_PY_THREADS=4
PATH_TO_JSON=`dirname $(readlink -f $0)`
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
# Create metadata files and files for CARRA
python -m preprocessing outputs/xml_output/xml_with_inventors $NUM_PY_THREADS $PATH_TO_JSON
# mv preprocessing/carra_files/out_data/*.csv outputs/for_carra
mv *.json outputs/json_output
mv prdn_metadata.csv outputs/csv_output/
