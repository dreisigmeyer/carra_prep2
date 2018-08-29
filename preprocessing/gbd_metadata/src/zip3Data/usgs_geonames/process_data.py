# -*- coding: utf-8 -*-

import codecs
import os
from ...helperFunctions import helper_funs as HF

file_dir = os.path.dirname(os.path.relpath(__file__))
os.chdir(file_dir)

"""
This is data from http://geonames.usgs.gov/domestic/download_data.htm "All Names" and gives us:

FEATURE_ID|FEATURE_NAME

** FEATURE_ID:
Permanent, unique feature record identifier and official feature name as defined in INCITS 446-2008
** FEATURE_NAME:
Permanent official feature name as defined in INCITS 446-2008 as well as alternate spellings

"""
# awk -F'|' -v OFS='|' '{print $1, $2}' AllNames_*.txt > alternate_names.csv && \ # replace with cut
alias_cmd = """
cut -d'|' -f1,2 AllNames_*.txt > alternate_names.csv && \
sed -i '1d' alternate_names.csv && \
sed -i 's/Census Designated Place//g' alternate_names.csv
"""
os.system(alias_cmd)

"""
This is data from geonames.usgs.gov/domestic/download_data.htm "AllStateFedCodes" and gives us:

GEOID|FEATURE_ID|STATE_ALPHA|FEATURE_NAME|FIPS

** STATE_NUMERIC (State FIPS) + CENSUS_CODE (Place FIPS):
The unique two number code for a US State as specified in INCITS 38:200x, (Formerly FIPS 5-2)
The unique two number code and the unique two letter alphabetic code for a US State as specified in
INCITS 38:200x, (Formerly FIPS 5-2)
The two combined give us the GEOID (see below)
** FEATURE_ID:
Permanent, unique feature record identifier and official feature name as defined in INCITS 446-2008
** STATE_ALPHA:
The unique two letter alphabetic code for a US State as specified in INCITS 38:200x, (Formerly FIPS 5-2)
** FEATURE_NAME:
Permanent official feature name as defined in INCITS 446-2008
** STATE_NUMERIC (State FIPS) + COUNTY_NUMERIC (County FIPS):
The unique two number code for a US State as specified in INCITS 38:200x, (Formerly FIPS 5-2)
The unique three number code for a county or county equivalent as specified in INCITS 31:200x,
(Formerly FIPS 6-4)
Combined these give us the unique FIPS code for the county
"""
names_cmd = """
awk -F'|' -v OFS='|' '{print $8 $4, $1, $9, $2, $8 $11}' ./states/*_FedCodes_* > codes_names_states.csv && \
sed -i '1d' codes_names_states.csv && \
sed -i 's/Census Designated Place//g' codes_names_states.csv
"""
os.system(names_cmd)

"""
This is data from www.census.gov/geo/maps-data/data/relationship.html "ZCTA Relationship File"
and gives us:

GEOID|ZCTA5

** GEOID:
See STATE_NUMERIC (State FIPS) + CENSUS_CODE (Place FIPS) above
** ZCTA5:
Census ZCTA for 2010
"""
zcta5_cmd = """
awk -F',' -v OFS='|' '{print $5, $1}' zcta_place_rel_10.txt > geoid_to_zcta5_2010.csv && \
sed -i '1d' geoid_to_zcta5_2010.csv && \
sed -i 's/Census Designated Place//g' geoid_to_zcta5_2010.csv
"""
os.system(zcta5_cmd)

encoding = 'utf-8'

in_file = codecs.open("geoid_to_zcta5_2010.csv", "r", encoding=encoding)
geoid_to_zcta5 = {}  # We need the geoids to link up different files
for line in in_file:
    geoid, zcta5 = line.split('|')
    geoid_to_zcta5[geoid] = zcta5[0:3]
in_file.close()

in_file = codecs.open("codes_names_states.csv", "r", encoding=encoding)
geoid_info = {}
fips_zip3s = {}  # all of the zips in a county
feature_to_geo_id = {}  # also to link up different data files
for line in in_file:
    geoid, feature_id, state, name, fips = line.split('|')
    clean_name = HF.clean_it(name)
    if geoid in geoid_to_zcta5:  # get all of the zip3s in a county
        zip3 = geoid_to_zcta5[geoid]
        try:
            fips_zip3s[fips].update([zip3])
        except Exception:
            fips_zip3s[fips] = set([zip3])
    feature_to_geo_id[feature_id] = geoid
    geoid_info[geoid] = {}
    geoid_info[geoid]['state'] = state
    geoid_info[geoid]['name'] = set([clean_name])
    geoid_info[geoid]['fips'] = fips
in_file.close()

in_file = codecs.open("alternate_names.csv", "r", encoding=encoding)
for line in in_file:
    feature_id, name = line.split('|')
    clean_name = HF.clean_it(name)
    if feature_id in feature_to_geo_id:
        geoid = feature_to_geo_id[feature_id]
        geoid_info[geoid]['name'].update([clean_name])
in_file.close()

out_file = codecs.open("usgs_zcta5.csv", "w", encoding=encoding)

'''
There were some major issues having things correctly save as utf-8 even
though they had utf-8 characters in them.  Having a line early in the file
with utf-8 characters in it took care of things?
'''
out_file.write(u"A UTF-8 character to enforce saving the file as UTF-8: Ñ\n")

for geoid in geoid_info:
    state = geoid_info[geoid]['state']
    if geoid in geoid_to_zcta5:
        zip3 = geoid_to_zcta5[geoid]
        for name in geoid_info[geoid]['name']:
            holder = '|'.join([name, state, zip3])
            out_file.write(holder + "\n")
    else:
        fips = geoid_info[geoid]['fips']
        if fips in fips_zip3s:
            for zip3 in fips_zip3s[fips]:
                for name in geoid_info[geoid]['name']:
                    holder = '|'.join([name, state, zip3])
                    out_file.write(holder + "\n")
out_file.close()

os.system("mv usgs_zcta5.csv ../")
os.system("rm alternate_names.csv")
os.system("rm codes_names_states.csv")
os.system("rm geoid_to_zcta5_2010.csv")
