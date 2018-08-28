# -*- coding: utf-8 -*-

import glob
import json
import os
import random
import sys
import src.xmlParser as xmlParser
from multiprocessing import Process


def split_seq(seq, num_processes):
    """
    Slices a list into number_of_processes pieces
    of roughly the same size
    """
    num_files = len(seq)
    if num_files < num_processes:
        num_processes = num_files
    size = num_processes
    newseq = []
    splitsize = 1.0 / size * num_files
    for i in range(size):
        newseq.append(seq[int(round(i * splitsize)):int(round((i + 1) * splitsize))])
    return newseq


# Start processing
number_of_processes = int(sys.argv[1])
pathToData = 'inData/'
pathToJSON = 'parse_GBD/'
files = glob.glob(os.path.join(pathToData, "*.zip"))
random.shuffle(files)  # Newer years have more granted patents
files_list = split_seq(files, number_of_processes)
if __name__ == '__main__':
    with open(pathToJSON + 'zip3_cities.json') as json_data:
        zips_dict = json.load(json_data)
    with open(pathToJSON + 'cityMisspellings.json') as json_data:
        cities_dict = json.load(json_data)
    with open(pathToJSON + 'inventors.json') as json_data:
        inventors_dict = json.load(json_data)
    procs = []
    for chunk in files_list:
        p = Process(target=xmlParser.assign_zip3, args=(chunk, zips_dict, cities_dict, inventors_dict,))
        procs.append(p)
        p.start()
