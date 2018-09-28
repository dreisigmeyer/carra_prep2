import glob
import csv
import json
import os
from preprocessing.shared_python_code.process_text import clean_patnum
from preprocessing.shared_python_code.process_text import standardize_name
from preprocessing.shared_python_code.process_text import standardize_name_late_of
import re

CITIES_DICT = dict()
INVENTORS_DICT = dict()


def add_to_inventors_dict(prdn, inv_seq, state, city, alias=False):
    '''
    Add city misspelling information to global dictionary
    '''
    global INVENTORS_DICT
    if not prdn or not inv_seq or not state or not city:
        return
    if len(state) != 2:  # not a real state
        return
    if re.search(r'\bbCOUNTY\b', city):  # not a real city
        return
    if not alias:  # this is the cleaned data and we're setting up the dict
        if prdn in INVENTORS_DICT:
            if inv_seq in INVENTORS_DICT[prdn]:  # this shoudln't happen
                return
            else:
                INVENTORS_DICT[prdn][inv_seq] = {'state': state, 'city': city, 'alias': [city]}
        else:
            INVENTORS_DICT[prdn] = {}
            INVENTORS_DICT[prdn][inv_seq] = {'state': state, 'city': city, 'alias': [city]}
    else:  # all of these if statements must be true for this to be a valid city misspelling
        if prdn in INVENTORS_DICT:
            if inv_seq in INVENTORS_DICT[prdn]:
                if state == INVENTORS_DICT[prdn][inv_seq]['state']:
                    if city not in INVENTORS_DICT[prdn][inv_seq]['alias']:
                        INVENTORS_DICT[prdn][inv_seq]['alias'].append(city)


def add_to_cities_dict(state, city, alias):
    '''
    Add city misspelling information to global dictionary
    '''
    global CITIES_DICT
    if not state or not city or not alias:
        return
    if len(state) != 2:  # not a real state
        return
    if re.search(r'\bCOUNTY\b', city) or re.search(r'\bCOUNTY\b', alias):  # not a real city
        return
    if state in CITIES_DICT:
        if city in CITIES_DICT[state]:
            if alias not in CITIES_DICT[state][city]:
                CITIES_DICT[state][city].append(alias)
        else:
            CITIES_DICT[state][city] = []
            CITIES_DICT[state][city].append(alias)
    else:
        CITIES_DICT[state] = {}
        CITIES_DICT[state][city] = []
        CITIES_DICT[state][city].append(alias)


def create_city_json(working_dir):
    '''
    '''
    uspto_data_path = os.path.join(working_dir, 'data/uspto_data/')
    user_data_path = os.path.join(working_dir, 'data/user_data/')
    raw_data = glob.glob(uspto_data_path + 'INVENTOR_*')[0]
    clean_data = glob.glob(uspto_data_path + 'INV_COUNTY_*')[0]
    user_data = glob.glob(user_data_path + 'city_misspellings.csv')[0]
    with open(user_data) as user_file:
        reader = csv.reader(user_file)
        for state, city, alias in reader:
            add_to_cities_dict(state, city, alias)
    with open(clean_data) as clean_file:
        for line in clean_file:
            zip_code = line[94:99].strip()
            state = line[90:93]
            city = line[69:89]
            prdn = line[0:7]
            inv_seq = line[8:11].strip()
            if not zip_code:  # self-assigned seem to not be corrected so skip
                state = standardize_name(state)
                city = standardize_name(city)
                prdn = clean_patnum(prdn)[0]
                add_to_inventors_dict(prdn, inv_seq, state, city)
    with open(raw_data) as clean_file:
        for line in clean_file:
            state = line[121:124]
            city = line[100:120]
            prdn = line[0:7]
            inv_seq = line[8:11].strip()
            state = standardize_name(state)
            city = standardize_name_late_of(city)
            prdn = clean_patnum(prdn)[0]
            add_to_inventors_dict(prdn, inv_seq, state, city, alias=True)
    for prdn in INVENTORS_DICT:
        for inv_seq in INVENTORS_DICT[prdn]:
            state = INVENTORS_DICT[prdn][inv_seq]['state']
            city = INVENTORS_DICT[prdn][inv_seq]['city']
            for alias in INVENTORS_DICT[prdn][inv_seq]['alias']:
                add_to_cities_dict(state, city, alias)
    with open('city_misspellings.json', 'w') as json_file:
        json.dump(CITIES_DICT, json_file, ensure_ascii=False, indent=4)
