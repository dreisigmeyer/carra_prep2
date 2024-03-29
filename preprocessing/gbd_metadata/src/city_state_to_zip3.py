import csv
import glob
import json
from lxml import etree
import os
from preprocessing.shared_python_code.process_text import standardize_name_cdp
import re

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


def create_abbreviations(line):
    '''Expands abbreviations or creates them

    line -- string to work on
    '''
    global STATE_CITY_ZIP3

    def insert_new_city(abbrev_re, word, state, city):
        '''Actually inserts the new abbreviations correctly
        '''
        global STATE_CITY_ZIP3
        if re.search(abbrev_re, city):
            new_city = re.sub(abbrev_re, word, city)
            if new_city in STATE_CITY_ZIP3[state]:
                for zip3 in STATE_CITY_ZIP3[state][city]:
                    if zip3 not in STATE_CITY_ZIP3[state][new_city]:
                        STATE_CITY_ZIP3[state][new_city].append(zip3)
            else:
                STATE_CITY_ZIP3[state][new_city] = STATE_CITY_ZIP3[state][city]

    abbrev, word = line[0], line[1]
    abbrev_re = '\\b' + abbrev + '\\b'
    word_re = '\\b' + word + '\\b'
    states = [*STATE_CITY_ZIP3]
    for state in states:
        cities = [*STATE_CITY_ZIP3[state]]
        for city in cities:
            insert_new_city(abbrev_re, word, state, city)
            insert_new_city(word_re, abbrev, state, city)


def csv_reader_skip_headers(in_file, delimiter=','):
    '''Returnes a csv reader skipping over the header line.

    in_file -- name of the file to read in
    delimiter -- (Default ',')
    '''
    f_csv = csv.reader(in_file, delimiter=delimiter)
    next(f_csv)
    return f_csv


def process_state_html(file):
    '''Gets zips out of the USPS HTML

    file -- file name to process
    '''
    path_info = "/body/table/tr/td/table/tr/td/table/tr/td//a[@alt]/../.."
    parser = etree.HTMLParser()
    state_name = os.path.splitext(os.path.basename(file))[0]
    state_abbrev = ST_ABBREVS[state_name]
    html_doc = etree.parse(open(file), parser)
    data = html_doc.findall(path_info)
    for office in data:
        zip_code = office[0][0].text.strip()
        city = office[1].text.strip()
        if zip_code and city:
            update_zip3_mapping(state_abbrev, city, zip_code[:3])


def read_zcta_line(line):
    '''This maps the geoid to zip3s.

    line -- string to process
    '''
    global GEOID_TO_ZIP3
    geoid, zcta = line[4], line[0]
    GEOID_TO_ZIP3[geoid] = zcta[:3]
    return


def read_states_line(line):
    '''This collects together state information.

    line -- string to process
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


def read_sparql_line(line):
    '''Reads in a SPARQL query result

    line -- string to process
    '''
    zip3, city, state = line[0], line[1], line[2]
    city = standardize_name_cdp(city)
    state = standardize_name_cdp(state)
    if len(zip3) == 4:  # lacking a leading 0
        zip3 = '0' + zip3[:2]
    elif len(zip3) == 5:
        zip3 = zip3[:3]
    else:  # can't be a zipcode
        return
    if state in ST_ABBREVS:
        abbrev = ST_ABBREVS[state]
        update_zip3_mapping(abbrev, city, zip3)
    return


def read_dbpedia_line(line):
    '''Reads in a line from the DBPedia dataset

    line -- string to process
    '''
    city, state, zip3 = line[0], line[1], line[2]
    city = standardize_name_cdp(city)
    state = standardize_name_cdp(state)
    if len(zip3) == 4:  # lacking a leading 0
        zip3 = '0' + zip3[:2]
    elif len(zip3) == 5:
        zip3 = zip3[:3]
    else:  # can't be a zipcode
        return
    if state in ST_ABBREVS:
        abbrev = ST_ABBREVS[state]
        update_zip3_mapping(abbrev, city, zip3)
    return


def read_other_line(line):
    '''Generic processing of a string

    line -- string to process
    '''
    city, abbrev, zip3 = line[0], line[1], line[2]
    zip3 = zip3[:3]
    update_zip3_mapping(abbrev, city, zip3)
    return


def read_allname_line(line):
    '''This collects alternate names for each geoid.

    line -- string to process
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
    '''Creates the city+state to zip3 mapping.
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
    '''Add new zip3 to dictionary

    state -- state the zip3 is in
    name -- city name of the zip3
    zip3 -- the zip3
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
    '''Main programm to create the city+state to zip3 mappings

    working_dir -- location of data files
    '''
    usgs_data_path = os.path.join(working_dir, 'data/usgs_data/')
    states_data_path = os.path.join(usgs_data_path, 'states/')
    zipcode_data_path = os.path.join(working_dir, 'data/zipcode_data/')
    user_data_path = os.path.join(working_dir, 'data/user_data/')
    allnames_data = glob.glob(usgs_data_path + 'AllNames_*.txt')[0]
    zcta_data = glob.glob(usgs_data_path + 'zcta_place_rel_*.txt')[0]
    states_data = glob.glob(states_data_path + '*_FedCodes_*.txt')
    usps_data = glob.glob(zipcode_data_path + 'post_offices/*.html')
    sparql_data = glob.glob(zipcode_data_path + 'sparql_query_results.csv')[0]
    dbpedia_data = glob.glob(zipcode_data_path + 'infobox_postalcodes_en.csv')[0]
    free_zipcode_data = glob.glob(zipcode_data_path + 'free-zipcode-database.csv')[0]
    post_office_data = glob.glob(zipcode_data_path + 'post_office_zips.csv')[0]
    additional_zips = glob.glob(user_data_path + 'additional_zips.csv')[0]
    abbreviations = glob.glob(user_data_path + 'abbreviations.csv')[0]

    # start by using the usgs geoid
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
    state_city_to_zip3()  # create the final mapping from the geoids

    # now start updating the mapping with other sources
    for state_html in usps_data:  # from the usps
        process_state_html(state_html)
    with open(sparql_data) as csv_file:  # sparql query
        sparql_reader = csv.reader(csv_file)
        for line in sparql_reader:
            read_sparql_line(line)
    with open(dbpedia_data) as csv_file:  # DBPedia
        dbpedia_reader = csv.reader(csv_file)
        for line in dbpedia_reader:
            read_dbpedia_line(line)
    with open(free_zipcode_data) as csv_file:  # free-zipcode file
        free_zipcode_reader = csv.reader(csv_file, delimiter='|')
        for line in free_zipcode_reader:
            read_other_line(line)
    with open(post_office_data) as csv_file:  # post office locations
        post_office_reader = csv.reader(csv_file, delimiter='|')
        for line in post_office_reader:
            read_other_line(line)
    with open(additional_zips) as csv_file:  # user supplied
        additional_zips_reader = csv.reader(csv_file, delimiter='|')
        for line in additional_zips_reader:
            read_other_line(line)

    # now expand things by substituting common abbreviations
    with open(abbreviations) as csv_file:  # sparql query
        abbrevs_reader = csv.reader(csv_file)
        for line in abbrevs_reader:
            create_abbreviations(line)

    with open('city_state_to_zip3.json', 'w') as json_file:
        json.dump(STATE_CITY_ZIP3, json_file, ensure_ascii=False, indent=4)
        return os.path.abspath(json_file.name)
