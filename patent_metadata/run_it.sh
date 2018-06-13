#!/bin/bash

./create_patent_metadata.py 5
cat outData/*.csv > prdn_metadata.csv
