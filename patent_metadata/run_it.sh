#!/bin/bash

./create_patent_metadata.py 4
cat outData/*.csv > prdn_metadata.csv
rm inData/*.bz2