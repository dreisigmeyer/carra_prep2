# -*- coding: utf-8 -*-

from difflib import SequenceMatcher as SeqMatcher
import json
import os
from preprocessing.gbd_metadata.src.city_names import create_city_json
from preprocessing.gbd_metadata.src.city_state_to_zip3 import create_zip3_mapping
from preprocessing.gbd_metadata.src.inventor_names import create_inventor_json
import sys
import xmltodict

# base_dir = 'create_GBD_metadata'
# cw_dir = os.getcwd()
# fp_dir = cw_dir + '/' + base_dir
CLOSE_CITY_SPELLINGS = {}
xml_files = sys.argv[1]
THIS_DIR = os.path.dirname(__file__)


class SetEncoder(json.JSONEncoder):
    '''
    To export the sets in CLOSE_CITY_SPELLINGS.
    '''

    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)
        return json.JSONEncoder.default(self, obj)


def init_close_city_spellings(zip_file, city_file, out_file):
    '''
    Creates CLOSE_CITY_SPELLINGS
    '''
    with open(zip_file) as json_data:
        zip3_json = json.load(json_data)
    with open(city_file) as json_data:
        cleaned_cities_json = json.load(json_data)
    global CLOSE_CITY_SPELLINGS
    states = zip3_json.keys()
    for state in states:
        CLOSE_CITY_SPELLINGS[state] = {}
        hold_zips = zip3_json.get(state)
        hold_misspells = cleaned_cities_json.get(state)
        if hold_zips and hold_misspells is not None:
            for city in hold_misspells.keys():
                CLOSE_CITY_SPELLINGS[state][city] = set()
                for alias, zips in hold_zips.iteritems():
                    str_match = SeqMatcher(None, alias, city)
                    if str_match.ratio() >= 0.9:
                        CLOSE_CITY_SPELLINGS[state][city].update(zips)
    with open(out_file, 'w') as fp:
        json.dump(CLOSE_CITY_SPELLINGS, fp, sort_keys=True, indent=8, cls=SetEncoder)


def zips_xml_to_json(xml_file, json_file):
    '''
    This is to change the XML file to a JSON
    '''
    with open(xml_file) as f:
        zips = xmltodict.parse(f.read())
    zip_dict = dict()
    for state in zips['states']['state']:
        abbrev = state['@abbrev']
        zip_dict[abbrev] = dict()
        for city in state['zip3']:
            cty = city['@city']
            zip = city['#text']
            if cty in zip_dict[abbrev]:
                zip_dict[abbrev][cty].append(zip)
            else:
                zip_dict[abbrev][cty] = []
                zip_dict[abbrev][cty].append(zip)
    with open(json_file, 'w') as fp:
        json.dump(zip_dict, fp, indent=8, sort_keys=True)


def make_gbd_metadata(xml_files):
    '''
    '''
    # create_city_json(THIS_DIR)
    # create_inventor_json(xml_files, THIS_DIR)
    create_zip3_mapping(THIS_DIR)
