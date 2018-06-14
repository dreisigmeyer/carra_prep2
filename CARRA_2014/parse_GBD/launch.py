# -*- coding: utf-8 -*-

# import xmlParser, xmltodict
# from lxml import etree
import glob, json, os, random, sys
from functools import partial
from multiprocessing import Pool, Manager


NUMBER_OF_PROCESSES = int(sys.argv[1])
cw_dir = sys.argv[2]

# # The following three functions convert the XML data into Python dictionaries
# # This is needed so the data can be shared across processes without each process
# # having its own copy
# def get_zips():
#     with open('./parse_GBD/ASCII_zip3_cities.xml') as f:
#         zips = xmltodict.parse(f.read())
#     zip_dict = dict()
#     for state in zips['states']['state']:
#         abbrev = state['@abbrev']
#         zip_dict[abbrev] = dict()
#         for city in state['zip3']:
#             cty = city['@city']
#             zip = city['#text']
#             if cty in zip_dict[abbrev]:
#                 zip_dict[abbrev][cty].append(zip)
#             else:
#                 zip_dict[abbrev][cty] = []
#                 zip_dict[abbrev][cty].append(zip)
#     return zip_dict
#
# def get_cities():
#     with open('./parse_GBD/cityMisspellings.xml') as f:
#         cities = xmltodict.parse(f.read())
#     city_dict = dict()
#     for state in cities['states']['state']:
#         abbrev = state['@abbrev']
#         city_dict[abbrev] = dict()
#         if 'alias' not in state: # no misspellings for this state
#             continue
#         if not isinstance(state['alias'], list): # a single misspelling for the state
#             state['alias'] = [state['alias']]
#         for city in state['alias']:
#             alias = city['@name']
#             name = city['#text']
#             if alias in city_dict[abbrev]:
#                 city_dict[abbrev][alias].append(name)
#             else:
#                 city_dict[abbrev][alias] = []
#                 city_dict[abbrev][alias].append(name)
#     return city_dict
#
# def get_inventors():
#     with open('./parse_GBD/inventors.xml') as f:
#         inventors = xmltodict.parse(f.read())
#     inventor_dict = dict()
#     for last_nm in inventors['inventors']['lastName']:
#         ln = last_nm['@abbrev']
#         inventor_dict[ln] = dict()
#         for first_nm in last_nm['firstName']:
#             fn = first_nm['@abbrev']
#             inventor_dict[ln][fn] = dict()
#             for middle_initial in first_nm[middleInitial]:
#                 mi = middle_initial['@abbrev']
#                 inventor_dict[ln][fn][mi] = []
#                 for location in middle_initial['location']:
#                     city = location['@city']
#                     state = location['@state']
#                     inventor_dict[ln][fn][mi].append({'city':city, 'state':state})
#     return inventor_dict

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
    manager = Manager()
    zips_dict = manager.dict()
    cities_dict = manager.dict()
    inventors_dict = manager.dict()
    with open('zip3_cities.json') as json_data:
        zips_dict = json.load(json_data)
    with open('cityMisspellings.json') as json_data:
        cities_dict = json.load(json_data)
    with open('inventors.json') as json_data:
        inventors_dict = json.load(json_data)
    
    # p = Pool(NUMBER_OF_PROCESSES)
    # p.map(partial(xmlParser.assign_zip3, z_dict=zips_dict, c_dict=cities_dict, i_dict=inventors_dict), files_list)
