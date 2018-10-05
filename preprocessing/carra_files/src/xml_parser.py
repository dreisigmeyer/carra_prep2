import codecs
import csv
from datetime import datetime
from difflib import SequenceMatcher as SeqMatcher
import glob
import json
from lxml import etree
import os
from preprocessing.shared_python_code.inventor_info import get_inventor_info
from preprocessing.shared_python_code.process_text import clean_patnum
from preprocessing.shared_python_code.process_text import dateFormat
from preprocessing.shared_python_code.process_text import grant_year_re
from preprocessing.shared_python_code.xml_paths import carra_xml_paths
from preprocessing.shared_python_code.xml_paths import magic_validator
import re
import shutil
import tarfile
import warnings

THIS_DIR = os.path.dirname(__file__)
hold_folder_path = THIS_DIR + '/hold_data/'
out_folder_path = THIS_DIR + '/../out_data/'
'''
CLOSE_CITY_SPELLINGS is a dictionary of zips of cities in the same state with a similar name.  It includes the
zips of the city itself.  This can be updated by each process which is why we didn't create it in launch.py.
'''
CLOSE_CITY_SPELLINGS = {}


def get_zip3(applicant_state, applicant_city,
             zip3_json, cleaned_cities_json, inventor_names_json,
             last_name=None, first_name=None, middle_initial=None,
             flag=0):
    '''
    Attempts to find a zip3 from an applicant's city and state information.
    flag is for when we call this function again and avoid infinite recursion.
    '''
    global CLOSE_CITY_SPELLINGS
    possible_zip3s = set()
    possible_cities = [applicant_city]
    cleaned_cities = cleaned_cities_json.get(applicant_state)
    if cleaned_cities:
        for hold_city, spellings in cleaned_cities.items():
            if hold_city not in possible_cities:
                if applicant_city[:20] in spellings:
                    possible_cities.append(hold_city)
    city_names = zip3_json.get(applicant_state)
    close_city_names = CLOSE_CITY_SPELLINGS.get(applicant_state)
    if close_city_names:
        close_city_names_keys = close_city_names.keys()
    else:
        close_city_names_keys = []
    for alias in possible_cities:
        if alias in close_city_names_keys:  # is the name ok?
            possible_zip3s.update(close_city_names[alias])
            continue
        if applicant_state not in CLOSE_CITY_SPELLINGS.keys():  # is this a real state?
            continue
        CLOSE_CITY_SPELLINGS[applicant_state][alias] = set()  # this isn't there
        if city_names:  # this may be a new misspelling, which we're going to check for now
            for city, zips in city_names.items():
                str_match = SeqMatcher(None, alias, city)
                if str_match.ratio() >= 0.9:  # good enough match
                    CLOSE_CITY_SPELLINGS[applicant_state][alias].update(zips)
                    possible_zip3s.update(zips)
    # If we couldn't find a zip3 we'll see if we can correct the city, state or country
    if not possible_zip3s and not flag:
        l_name = last_name[:20]
        f_name = first_name[:15]
        if middle_initial:
            middle_initial = middle_initial[0]
        locations = []
        try:
            locations = inventor_names_json.get(l_name).get(f_name).get(middle_initial)
        except Exception:  # possible the name isn't in our JSON file
            pass
        for location in locations:
            app_city = applicant_city[:20]
            app_state = applicant_state
            possible_city = location['city']
            possible_state = location['state']
            # Foreign national
            if len(possible_state) == 3 and possible_state[2] == 'X':
                continue
            # We only allow the city OR the state to be incorrect.
            # Otherwise we could be finding a different inventor with
            # the same name with a relatively high probability.
            # The state is wrong (seems to happen more often so it's first)
            elif app_city == possible_city and app_state != possible_state:
                app_state = possible_state
            # The city is wrong (seems to happen less often so it's second)
            elif app_city != possible_city and app_state == possible_state:
                app_city = possible_city
            # Nothing is wrong
            else:
                continue

            hold_corrected_zip3 = get_zip3(app_state, app_city,
                                           zip3_json, cleaned_cities_json, inventor_names_json,
                                           flag=1)
            possible_zip3s.update(hold_corrected_zip3)
    return possible_zip3s


def zip3_thread(in_file, zip3_json, cleaned_cities_json, inventor_names_json):
    '''
    '''
    folder_name = os.path.splitext(os.path.basename(in_file))[0]
    grant_year_gbd = int(grant_year_re.match(folder_name).group(1)[:4])
    folder_name = os.path.basename(in_file).split('.')[0]
    xml_data_path = hold_folder_path + folder_name
    with tarfile.open(name=in_file, mode='r:bz2') as tar_file:
        tar_file.extractall(path=hold_folder_path)
        xml_split = glob.glob(xml_data_path + '/*.xml')
        for xmlDoc in xml_split:
            try:
                xml_doc_thread(xmlDoc, grant_year_gbd, zip3_json, cleaned_cities_json, inventor_names_json, folder_name)
            except Exception as e:
                print(xmlDoc + ': ' + str(e))
                pass
    shutil.rmtree(xml_data_path)


def write_csv_line(
        root, path_alt1, path_alt2,
        prdn, uspto_prdn, app_year, grant_year, assg_st, xml_doc,
        zip3_json, cleaned_cities_json, inventor_names_json):
    '''
    '''
    if root.find(path_alt1) is not None:
        path_applicants = path_alt1
    elif root.find(path_alt2) is not None:
        path_applicants = path_alt2
    else:
        return
    applicants = root.findall(path_applicants)
    if not applicants:
        return
    number_applicants_to_process = len(applicants)
    applicant_counter = 0
    for applicant in applicants:
        applicant_counter += 1
        csv_line = [prdn, uspto_prdn, app_year, grant_year]
        inv_info = get_inventor_info(applicant, grant_year)
        appl_city, appl_state, appl_seq_num = inv_info[0], inv_info[1], inv_info[2]
        appl_ln, appl_suf, appl_fn, appl_mn = inv_info[3], inv_info[4], inv_info[5], inv_info[6]
        if not appl_state:  # not a US inventor
            continue
        if not appl_ln:  # something's wrong
            continue
        csv_line.extend(
            (appl_city, appl_state, appl_seq_num, applicant_counter, appl_ln, appl_suf, appl_fn, appl_mn))
        possible_zip3s = get_zip3(appl_state, appl_city,
                                  zip3_json, cleaned_cities_json, inventor_names_json,
                                  appl_ln, appl_fn, appl_mn)
        if not possible_zip3s:  # Didn't find a zip3?
            possible_zip3s.add('')  # We'll at least have the city/state
        out_csv_file = out_folder_path + 'zip3s_' + app_year + '.csv'
        csv_file = codecs.open(out_csv_file, 'a')
        csv_writer = csv.writer(csv_file)
        # Write results
        for new_zip3 in possible_zip3s:
            for asg_st in assg_st:
                hold_csv_line = list(csv_line)  # copy csv_line...
                hold_csv_line.append(new_zip3)  # ... so we can append without fear!
                hold_csv_line.append(asg_st)
                csv_writer.writerow(hold_csv_line)
    # make sure we at least tried to get every applicant
    if number_applicants_to_process != applicant_counter:
        warnings.warn('Did not try to process every applicant on patent ' + prdn)


# noinspection PyUnboundLocalVariable
def xml_doc_thread(xml_doc, grant_year_gbd, zip3_json, cleaned_cities_json, inventor_names_json, folder_name):
    '''
    '''
    xml_paths = carra_xml_paths(grant_year_gbd)
    path_patent_number, path_app_date = xml_paths[0], xml_paths[1]
    path_applicants_alt1, path_applicants_alt2 = xml_paths[2], xml_paths[3]
    path_inventors_alt1, path_inventors_alt2 = xml_paths[4], xml_paths[5]
    path_assignees, rel_path_assignees_state = xml_paths[6], xml_paths[7]
    root = etree.parse(xml_doc, parser=magic_validator)
    patent_number = root.find(path_patent_number).text
    patent_number, uspto_pat_num = clean_patnum(patent_number)
    app_date = root.find(path_app_date).text
    app_year = str(datetime.strptime(app_date, dateFormat).year)
    assignees = root.findall(path_assignees)
    assignee_state = set()
    if assignees:
        for assignee in assignees:
            try:  # to get an assignee state
                assignee_state_hold = assignee.find(rel_path_assignees_state).text
                assignee_state_hold = re.sub('[^a-zA-Z]+', '', assignee_state_hold).upper()
                assignee_state.add(assignee_state_hold)
            except Exception:  # don't worry if you can't
                pass
    if not assignee_state:
        assignee_state.add('')  # we need a non-empty assignee_state below
    write_csv_line(
        root, path_applicants_alt1, path_applicants_alt2,
        patent_number, uspto_pat_num, app_year, grant_year_gbd, assignee_state, xml_doc,
        zip3_json, cleaned_cities_json, inventor_names_json)
    if grant_year_gbd >= 2005:  # inventor information may not be in the applicant fields
        write_csv_line(
            root, path_inventors_alt1, path_inventors_alt2,
            patent_number, uspto_pat_num, app_year, grant_year_gbd, assignee_state, xml_doc,
            zip3_json, cleaned_cities_json, inventor_names_json)


def assign_zip3(files, path_to_json, zip3_json, cleaned_cities_json, inventor_names_json):
    '''
    '''
    global CLOSE_CITY_SPELLINGS
    with open(path_to_json + '/close_city_spellings.json') as json_data:
        CLOSE_CITY_SPELLINGS = json.load(json_data)
    for in_file in files:
        zip3_thread(in_file, zip3_json, cleaned_cities_json, inventor_names_json)
