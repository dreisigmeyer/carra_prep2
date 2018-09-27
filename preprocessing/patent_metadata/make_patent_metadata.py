import csv
from datetime import datetime
import glob
from lxml import etree
from multiprocessing import Pool
import os
from preprocessing.shared_python_code.process_text import clean_patnum
from preprocessing.shared_python_code.process_text import dateFormat
from preprocessing.shared_python_code.process_text import grant_year_re
from preprocessing.shared_python_code.utility_functons import split_seq
from preprocessing.shared_python_code.xml_paths import magic_validator
from preprocessing.shared_python_code.xml_paths import metadata_xml_paths
import re
import shutil
import tarfile

THIS_DIR = os.path.dirname(__file__)


def get_info(files):
    '''
    '''
    for file in files:
        folder_name = os.path.basename(file).split('.')[0]
        out_csv_file = './out_data/' + folder_name + '.csv'
        grant_year_GBD = int(grant_year_re.match(folder_name).group(1))
        with open(out_csv_file, 'w') as csv_file:
            csv_writer = csv.writer(csv_file, delimiter=',')
            # Get data in and ready
            hold_folder_path = THIS_DIR + '/hold_data/' + folder_name
            os.mkdir(hold_folder_path)
            with tarfile.open(name=file, mode='r:bz2') as tar_file:
                tar_file.extractall(path=hold_folder_path)
                xml_split = glob.glob(hold_folder_path + '/*.xml')
                for xml_doc in xml_split:
                    process_xml_file(xml_doc, grant_year_GBD, csv_writer, folder_name)
            shutil.rmtree(hold_folder_path)


def process_xml_file(xml_doc, grant_year_GBD, csv_writer, folder_name):
    '''
    '''
    us_inventor = 0
    try:
        root = etree.parse(xml_doc, parser=magic_validator)
    except Exception as e:
        print('Problem parsing ' + xml_doc + ' in ' + folder_name + ' with error ' + str(e))
        return

    def find_a_us_inventor(path_alt1, path_alt2, rel_path_state):
        '''
        '''
        nonlocal us_inventor
        path_applicants = ''
        if root.find(path_alt1) is not None:
            path_applicants = path_alt1
        elif path_alt2:
            if root.find(path_alt2) is not None:
                path_applicants = path_alt2
        if path_applicants:
            applicants = root.findall(path_applicants)
            if applicants:
                for applicant in applicants:
                    applicant_state = ''
                    try:
                        applicant_state = applicant.find(rel_path_state).text
                        if applicant_state:
                            us_inventor = 1
                            break
                    except Exception:  # not a US inventor
                        pass

    all_xml_paths = metadata_xml_paths(grant_year_GBD)
    path_patent_number = all_xml_paths[0]
    path_grant_date = all_xml_paths[1]
    path_app_date = all_xml_paths[2]
    path_applicants_alt1 = all_xml_paths[3]
    path_applicants_alt2 = all_xml_paths[4]
    path_inventors_alt1 = all_xml_paths[5]
    path_inventors_alt2 = all_xml_paths[6]
    path_assignees = all_xml_paths[7]
    rel_path_inventors_state = all_xml_paths[8]
    rel_path_applicants_state = all_xml_paths[8]

    try:  # to get patent number
        xml_patent_number = root.find(path_patent_number).text
        xml_patent_number, patent_number = clean_patnum(xml_patent_number)
    except Exception:  # no point in going on
        return
    # I hand fixed some files and want the grant year from the XML
    # for these, otherwise take the grant year from the folder name
    grant_year = grant_year_GBD
    hand_fixed = re.match(r'fix', folder_name)
    if (hand_fixed and hand_fixed.group(0) == 'fix'):
        try:  # to get the application date
            grantDate = root.find(path_grant_date).text.upper()
            grant_year = str(datetime.strptime(grantDate, dateFormat).year)
        except Exception:
            grant_year = grant_year_GBD
            pass
    appDate = ''
    appYear = ''
    try:  # to get the application date
        appDate = root.find(path_app_date).text
        appYear = str(datetime.strptime(appDate, dateFormat).year)
    except Exception:
        appYear = ''
        pass
    assignees = root.findall(path_assignees)
    if not assignees:  # Self-assigned
        number_assignees = 0
    else:
        number_assignees = len(assignees)
    # US inventors?
    find_a_us_inventor(path_applicants_alt1, path_applicants_alt2, rel_path_applicants_state)
    if grant_year_GBD >= 2005:  # USPTO changing their way of entering information
        find_a_us_inventor(path_inventors_alt1, path_inventors_alt2, rel_path_inventors_state)
    csv_line = []
    csv_line.append(xml_patent_number)
    csv_line.append(grant_year)
    csv_line.append(appYear)
    csv_line.append(number_assignees)
    csv_line.append(us_inventor)
    csv_writer.writerow(csv_line)


def make_patent_metadata(xml_files, NUMBER_OF_PROCESSES):
    '''
    '''
    files = glob.glob(os.path.join(xml_files, '*.bz2'))
    files_list = split_seq(files, NUMBER_OF_PROCESSES)
    p = Pool(NUMBER_OF_PROCESSES)
    p.map(get_info, files_list)
