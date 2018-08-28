import tarfile
import glob
import json
from lxml import etree
import os
from preprocessing.shared_python_code.inventor_info import get_inventor_info
from preprocessing.shared_python_code.xml_paths import inv_xml_paths
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
    if not state or not ln or not fn or not city:
        return
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


def xml_to_json_doc(xml_doc, grant_year):
    '''
    '''
    _, _, path_apps_alt1, path_apps_alt2, path_invs_alt1, path_invs_alt2, _ = inv_xml_paths(grant_year)
    root = etree.parse(xml_doc, parser=magic_validator)
    if root.find(path_apps_alt1) is not None:
        path_applicants = path_apps_alt1
    elif path_apps_alt2 and root.find(path_apps_alt2) is not None:
            path_applicants = path_apps_alt2
    else:
        return
    applicants = root.findall(path_applicants)
    if not applicants:
        return
    for applicant in applicants:
        city, state, _, ln, suf, fn, mn = get_inventor_info(applicant, grant_year)
        ln = (ln + ' ' + suf).strip()
        add_to_inventors_dict(ln, fn, mn, city, state)
    if path_invs_alt1:  # more recent patents have the assignees as the applicants
        if root.find(path_invs_alt1) is not None:
            path_inventors = path_invs_alt1
        elif root.find(path_invs_alt2) is not None:
            path_inventors = path_invs_alt2
        else:
            return
        applicants = root.findall(path_inventors)
        if not applicants:
            return
        for applicant in applicants:
            city, state, _, ln, suf, fn, mn = get_inventor_info(applicant, grant_year)
            ln = (ln + ' ' + suf).strip()
            add_to_inventors_dict(ln, fn, mn, city, state)
