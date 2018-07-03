#!/bin/bash

python parse_GBD/setup.py build_ext --inplace
rm -rf build/
python parse_GBD >> messages
rm parse_GBD/*.json
rm inData/*.zip