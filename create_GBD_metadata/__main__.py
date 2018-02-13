# -*- coding: utf-8 -*-

import os, shutil, subprocess

base_dir = "create_GBD_metadata"
cw_dir = os.getcwd()
fp_dir = cw_dir + "/" + base_dir

print "Creating City misspellings file..."
cd_str = """{FP}/pythonCode/cleanCityNames/""".format(FP = fp_dir)
os.chdir(cd_str)
subprocess.call(["perl", "cleanCityNames.pl"])
print "Finished"

print "Creating Inventor names file..."
cd_str = """{FP}/pythonCode/inventorNames/""".format(FP = fp_dir)
os.chdir(cd_str)
subprocess.call(["perl", "inventorNames.pl"])
print "Finished"

os.chdir(cw_dir)
print "Creating Zip Codes file..."
process_data = """
python -m {BD}.pythonCode.zip3Data.usgs_geonames.process_data
""".format(BD = base_dir)
os.system(process_data)

parse_post_offices = """
python -m {BD}.pythonCode.zip3Data.parse_post_offices \
post_offices/
""".format(BD = base_dir)
os.system(parse_post_offices)

'''
parser = """
python -m {BD}.pythonCode.zip3Data.parser \
sparql_query_results.csv \
infobox_properties_en.nt
""".format(BD = base_dir)
os.system(parser)
'''

zip3_cities = """
python -m {BD}.pythonCode.zip3Data.zip3_cities
""".format(BD = base_dir)
os.system(zip3_cities)

city_xslt = """
python -m {BD}.pythonCode.zip3Data.city_xslt
""".format(BD = base_dir)
os.system(city_xslt)

shutil.move(base_dir + "/pythonCode/inventorNames/inventors.xml", base_dir)
shutil.move(base_dir + "/pythonCode/cleanCityNames/cityMisspellings.xml", base_dir)
shutil.move(base_dir + "/pythonCode/zip3Data/zip3_cities.xml", base_dir + "/UTF8_zip3_cities.xml")
os.remove(base_dir + "/pythonCode/zip3Data/us_towns.csv")
os.remove(base_dir + "/pythonCode/zip3Data/post_office_zips.csv")
os.remove(base_dir + "/pythonCode/zip3Data/usgs_zcta5.csv")
os.remove(base_dir + "/pythonCode/zip3Data/hold_zip3_cities.xml")

zip3_final = """
iconv -f UTF8 -t ASCII//TRANSLIT < {BD}/UTF8_zip3_cities.xml > {BD}/ASCII_zip3_cities.xml
""".format(BD = base_dir, CD = cw_dir)
os.system(zip3_final)
print "Finished"

