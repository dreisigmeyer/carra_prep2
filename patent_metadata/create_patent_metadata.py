#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
The patent bulk download data (from Google or USPTO) should be cleaned with
the GBD_data_cleaner before being used here.  That removes HTML entities and
performs other cleaning on the XML files.

This outputs PRDN meta-data.  The format is:
xml_pat_num,grant_yr,app_yr,num_assgs,us_inventor_flag


To run this make this file executable and do:
    ./create_patent_metadata.py num_of_processes
num_of_processes >=1 is the number of individual Python processes to run.

The XML paths are given below for the Google bulk download.  Make
sure they haven't changed if you have problems.

Created by David W. Dreisigmeyer 23 Feb 17
'''

import codecs
import csv
from datetime import datetime
import glob
from lxml import etree
from multiprocessing import Pool
import os
from random import shuffle
import re
import sys
import unicodedata

NUMBER_OF_PROCESSES = int(sys.argv[1])
cw_dir = os.getcwd()
pat_num_re = re.compile(r'([A-Z]*)0*([0-9]+)')
dateFormat = '%Y%m%d'  # The dates are expected in %Y%m%d format
# We'll use this to get the grant year from the GBD file name
grant_year_re = grant_year_re = re.compile('i?pgb([0-9]{4})')
magic_validator = etree.XMLParser(
    dtd_validation=True,
    resolve_entities=False,
    encoding='utf-8',
    recover=True)


def split_seq(seq, NUMBER_OF_PROCESSES):
    '''
    Slices a list into NUMBER_OF_PROCESSES pieces
    of roughly the same size
    '''
    shuffle(seq)  # don't want newer/older years going to a single process
    num_files = len(seq)
    if num_files < NUMBER_OF_PROCESSES:
        NUMBER_OF_PROCESSES = num_files
    size = NUMBER_OF_PROCESSES
    newseq = []
    splitsize = 1.0 / size * num_files
    if NUMBER_OF_PROCESSES == 1:
        newseq.append(seq[0:])
        return newseq
    for i in range(size):
        newseq.append(seq[int(round(i * splitsize)):int(round((i + 1) * splitsize))])
    return newseq


def clean_patnum(patnum):
    '''
    Removes extraneous zero padding
    '''
    pat_num = patnum.strip().upper()
    try:  # removes any zero padding and rejoins the patent number
        hold_pat_num = pat_num_re.match(pat_num).groups()
        pat_num_len = len(hold_pat_num[0] + hold_pat_num[1])
        zero_padding = '0' * (7 - pat_num_len)
        pat_num = hold_pat_num[0] + zero_padding + hold_pat_num[1]
        zero_padding = '0' * (8 - pat_num_len)
        xml_pat_num = hold_pat_num[0] + zero_padding + hold_pat_num[1]
    except Exception:
        pass
    return xml_pat_num, pat_num


def clean_it(in_str):
    if isinstance(in_str, str):
        encoded_str = in_str.decode('unicode_escape')
    out_str = encoded_str
    return out_str


def to_ascii(applicant_text):
    '''
    Clean up the string
    '''
    applicant_text = clean_it(applicant_text)
    # Replace utf-8 characters with their closest ascii
    applicant_text = unicodedata.normalize('NFKD', applicant_text)
    applicant_text = applicant_text.encode('ascii', 'ignore')
    applicant_text = applicant_text.replace('&', ' AND ')  # This needs to be in the names
    applicant_text = ' '.join(applicant_text.split())
    applicant_text = re.sub('[^a-zA-Z0-9 ]+', '', applicant_text).upper()
    return applicant_text.strip()


def get_assignee_info(assignee, xml_path):
    '''
    '''
    try:
        assignee_info = assignee.find(xml_path).text
        assignee_info = to_ascii(assignee_info)
    except Exception:  # may have assignee name from USPTO DVD
        assignee_info = ''
    return assignee_info


def get_info(files):
    for file in files:
        folder_name = os.path.basename(file).split('.')[0]
        # Get data in and ready
        folder_path = cw_dir + '/holdData/' + folder_name + '/'
        os.system('mkdir ' + folder_path)
        os.system('tar -xf ' + file + ' -C ' + folder_path + ' --strip-components=1')
        xml_split = glob.glob(folder_path + '/*.xml')
        out_file_name = os.path.basename(file).split('.')[0]
        csv_file = codecs.open('./outData/' + out_file_name + '.csv', 'w', 'ascii')
        csv_writer = csv.writer(csv_file, delimiter=',')
        grant_year_GBD = int(grant_year_re.match(folder_name).group(1))
        '''
        These are the XML paths we use to extract the data.
        Note: if the path is rel_path_something_XXX then this is a path that is
        relative to the path given by path_something
        '''
        if grant_year_GBD > 2004:
            # Theses paths are for 2005 - present
            path_patent_number = 'us-bibliographic-data-grant/publication-reference/document-id/doc-number'
            path_grant_date = 'us-bibliographic-data-grant/publication-reference/document-id/date'
            path_app_date = 'us-bibliographic-data-grant/application-reference/document-id/date'
            path_assignees = 'us-bibliographic-data-grant/assignees/'
            path_applicants_alt1 = 'us-bibliographic-data-grant/parties/applicants/'
            path_applicants_alt2 = 'us-bibliographic-data-grant/us-parties/us-applicants/'
            path_applicants = ''
            rel_path_applicants_state = 'addressbook/address/state'
            path_inventors_alt1 = 'us-bibliographic-data-grant/parties/inventors/'
            path_inventors_alt2 = 'us-bibliographic-data-grant/us-parties/inventors/'
            path_inventors = ''
            rel_path_inventors_state = 'addressbook/address/state'
        elif 2001 < grant_year_GBD < 2005:
            # Theses paths are for 2002 - 2004
            path_patent_number = 'SDOBI/B100/B110/DNUM/PDAT'
            path_grant_date = 'SDOBI/B100/B140/DATE/PDAT'
            path_app_date = 'SDOBI/B200/B220/DATE/PDAT'
            path_assignees = 'SDOBI/B700/B730'  # nodes B731 are all of the assignees
            path_applicants_alt1 = 'SDOBI/B700/B720'
            path_applicants_alt2 = ''
            path_applicants = ''
            rel_path_applicants_state = './B721/PARTY-US/ADR/STATE/PDAT'
        elif grant_year_GBD < 2002:
            # Theses paths are for pre-2002
            path_patent_number = 'WKU'
            path_grant_date = 'ISD'
            path_app_date = 'APD'
            path_assignees = 'assignees/'
            path_applicants_alt1 = 'inventors/'
            path_applicants_alt2 = ''
            path_applicants = ''
            rel_path_applicants_state = 'STA'
        else:
            raise UserWarning('Incorrect grant year: ' + str(grant_year_GBD))
        # Run the queries
        for xml_doc in xml_split:
            try:
                root = etree.parse(xml_doc, parser=magic_validator)
            except Exception as e:
                print('Problem parsing ' + xml_doc + ' in ' + folder_name + ' with error ' + str(e))
                continue
            try:  # to get patent number
                xml_patent_number = root.find(path_patent_number).text
                xml_patent_number, patent_number = clean_patnum(xml_patent_number)
            except Exception:  # no point in going on
                continue
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
            us_inventor = 0
            if root.find(path_applicants_alt1) is not None:
                path_applicants = path_applicants_alt1
            elif path_applicants_alt2:
                if root.find(path_applicants_alt2) is not None:
                    path_applicants = path_applicants_alt2

            if path_applicants:
                applicants = root.findall(path_applicants)
                if applicants:
                    for applicant in applicants:
                        applicant_state = ''
                        try:
                            applicant_state = applicant.find(rel_path_applicants_state).text
                            if applicant_state:
                                us_inventor = 1
                                break
                        except Exception:  # not a US inventor
                            continue
            if grant_year_GBD > 2004:  # USPTO changing their way of entering information
                if root.find(path_inventors_alt1) is not None:
                    path_inventors = path_inventors_alt1
                elif root.find(path_inventors_alt2) is not None:
                    path_inventors = path_inventors_alt2
                if path_inventors:
                    inventors = root.findall(path_inventors)
                    if inventors:
                        for inventor in inventors:
                            inventor_state = ''
                            try:
                                inventor_state = inventor.find(rel_path_inventors_state).text
                                if inventor_state:
                                    us_inventor = 1
                                    break
                            except Exception:  # not a US inventor
                                continue
            csv_line = []
            csv_line.append(xml_patent_number)
            csv_line.append(grant_year)
            csv_line.append(appYear)
            csv_line.append(number_assignees)
            csv_line.append(us_inventor)
            csv_writer.writerow(csv_line)
        # Clean things up
        csv_file.close()
        os.system('rm -rf ' + folder_path)


# Start processing
pathToData = './inData/'
files = glob.glob(os.path.join(pathToData, '*.bz2'))
files_list = split_seq(files, NUMBER_OF_PROCESSES)
if __name__ == '__main__':
    p = Pool(NUMBER_OF_PROCESSES)
    p.map(get_info, files_list)
