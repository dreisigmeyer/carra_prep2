#!/bin/bash

NUM_PY_THREADS=4
./create_patent_metadata.py $NUM_PY_THREADS
cat outData/*.csv > prdn_metadata.csv
rm inData/*.bz2