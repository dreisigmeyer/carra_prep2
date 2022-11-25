import glob
import json
from lxml import etree
import os
from preprocessing.shared_python_code.inventor_info import get_inventor_info
from preprocessing.shared_python_code.xml_paths import inv_xml_paths
from preprocessing.shared_python_code.xml_paths import magic_validator
import re
import shutil
import tarfile

INVENTORS_DICT = dict()


def add_to_inventors_dict(ln, fn, mn, city, state):
    '''Add applicant information to global dictionary

    ln -- inventor's last name
    fn -- inventor's first name
    mn -- inventor's middle name
    city -- inventor's city on the patent
    state -- inventor's state on the patent
    '''
    global INVENTORS_DICT
    if not state or not ln or not fn or not city:
        return
    if len(state) != 2:  # not a real state
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


def create_inventor_json(directories, working_dir):
    '''Creates the JSON file of inventor information that is used for
    auto-correcting inventor city+state information

    directories -- location of bz2 XML files
    working_dir -- location where intermediate working files should be put
    '''
    hold_data_path = os.path.join(working_dir, 'data/xml_data/')
    grant_year_re = re.compile('i?pgb([0-9]{4})')
    xml_directories = glob.glob(directories + '/*.bz2')
    for xml_directory in xml_directories:
        xml_filename = os.path.basename(xml_directory).split('.')[0]
        grant_year = int(grant_year_re.match(xml_filename).group(1)[:4])
        hold_directory = hold_data_path + xml_filename
        with tarfile.open(name=xml_directory, mode='r:bz2') as tar_file:
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
                
            
            safe_extract(tar_file, path=hold_data_path)
            xml_docs = glob.glob(hold_directory + '/*.xml')
            for xml_doc in xml_docs:
                xml_to_json_doc(xml_doc, grant_year)
            shutil.rmtree(hold_directory)
    with open('inventors.json', 'w') as json_file:
        json.dump(INVENTORS_DICT, json_file, ensure_ascii=False, indent=4)
        return os.path.abspath(json_file.name)


def xml_to_json_doc(xml_doc, grant_year):
    '''Takes information from the XML files and places it into JSON format

    xml_doc -- name of the XML file that's being processed
    grant_year -- grant year of patent
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
        if not ln or not fn:  # no last or first name
            continue
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
            if not ln or not fn:  # no last or first name
                continue
            add_to_inventors_dict(ln, fn, mn, city, state)
