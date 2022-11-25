import codecs
import csv
from datetime import datetime
import glob
from lxml import etree
import os
from preprocessing.shared_python_code.inventor_info import get_inventor_info
from preprocessing.shared_python_code.process_text import clean_patnum
from preprocessing.shared_python_code.process_text import dateFormat
from preprocessing.shared_python_code.process_text import grant_year_re
from preprocessing.shared_python_code.xml_paths import carra_xml_paths
from preprocessing.shared_python_code.xml_paths import magic_validator
from preprocessing.shared_python_code.utility_functons import initialize_close_city_spelling
import re
import shutil
import tarfile
import warnings

THIS_DIR = os.path.dirname(__file__)
hold_folder_path = THIS_DIR + '/hold_data/'
out_folder_path = THIS_DIR + '/../out_data/'


def zip3_thread(in_file, zip3_json, cleaned_cities_json, inventor_names_json):
    '''Prepares things to attach zip3s to inventor names

    in_file -- XML file to process
    zip3_json -- JSON file of city+state to zip3s
    cleaned_cities_json -- JSON file of potential city misspellings
    inventor_names_json -- JSON file of inventor names to potential prior city+state residencies
    '''
    folder_name = os.path.splitext(os.path.basename(in_file))[0]
    grant_year_gbd = int(grant_year_re.match(folder_name).group(1)[:4])
    folder_name = os.path.basename(in_file).split('.')[0]
    xml_data_path = hold_folder_path + folder_name
    with tarfile.open(name=in_file, mode='r:bz2') as tar_file:
        def is_within_directory(directory, target):
            
            abs_directory = os.path.abspath(directory)
            abs_target = os.path.abspath(target)
        
            prefix = os.path.commonprefix([abs_directory, abs_target])
            
            return prefix == abs_directory
        
        def safe_extract(tar, path=".", members=None, *, numeric_owner=False):
        
            for member in tar.getmembers():
                member_path = os.path.join(path, member.name)
                if not is_within_directory(path, member_path):
                    raise Exception("Attempted Path Traversal in Tar File")
        
            tar.extractall(path, members, numeric_owner=numeric_owner) 
            
        
        safe_extract(tar_file, path=hold_folder_path)
        xml_split = glob.glob(xml_data_path + '/*.xml')
        for xmlDoc in xml_split:
            try:
                xml_doc_thread(xmlDoc, grant_year_gbd, zip3_json, cleaned_cities_json, inventor_names_json)
            except Exception as e:
                print(xmlDoc + ': ' + str(e))
                pass
    shutil.rmtree(xml_data_path)


def write_csv_line(
        root, path_alt1, path_alt2,
        prdn, uspto_prdn, app_year, grant_year, assg_st,
        zip3_json, cleaned_cities_json, inventor_names_json):
    '''Writes the inventor information to the output file for CARRA

    root -- root of the XML document
    path_alt1 -- path to inventors
    path_alt2 -- path to inventors
    prdn -- patent number
    uspto_prdn -- patent number in USPTO format
    app_year -- application year of the patent
    grant_year -- grant year of the patent
    assg_st -- assignee state
    zip3_json -- JSON file of city+state to zip3s
    cleaned_cities_json -- JSON file of potential city misspellings
    inventor_names_json -- JSON file of inventor names to potential prior city+state residencies
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


def xml_doc_thread(xml_doc, grant_year_gbd, zip3_json, cleaned_cities_json, inventor_names_json):
    '''Prepares XML information for writing to a CSV file for CARRA

    xml_doc -- the XML document we're parsing
    grant_year_gbd -- grant year of the patent
    zip3_json -- JSON file of city+state to zip3s
    cleaned_cities_json -- JSON file of potential city misspellings
    inventor_names_json -- JSON file of inventor names to potential prior city+state residencies
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
        patent_number, uspto_pat_num, app_year, grant_year_gbd, assignee_state,
        zip3_json, cleaned_cities_json, inventor_names_json)
    if grant_year_gbd >= 2005:  # inventor information may not be in the applicant fields
        write_csv_line(
            root, path_inventors_alt1, path_inventors_alt2,
            patent_number, uspto_pat_num, app_year, grant_year_gbd, assignee_state,
            zip3_json, cleaned_cities_json, inventor_names_json)


def assign_zip3(files, path_to_json, close_city_spellings, zip3_json, cleaned_cities_json, inventor_names_json):
    '''Master file that launches the zip3 assignement

    files -- XML files to process
    path_to_json -- where the JSON data files are located at
    close_city_spellings -- misspellings of city names
    zip3_json -- JSON file of city+state to zip3s
    cleaned_cities_json -- JSON file of potential city misspellings
    inventor_names_json -- JSON file of inventor names to potential prior city+state residencies
    '''
    global get_zip3
    get_zip3 = initialize_close_city_spelling(path_to_json + close_city_spellings)
    for in_file in files:
        zip3_thread(in_file, zip3_json, cleaned_cities_json, inventor_names_json)
