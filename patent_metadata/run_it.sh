#!/bin/bash

if [[ $# -eq 0 ]] ; then
	NUM_PY_THREADS=1
elif [[ $# -eq 1 ]] ; then
	NUM_PY_THREADS=$1
else
	echo 'Wrong number of parameters passed to xml_rewrite: only NUM_PY_THREADS needed.'
    exit 1
fi

./create_patent_metadata.py $NUM_PY_THREADS
cat outData/*.csv > prdn_metadata.csv
rm inData/*.bz2