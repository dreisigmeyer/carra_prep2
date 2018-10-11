# -*- coding: utf-8 -*-

import glob
import json
import os
import preprocessing.carra_files.src.xml_parser as xml_parser
from multiprocessing import Process
from preprocessing.shared_python_code.utility_functons import split_seq

THIS_DIR = os.path.dirname(__file__)


# Start processing
def make_carra_files(xml_files, NUMBER_OF_PROCESSES, path_to_json):
    '''
    '''
    files = glob.glob(os.path.join(xml_files, "*.bz2"))
    files_list = split_seq(files, NUMBER_OF_PROCESSES)
    with open(path_to_json + '/city_state_to_zip3.json') as json_data:
        zips_dict = json.load(json_data)
    with open(path_to_json + '/city_misspellings.json') as json_data:
        cities_dict = json.load(json_data)
    with open(path_to_json + '/inventors.json') as json_data:
        inventors_dict = json.load(json_data)
    close_city_spellings = '/close_city_spellings.json'
    procs = []
    for chunk in files_list:
        p = Process(
            target=xml_parser.assign_zip3,
            args=(chunk, path_to_json, close_city_spellings, zips_dict, cities_dict, inventors_dict,))
        procs.append(p)
        p.start()
