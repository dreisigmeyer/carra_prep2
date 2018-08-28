import tarfile
import glob
import json
from lxml import etree
import os
import re
import shutil

INVENTORS_DICT = dict()
magic_validator = etree.XMLParser(
    dtd_validation=False,
    resolve_entities=False,
    encoding='utf-8',
    recover=True)


def add_to_inventors_dict(ln, fn, mn, city, state):
    '''
    Add applicant information to global dictionary
    '''
    global INVENTORS_DICT
    if mn:
        mi = mn[0]
    else:
        mi = ''
    if ln in INVENTORS_DICT:
        if fn in INVENTORS_DICT[ln]:
            if mi in INVENTORS_DICT[ln][fn]:
                new_entry = {'city': city, 'state': state}
                if new_entry not in INVENTORS_DICT[ln][fn][mi]:
                    INVENTORS_DICT[ln][fn][mi].append(new_entry)
            else:
                INVENTORS_DICT[ln][fn][mi] = []
                INVENTORS_DICT[ln][fn][mi].append({'city': city, 'state': state})
        else:
            INVENTORS_DICT[ln][fn] = {}
            INVENTORS_DICT[ln][fn][mi] = []
            INVENTORS_DICT[ln][fn][mi].append({'city': city, 'state': state})
    else:
        INVENTORS_DICT[ln] = {}
        INVENTORS_DICT[ln][fn] = {}
        INVENTORS_DICT[ln][fn][mi] = []
        INVENTORS_DICT[ln][fn][mi].append({'city': city, 'state': state})


def create_inventor_json(directories):
    hold_data_path = 'xml_data/'
    grant_year_re = re.compile('i?pgb([0-9]{4})')
    xml_directories = glob.glob(directories + '/*.bz2')
    for xml_directory in xml_directories:
        xml_filename = os.path.basename(xml_directory).split('.')[0]
        grant_year = int(grant_year_re.match(xml_filename).group(1)[:4])
        hold_directory = hold_data_path + xml_filename
        with tarfile.open(name=xml_directory, mode='r:bz2') as tar_file:
            tar_file.extractall(path=hold_data_path)
            xml_docs = glob.glob(hold_directory + '/*.xml')
            for xml_doc in xml_docs:
                xml_to_json_doc(xml_doc, grant_year)
            shutil.rmtree(hold_directory)
    with open('inventors.json', 'w') as json_file:
        json.dump(INVENTORS_DICT, json_file, ensure_ascii=False, indent=4)


def split_first_name(in_name):
    '''
    Get middle name out of first name
    '''
    holder = in_name.split(' ', 1)
    if len(holder) > 1:
        return holder[0], holder[1]
    else:
        return in_name, ''


def split_name_suffix(in_name):
    '''
    Takes the suffix off the last name
    '''
    # These are the generational suffixes.
    suffix_list = [
        'SR', 'SENIOR', 'I', 'FIRST', '1ST',
        'JR', 'JUNIOR', 'II', 'SECOND', '2ND',
        'THIRD', 'III', '3RD',
        'FOURTH', 'IV', '4TH',
        'FIFTH', 'V', '5TH',
        'SIXTH', 'VI', '6TH',
        'SEVENTH', 'VII', '7TH',
        'EIGHTH', 'VIII', '8TH',
        'NINTH' 'IX', '9TH',
        'TENTH', 'X', '10TH'
    ]
    holder = in_name.rsplit(' ', 2)
    if len(holder) == 1:  # includes empty string
        return in_name, ''
    elif len(holder) == 2:
        if holder[1] in suffix_list:
            return holder[0], holder[1]
        else:
            return in_name, ''
    elif holder[2] in suffix_list:
        if holder[1] == 'THE':
            return holder[0], holder[2]
        else:
            last_nm = holder[0] + ' ' + holder[1]
            return last_nm, holder[2]
    else:
        return in_name, ''


def xml_to_json_doc(xml_doc, grant_year):
    '''
    '''
    if 2005 <= grant_year:
        path_applicants_alt1 = 'us-bibliographic-data-grant/parties/applicants/'
        path_applicants_alt2 = 'us-bibliographic-data-grant/us-parties/us-applicants/'
        rel_path_applicants_last_name = 'addressbook/last-name'
        rel_path_applicants_first_name = 'addressbook/first-name'
        rel_path_applicants_city = 'addressbook/address/city'
        rel_path_applicants_state = 'addressbook/address/state'
        path_inventors_alt1 = 'us-bibliographic-data-grant/parties/inventors/'
        path_inventors_alt2 = 'us-bibliographic-data-grant/us-parties/inventors/'
        rel_path_inventors_last_name = 'addressbook/last-name'
        rel_path_inventors_first_name = 'addressbook/first-name'
        rel_path_inventors_city = 'addressbook/address/city'
        rel_path_inventors_state = 'addressbook/address/state'
    elif 2002 <= grant_year <= 2004:
        path_applicants_alt1 = 'SDOBI/B700/B720'
        path_applicants_alt2 = ''
        rel_path_applicants_last_name = './B721/PARTY-US/NAM/SNM/STEXT/PDAT'
        rel_path_applicants_first_name = './B721/PARTY-US/NAM/FNM/PDAT'
        rel_path_applicants_city = './B721/PARTY-US/ADR/CITY/PDAT'
        rel_path_applicants_state = './B721/PARTY-US/ADR/STATE/PDAT'
    elif 1976 <= grant_year <= 2001:
        path_applicants_alt1 = 'inventors'
        path_applicants_alt2 = ''
        rel_path_applicants_last_name = 'LN'
        rel_path_applicants_first_name = 'FN'
        rel_path_applicants_city = 'CTY'
        rel_path_applicants_state = 'STA'
    else:
        raise UserWarning('Incorrect grant year: ' + str(grant_year))

    root = etree.parse(xml_doc, parser=magic_validator)
    if path_applicants_alt2:
        if root.find(path_applicants_alt1) is not None:
            path_applicants = path_applicants_alt1
        else:
            path_applicants = path_applicants_alt2
    else:
        return
    applicants = root.findall(path_applicants)
    if not applicants:
        return
    for applicant in applicants:
        try:
            applicant_city = applicant.find(rel_path_applicants_city).text
        except Exception:
            continue
        try:
            applicant_state = applicant.find(rel_path_applicants_state).text
            applicant_state = re.sub('[^a-zA-Z]+', '', applicant_state).upper()
        except Exception:  # not a US inventor
            continue
        try:  # to get all of the applicant data
            applicant_last_name = applicant.find(rel_path_applicants_last_name).text
            applicant_last_name, applicant_suffix = split_name_suffix(applicant_last_name)
            applicant_first_name = applicant.find(rel_path_applicants_first_name).text
            applicant_first_name, applicant_middle_name = split_first_name(applicant_first_name)
        except Exception:  # something's wrong so go to the next applicant
            continue
        add_to_inventors_dict(
            applicant_last_name,
            applicant_first_name,
            applicant_middle_name,
            applicant_city,
            applicant_state)
    if path_inventors_alt1:  # more recent patents have the assignees as the applicants
        if root.find(path_inventors_alt1) is not None:
            path_inventors = path_inventors_alt1
        elif root.find(path_inventors_alt2) is not None:
            path_inventors = path_inventors_alt2
        else:
            return
        applicants = root.findall(path_inventors)
        if not applicants:
            return
        for applicant in applicants:
            try:
                applicant_city = applicant.find(rel_path_inventors_city).text
            except Exception:
                continue
            try:
                applicant_state = applicant.find(rel_path_inventors_state).text
                applicant_state = re.sub('[^a-zA-Z]+', '', applicant_state).upper()
            except Exception:  # not a US inventor
                continue
            try:  # to get all of the applicant data
                applicant_last_name = applicant.find(rel_path_inventors_last_name).text
                applicant_last_name, applicant_suffix = split_name_suffix(applicant_last_name)
                applicant_first_name = applicant.find(rel_path_inventors_first_name).text
                applicant_first_name, applicant_middle_name = split_first_name(applicant_first_name)
            except Exception:  # something's wrong so go to the next applicant
                continue
            add_to_inventors_dict(
                applicant_last_name,
                applicant_first_name,
                applicant_middle_name,
                applicant_city,
                applicant_state)
