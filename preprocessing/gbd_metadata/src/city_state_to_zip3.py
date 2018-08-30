import codecs
import csv
import glob
from lxml import etree
import os
from preprocessing.shared_python_code.process_text import standardize_name_cdp

GEOID_TO_ZIP3 = dict()  # We need the geoids to link up different files
GEOID_INFO = dict()
FIPS_ZIP3S = dict()  # all of the zips in a county
FEATURE_TO_GEO_ID = dict()  # also to link up different data files
STATE_CITY_ZIP3 = dict()

ST_ABBREVS = {
    "ALABAMA": "AL",
    "ALASKA": "AK",
    "ARIZONA": "AZ",
    "ARKANSAS": "AR",
    "CALIFORNIA": "CA",
    "COLORADO": "CO",
    "CONNECTICUT": "CT",
    "DELAWARE": "DE",
    "FLORIDA": "FL",
    "GEORGIA": "GA",
    "HAWAII": "HI",
    "IDAHO": "ID",
    "ILLINOIS": "IL",
    "INDIANA": "IN",
    "IOWA": "IA",
    "KANSAS": "KS",
    "KENTUCKY": "KY",
    "LOUISIANA": "LA",
    "MAINE": "ME",
    "MARYLAND": "MD",
    "MASSACHUSETTS": "MA",
    "MICHIGAN": "MI",
    "MINNESOTA": "MN",
    "MISSISSIPPI": "MS",
    "MISSOURI": "MO",
    "MONTANA": "MT",
    "NEBRASKA": "NE",
    "NEVADA": "NV",
    "NEW_HAMPSHIRE": "NH",
    "NEW_JERSEY": "NJ",
    "NEW_MEXICO": "NM",
    "NEW_YORK": "NY",
    "NORTH_CAROLINA": "NC",
    "NORTH_DAKOTA": "ND",
    "OHIO": "OH",
    "OKLAHOMA": "OK",
    "OREGON": "OR",
    "PENNSYLVANIA": "PA",
    "RHODE_ISLAND": "RI",
    "SOUTH_CAROLINA": "SC",
    "SOUTH_DAKOTA": "SD",
    "TENNESSEE": "TN",
    "TEXAS": "TX",
    "UTAH": "UT",
    "VERMONT": "VT",
    "VIRGINIA": "VA",
    "WASHINGTON": "WA",
    "WEST_VIRGINIA": "WV",
    "WISCONSIN": "WI",
    "WYOMING": "WY"
}


def csv_reader_skip_headers(in_file, delimiter=','):
    '''
    Returnes a csv reader skipping over the header line.
    '''
    f_csv = csv.reader(in_file, delimiter=delimiter)
    next(f_csv)
    return f_csv


def read_zcta_line(line):
    '''
    This maps the geoid to zip3s.
    '''
    global GEOID_TO_ZIP3
    geoid, zcta = line[4], line[0]
    GEOID_TO_ZIP3[geoid] = zcta[:3]
    return


def read_states_line(line):
    '''
    This collects together state information.
    '''
    global GEOID_INFO
    global FIPS_ZIP3S
    geoid, f_id, st, nm, fips = line[7] + line[3], line[0], line[8], line[1], line[7] + line[10]
    nm = standardize_name_cdp(nm)
    if geoid in GEOID_TO_ZIP3:
        zip3 = GEOID_TO_ZIP3[geoid]
        if fips in FIPS_ZIP3S and zip3 not in FIPS_ZIP3S[fips]:  # get all of the zip3s in a county
            FIPS_ZIP3S[fips].append(zip3)
        elif fips not in FIPS_ZIP3S:
            FIPS_ZIP3S[fips] = [zip3]
    FEATURE_TO_GEO_ID[f_id] = geoid
    GEOID_INFO[geoid] = {}
    GEOID_INFO[geoid]['state'] = st
    GEOID_INFO[geoid]['name'] = [nm]
    GEOID_INFO[geoid]['fips'] = fips
    return


def read_allname_line(line):
    '''
    This collects alternate names for each geoid.
    '''
    global GEOID_INFO
    f_id, nm = line[0], line[1]
    nm = standardize_name_cdp(nm)
    if f_id in FEATURE_TO_GEO_ID:
        geoid = FEATURE_TO_GEO_ID[f_id]
        if nm not in GEOID_INFO[geoid]['name']:
            GEOID_INFO[geoid]['name'].append(nm)
    return


def state_city_to_zip3():
    '''
    Creates the city+state to zip3 mapping.
    '''
    for geoid in GEOID_INFO:
        state = GEOID_INFO[geoid]['state']
        if geoid in GEOID_TO_ZIP3:
            zip3 = GEOID_TO_ZIP3[geoid]
            for name in GEOID_INFO[geoid]['name']:
                update_zip3_mapping(state, name, zip3)
        else:
            fips = GEOID_INFO[geoid]['fips']
            if fips in FIPS_ZIP3S:
                for zip3 in FIPS_ZIP3S[fips]:
                    for name in GEOID_INFO[geoid]['name']:
                        update_zip3_mapping(state, name, zip3)
    return


def update_zip3_mapping(state, name, zip3):
    '''
    Add new zip3 to dictionary
    '''
    global STATE_CITY_ZIP3
    if state in STATE_CITY_ZIP3:
        if name in STATE_CITY_ZIP3[state]:
            if zip3 not in STATE_CITY_ZIP3[state][name]:
                STATE_CITY_ZIP3[state][name].append(zip3)
        else:
            STATE_CITY_ZIP3[state][name] = [zip3]
    else:
        STATE_CITY_ZIP3[state] = dict()
        STATE_CITY_ZIP3[state][name] = [zip3]
    return


def create_zip3_mapping(working_dir):
    '''
    '''
    usgs_data_path = os.path.join(working_dir, 'data/usgs_data/')
    states_data_path = os.path.join(usgs_data_path, 'states/')
    allnames_data = glob.glob(usgs_data_path + 'AllNames_*')[0]
    zcta_data = glob.glob(usgs_data_path + 'zcta_place_rel_*')[0]
    states_data = glob.glob(states_data_path + '*_FedCodes_*.txt')
    with open(zcta_data) as csv_file:  # get the zip3s for each geoid
        zcta_reader = csv_reader_skip_headers(csv_file)
        for line in zcta_reader:
            read_zcta_line(line)
    for state_data in states_data:  # get general info for each geoid and collect zip3s
        with open(state_data) as csv_file:
            state_reader = csv_reader_skip_headers(csv_file, delimiter='|')
            for line in state_reader:
                read_states_line(line)
    with open(allnames_data) as csv_file:
        allname_reader = csv_reader_skip_headers(csv_file, delimiter='|')  # getting alternate names for each geoid
        try:  # some null byte issues
            for line in allname_reader:
                read_allname_line(line)
        except Exception as e:
            pass
    state_city_to_zip3()  # create the final mapping
