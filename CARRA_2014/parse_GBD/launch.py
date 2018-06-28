# -*- coding: utf-8 -*-

import xmlParser
import glob, json, os, random, sys
from multiprocessing import Process, Manager


NUMBER_OF_PROCESSES = int(sys.argv[1])
cw_dir = sys.argv[2]


def split_seq(seq, NUMBER_OF_PROCESSES):
    """
    Slices a list into number_of_processes pieces
    of roughly the same size
    """
    num_files = len(seq)
    if num_files < NUMBER_OF_PROCESSES:
        NUMBER_OF_PROCESSES = num_files
    size = NUMBER_OF_PROCESSES
    newseq = []
    splitsize = 1.0/size*num_files
    for i in range(size):
        newseq.append(seq[int(round(i*splitsize)):int(round((i+1)*splitsize))])
    return newseq


# Start processing
pathToData = 'inData/'
pathToJSON = 'parse_GBD/'
files = glob.glob(os.path.join(pathToData, "*.zip"))
random.shuffle(files) # Newer years have more granted patents
files_list = split_seq(files, NUMBER_OF_PROCESSES)
if __name__ == '__main__':
    manager = Manager()
    zips_dict = manager.dict()
    cities_dict = manager.dict()
    inventors_dict = manager.dict()
    with open(pathToJSON + 'zip3_cities.json') as json_data:
        zips_dict = json.load(json_data)
    with open(pathToJSON + 'cityMisspellings.json') as json_data:
        cities_dict = json.load(json_data)
    with open(pathToJSON + 'inventors.json') as json_data:
        inventors_dict = json.load(json_data)
    for chunk in files_list:
        p = Process(target=xmlParser.assign_zip3, args=(chunk, zips_dict, cities_dict, inventors_dict,))
        p.start()
