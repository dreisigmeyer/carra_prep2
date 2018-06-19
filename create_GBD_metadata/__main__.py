# -*- coding: utf-8 -*-

import json, xmltodict, os, subprocess

def zips_xml_to_json(xml_file, json_file):
    """
    This is to change the XML file to a JSON
    """
    with open(xml_file) as f:
        zips = xmltodict.parse(f.read())
    zip_dict = dict()
    for state in zips['states']['state']:
        abbrev = state['@abbrev']
        zip_dict[abbrev] = dict()
        for city in state['zip3']:
            cty = city['@city']
            zip = city['#text']
            if cty in zip_dict[abbrev]:
                zip_dict[abbrev][cty].append(zip)
            else:
                zip_dict[abbrev][cty] = []
                zip_dict[abbrev][cty].append(zip)
    with open(json_file, 'w') as fp:
        json.dump(zip_dict, fp, indent=8, sort_keys=True)

base_dir = "create_GBD_metadata"
cw_dir = os.getcwd()
fp_dir = cw_dir + "/" + base_dir

# print "Creating City misspellings file..."
cd_str = """{FP}/pythonCode/cleanCityNames/""".format(FP = fp_dir)
os.chdir(cd_str)
subprocess.call(["perl", "cleanCityNames.pl"])
# print "Finished"

# print "Creating Inventor names file..."
cd_str = """{FP}/pythonCode/inventorNames/""".format(FP = fp_dir)
os.chdir(cd_str)
subprocess.call(["perl", "inventorNames.pl"])
# print "Finished"

os.chdir(cw_dir)
# print "Creating Zip Codes file..."
process_data = """
python -m {BD}.pythonCode.zip3Data.usgs_geonames.process_data
""".format(BD = base_dir)
os.system(process_data)

parse_post_offices = """
python -m {BD}.pythonCode.zip3Data.parse_post_offices \
post_offices/
""".format(BD = base_dir)
os.system(parse_post_offices)

parser = """
python -m {BD}.pythonCode.zip3Data.parser \
sparql_query_results.csv \
infobox_properties_en.nt
""".format(BD = base_dir)
os.system(parser)

zip3_cities = """
python -m {BD}.pythonCode.zip3Data.zip3_cities
""".format(BD = base_dir)
os.system(zip3_cities)

city_xslt = """
python -m {BD}.pythonCode.zip3Data.city_xslt
""".format(BD = base_dir)
os.system(city_xslt)

os.remove(base_dir + "/pythonCode/zip3Data/us_towns.csv")
os.remove(base_dir + "/pythonCode/zip3Data/post_office_zips.csv")
os.remove(base_dir + "/pythonCode/zip3Data/usgs_zcta5.csv")
os.remove(base_dir + "/pythonCode/zip3Data/hold_zip3_cities.xml")
# os.remove(base_dir + "/pythonCode/zip3Data/zip3_cities.xml")

zip3_final = """
iconv -f UTF-8 -t ASCII//TRANSLIT < {BD}/zip3_cities.xml > {BD}/ASCII_zip3_cities.xml
""".format(BD = base_dir, CD = cw_dir)
os.system(zip3_final)
os.remove(base_dir + "/zip3_cities.xml")
zips_xml_to_json(base_dir + "/ASCII_zip3_cities.xml", base_dir + "/zip3_cities.json")
os.remove(base_dir + "/ASCII_zip3_cities.xml")

# print "Finished"

