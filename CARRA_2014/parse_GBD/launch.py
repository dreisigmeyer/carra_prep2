# -*- coding: utf-8 -*-

import xmlParser
import glob, os, random, sys
from multiprocessing import Pool


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
files = glob.glob(os.path.join(pathToData, "*.zip"))
random.shuffle(files) # Newer years have more granted patents
files_list = split_seq(files, NUMBER_OF_PROCESSES)
if __name__ == '__main__':
    p = Pool(NUMBER_OF_PROCESSES)
    p.map(xmlParser.assign_zip3, files_list)
