#!/apps/anaconda/bin/python
# -*- coding: utf-8 -*-

"""
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
"""

import codecs, csv, glob, os, re, sys, unicodedata
from lxml import etree
from datetime import datetime
from multiprocessing import Pool
from difflib import SequenceMatcher as SM
from random import shuffle

NUMBER_OF_PROCESSES = int(sys.argv[1])
cw_dir = os.getcwd()

"""
                BEGIN Function definitions
"""
def split_seq(seq, NUMBER_OF_PROCESSES):
    """
    Slices a list into NUMBER_OF_PROCESSES pieces
    of roughly the same size
    """    
    shuffle(seq) # don't want newer/older years going to a single process
    num_files = len(seq)
    if num_files < NUMBER_OF_PROCESSES:
        NUMBER_OF_PROCESSES = num_files
    size = NUMBER_OF_PROCESSES
    newseq = []
    splitsize = 1.0/size*num_files
    if NUMBER_OF_PROCESSES == 1:
        newseq.append(seq[0:])
        return newseq
    for i in range(size):
        newseq.append(seq[int(round(i*splitsize)):int(round((i+1)*splitsize))])
    return newseq

pat_num_re = re.compile(r'([A-Z]*)0*([0-9]+)')
def clean_patnum(patnum):
    """
    Removes extraneous zero padding
    """
    pat_num = patnum.strip().upper()
    try: # removes any zero padding and rejoins the patent number
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
    """
    Clean up the string
    """
    applicant_text = clean_it(applicant_text)
    # Replace utf-8 characters with their closest ascii
    applicant_text = unicodedata.normalize('NFKD', applicant_text)        
    applicant_text = applicant_text.encode('ascii', 'ignore')
    applicant_text = applicant_text.replace('&', ' AND ') # This needs to be in the names
    applicant_text = ' '.join(applicant_text.split())
    applicant_text = re.sub('[^a-zA-Z0-9 ]+', '', applicant_text).upper()
    return applicant_text.strip()
    
def get_assignee_info(assignee, xml_path):
    """
    """
    try:
        assignee_info = assignee.find(xml_path).text
        assignee_info = to_ascii(assignee_info)
    except Exception: # may have assignee name from USPTO DVD
        assignee_info = ''
    return assignee_info

dateFormat = '%Y%m%d' # The dates are expected in %Y%m%d format
# We'll use this to get the grant year from the GBD file name
grant_year_re = re.compile('[a-z]{3,4}([0-9]{8})_wk[0-9]{2}')

xml_validator = etree.XMLParser(dtd_validation=False, resolve_entities=False, encoding='utf8')

def get_info(files):
    for file in files:
        folder_name = os.path.splitext(os.path.basename(file))[0]    
        # Get data in and ready
        folder_path = cw_dir + "/holdData/" + folder_name + "/"
        os.system("mkdir " + folder_path)
        os.system("unzip -qq -o " + file + " -d " + folder_path)
        xmlSplit = glob.glob(folder_path + "/*.xml")
        out_file_name = os.path.splitext(os.path.basename(file))[0]
        csv_file = codecs.open("./outData/" + out_file_name + ".csv", 'w', 'ascii')
        csv_writer = csv.writer(csv_file, delimiter=',')
        
        grant_year_GBD = int(grant_year_re.match(folder_name).group(1)[:4])
        """
        These are the XML paths we use to extract the data.
        Note: if the path is rel_path_something_XXX then this is a path that is
        relative to the path given by path_something
        """
        if grant_year_GBD > 2004:
            # Theses paths are for 2005 - present
            path_patent_number = "us-bibliographic-data-grant/publication-reference/document-id/doc-number"
            path_grant_date = "us-bibliographic-data-grant/publication-reference/document-id/date"
            path_app_date = "us-bibliographic-data-grant/application-reference/document-id/date"
            path_assignees = "us-bibliographic-data-grant/assignees/"
            path_applicants_alt1 = "us-bibliographic-data-grant/parties/applicants/"
            path_applicants_alt2 = "us-bibliographic-data-grant/us-parties/us-applicants/"
            path_applicants = ""
            rel_path_applicants_state = "addressbook/address/state"
        elif 2001 < grant_year_GBD < 2005:
            # Theses paths are for 2002 - 2004
            path_patent_number = "SDOBI/B100/B110/DNUM/PDAT"
            path_grant_date = "SDOBI/B100/B140/DATE/PDAT"
            path_app_date = "SDOBI/B200/B220/DATE/PDAT"
            path_assignees = "SDOBI/B700/B730" # nodes B731 are all of the assignees
            path_applicants_alt1 = "SDOBI/B700/B720"
            path_applicants_alt2 = ""
            path_applicants = ""
            rel_path_applicants_state = "./B721/PARTY-US/ADR/STATE/PDAT"
        elif grant_year_GBD < 2002:
            # Theses paths are for pre-2002
            path_patent_number = "WKU"
            path_grant_date = "" # just use grant_year_GBD
            path_app_date = "APD"
            path_assignees = "ASSGS/"
            path_applicants_alt1 = "INVTS/"
            path_applicants_alt2 = ""
            path_applicants = ""
            rel_path_applicants_state = "STA"
        else:
            raise UserWarning("Incorrect grant year: " + str(grant_year))

        # Run the queries
        for xmlDoc in xmlSplit:
            root = etree.parse(xmlDoc, xml_validator)

            try: # to get patent number
                xml_patent_number = root.find(path_patent_number).text
                xml_patent_number, patent_number = clean_patnum(xml_patent_number)
            except Exception: # no point in going on
                continue

            # I hand fixed some files and want the grant year from the XML
            # for these, otherwise take the grant year from the folder name
            grantYear = grant_year_GBD
            handFixed = re.match(r'fix', folder_name)
            if (handFixed and handFixed.group(0) == 'fix'):
                try: # to get the application date
                    grantDate = root.find(path_grant_date).text.upper()  
                    grantYear = str(datetime.strptime(grantDate, dateFormat).year)
                except Exception:
                    grantYear = grant_year_GBD
                    pass
            
            appDate = ''
            appYear = ''
            try: # to get the application date
                appDate = root.find(path_app_date).text
                appYear = str(datetime.strptime(appDate, dateFormat).year)       
            except Exception:
                appYear = ''
                pass
            
            assignees = root.findall(path_assignees)        
            if not assignees: # Self-assigned
                number_assignees = 0            
            else:
                number_assignees = len(assignees)

            # US inventors?
            us_inventor = 0
            if root.find(path_applicants_alt1) is not None:
                path_applicants = path_applicants_alt1
            elif root.find(path_applicants_alt2) is not None:
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
                        except Exception: # not a US inventor
                            continue
            csv_line = []
            csv_line.append(xml_patent_number)
            csv_line.append(grantYear)
            csv_line.append(appYear)
            csv_line.append(number_assignees)
            csv_line.append(us_inventor)
            csv_writer.writerow(csv_line)

        # Clean things up
        csv_file.close()
        os.system("rm -rf " + folder_path)
"""
                END Function definitions
"""

# Start processing
pathToData = './inData/'
files = glob.glob(os.path.join(pathToData, "*.zip"))
files_list = split_seq(files, NUMBER_OF_PROCESSES)
if __name__ == '__main__':
    p = Pool(NUMBER_OF_PROCESSES)
    p.map(get_info, files_list)

    
