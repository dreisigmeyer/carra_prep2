# -*- coding: utf-8 -*-

"""
This collects all of the City/State/Zip information together.
"""

import codecs, os
from ..helperFunctions import helper_funs as HF

file_dir = os.path.dirname(os.path.relpath(__file__))
os.chdir(file_dir)

encoding = 'utf-8'
free_zipcode = codecs.open("free-zipcode-database.csv", "r", encoding=encoding)
us_towns = codecs.open("us_towns.csv", "r", encoding=encoding)
additional_zips = codecs.open("../userData/additional_zips.csv", "r", encoding=encoding)
post_office_zips = codecs.open("post_office_zips.csv", "r", encoding=encoding)
usgs_zcta5 = codecs.open("usgs_zcta5.csv", "r", encoding=encoding)

zip_dict = {}

def process_file(file_handle, pop_first_line=False):
    '''
    Some of the files needed a trash line as their first line to make sure they
    were correctly saved as UTF-8 files instead of ASCII.  This was on RHEL 6
    and I could never figure out why this was happening.  The files have UTF-8
    characters in them...
    '''
    if pop_first_line:
        next(file_handle)
    for line in file_handle:
        city, state, zip_code = line.split('|')
        city = HF.clean_it(city)
        state = state.strip() # This should be capitalized abbreviations
        zip3 = zip_code[0:3]
        if state in zip_dict:
            if city in zip_dict[state]:
                zip_dict[state][city].update([zip3])
            else:
                zip_dict[state][city] = set([zip3])
        else:
            zip_dict[state] = {}
            zip_dict[state][city] = set([zip3])
            
process_file(free_zipcode)
process_file(us_towns, pop_first_line=True)
process_file(additional_zips)
process_file(post_office_zips)
process_file(usgs_zcta5, pop_first_line=True)

out_file = codecs.open("hold_zip3_cities.xml", "w", encoding=encoding)
out_file.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n")
out_file.write("<!--\n")
out_file.write("This comment is just to guarantee that this file is saved\n")
out_file.write("as UTF-8.  Without this it was continuously saved as ASCII\n")
out_file.write("even though it has UTF-8 characters in it.\n")
out_file.write(u"A UTF-8 character: Ñ")
out_file.write("-->\n")
out_file.write('<states>\n')
for state in sorted(zip_dict.iterkeys()):
    out_file.write('\t<state abbrev="' + state + '">\n')
    for city in sorted(zip_dict[state].iterkeys()):
        for zip3 in sorted(zip_dict[state][city]):
            out_line = '\t\t<zip3 city="' + city + '">' + zip3 + '</zip3>\n'
            out_file.write(out_line)
    out_file.write('\t</state>\n')
out_file.write("</states>\n")

