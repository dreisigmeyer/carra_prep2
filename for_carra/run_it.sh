#!/bin/bash

NUM_PY_THREADS=4
python -m parse_GBD $NUM_PY_THREADS
rm parse_GBD/*.json
rm inData/*.zip