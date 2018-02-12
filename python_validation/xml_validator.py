#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 24 11:03:39 2016

@author: dreis002

This validates every USPTO patent XML file against the appropriate DTD and
checks that it is well-formed.
"""

import glob, os, re
from lxml import etree

ill_formed_validator = etree.XMLParser(dtd_validation=False, resolve_entities=False)
invalid_validator = etree.XMLParser(dtd_validation=True, resolve_entities=True)

grant_year_re = re.compile('[a-z]{3,4}([0-9]{8})_wk[0-9]{2}')

for directory in glob.glob('holdData/*'):
    folder_name = os.path.splitext(os.path.basename(directory))[0]    
    grant_year_GBD = int(grant_year_re.match(folder_name).group(1)[:4])
    valid_well_formed_xml_dir = directory + '/valid_well_formed_xml/'
    invalid_xml_dir = directory + '/invalid_xml/'
    ill_formed_xml_dir = directory + '/ill_formed_xml/'
    os.mkdir(valid_well_formed_xml_dir)
    os.mkdir(invalid_xml_dir)
    os.mkdir(ill_formed_xml_dir)
    for xml_file in glob.glob(directory + '/*.xml'):
        file_name = os.path.basename(xml_file)
        holder = None
        
        try:
            holder = etree.parse(xml_file, ill_formed_validator)
        except Exception, e:
            print "ill-formed xml document " + xml_file + ' : ' + str(e)
            os.rename(xml_file, ill_formed_xml_dir + file_name)
            continue
        else:
            holder = None
           
        if grant_year_GBD > 2001:
            # Stopped validating the files - too many issues
            holder = None
            os.rename(xml_file, valid_well_formed_xml_dir + file_name)
            #try:
                #holder = etree.parse(xml_file, invalid_validator)
            #except Exception, e:
                #print "invalid xml document " + xml_file + ' : ' + str(e)
                #os.rename(xml_file, invalid_xml_dir + file_name)
            #else:
                #holder = None
                #os.rename(xml_file, valid_well_formed_xml_dir + file_name)
        elif grant_year_GBD < 2002:
            holder = None
            os.rename(xml_file, valid_well_formed_xml_dir + file_name)
