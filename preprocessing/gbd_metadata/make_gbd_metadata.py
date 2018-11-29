from difflib import SequenceMatcher as SeqMatcher
import json
import os
from preprocessing.gbd_metadata.src.city_names import create_city_json
from preprocessing.gbd_metadata.src.city_state_to_zip3 import create_zip3_mapping
from preprocessing.gbd_metadata.src.inventor_names import create_inventor_json
import sys

xml_files = sys.argv[1]
THIS_DIR = os.path.dirname(__file__)


class SetEncoder(json.JSONEncoder):
    '''To export the sets in CLOSE_CITY_SPELLINGS.
    '''

    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)
        return json.JSONEncoder.default(self, obj)


def init_close_city_spellings(zip_file, city_file):
    '''Creates CLOSE_CITY_SPELLINGS

    zip_file -- JSON file of city+state to zip3s
    city_file -- JSON file of aliases/misspellings of city names
    '''
    CLOSE_CITY_SPELLINGS = {}
    # global CLOSE_CITY_SPELLINGS
    with open(zip_file) as json_data:
        zip3_json = json.load(json_data)
    with open(city_file) as json_data:
        cleaned_cities_json = json.load(json_data)
    states = zip3_json.keys()
    for state in states:
        CLOSE_CITY_SPELLINGS[state] = {}
        hold_zips = zip3_json.get(state)
        hold_misspells = cleaned_cities_json.get(state)
        if hold_zips and hold_misspells is not None:
            for city in hold_misspells.keys():
                CLOSE_CITY_SPELLINGS[state][city] = set()
                for alias, zips in hold_zips.items():
                    str_match = SeqMatcher(None, alias, city)
                    if str_match.ratio() >= 0.9:
                        CLOSE_CITY_SPELLINGS[state][city].update(zips)
    with open('close_city_spellings.json', 'w') as json_file:
        json.dump(CLOSE_CITY_SPELLINGS, json_file, sort_keys=True, indent=8, cls=SetEncoder)
        return os.path.abspath(json_file.name)


def make_gbd_metadata(xml_files):
    '''Generates the patent metadata from the USPTO XML files

    xml_files -- path to XML files
    '''
    city_file = create_city_json(THIS_DIR)
    create_inventor_json(xml_files, THIS_DIR)
    zip_file = create_zip3_mapping(THIS_DIR)
    init_close_city_spellings(zip_file, city_file)
