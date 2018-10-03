# -*- coding: utf-8 -*-

import glob
import json
import os
import src.xml_parser as xml_parser
from multiprocessing import Process
from preprocessing.shared_python_code.utility_functons import split_seq

THIS_DIR = os.path.dirname(__file__)


# Start processing
def make_carra_files(xml_files, NUMBER_OF_PROCESSES, path_to_json):
    '''
    '''
    files = glob.glob(os.path.join(xml_files, "*.bz2"))
    files_list = split_seq(files, NUMBER_OF_PROCESSES)
    if __name__ == '__main__':
        with open(path_to_json + '/zip3_cities.json') as json_data:
            zips_dict = json.load(json_data)
        with open(path_to_json + '/cityMisspellings.json') as json_data:
            cities_dict = json.load(json_data)
        with open(path_to_json + '/inventors.json') as json_data:
            inventors_dict = json.load(json_data)
        procs = []
        for chunk in files_list:
            p = Process(
                target=xml_parser.assign_zip3,
                args=(chunk, path_to_json, zips_dict, cities_dict, inventors_dict,))
            procs.append(p)
            p.start()
