# -*- coding: utf-8 -*-

"""
This gets City/State and zip information from post office addresses.
Call it like:
./parse_post_offices.py post_offices/
The data files are the raw html code from webpmt.usps.gov where you
can locate every post office grouped by state, right-click to 
"View Page Source" and then save the resulting html code.  The HTML code 
is a mess and I can't guarantee the paths below will always hold true 
in the future.

Paths to zip and City (the first instance of that path):
html.body.td.table.tr.td.table.tr.td.a
html.body.td.table.tr.td.table.tr.td
"""
import codecs, os, sys
from lxml import etree

file_dir = os.path.dirname(os.path.relpath(__file__))
os.chdir(file_dir)

abbrevs = {
    "ALABAMA": "AL",
    "ALASKA": "AK",
    "ARIZONA": "AZ",
    "ARKANSAS": "AR",
    "CALIFORNIA": "CA",
    "COLORADO": "CO",
    "CONNECTICUT": "CT",
    "DELAWARE": "DE",
    "FLORIDA": "FL",
    "GEORGIA": "GA",
    "HAWAII": "HI",
    "IDAHO": "ID",
    "ILLINOIS": "IL",
    "INDIANA": "IN",
    "IOWA": "IA",
    "KANSAS": "KS",
    "KENTUCKY": "KY",
    "LOUISIANA": "LA",
    "MAINE": "ME",
    "MARYLAND": "MD",
    "MASSACHUSETTS": "MA",
    "MICHIGAN": "MI",
    "MINNESOTA": "MN",
    "MISSISSIPPI": "MS",
    "MISSOURI": "MO",
    "MONTANA": "MT",
    "NEBRASKA": "NE",
    "NEVADA": "NV",
    "NEW_HAMPSHIRE": "NH",
    "NEW_JERSEY": "NJ",
    "NEW_MEXICO": "NM",
    "NEW_YORK": "NY",
    "NORTH_CAROLINA": "NC",
    "NORTH_DAKOTA": "ND",
    "OHIO": "OH",
    "OKLAHOMA": "OK",
    "OREGON": "OR",
    "PENNSYLVANIA": "PA",
    "RHODE_ISLAND": "RI",
    "SOUTH_CAROLINA": "SC",
    "SOUTH_DAKOTA": "SD",
    "TENNESSEE": "TN",
    "TEXAS": "TX",
    "UTAH": "UT",
    "VERMONT": "VT",
    "VIRGINIA": "VA",
    "WASHINGTON": "WA",
    "WEST_VIRGINIA": "WV",
    "WISCONSIN": "WI",
    "WYOMING": "WY"
}

encoding = 'utf-8'

# Start processing
pathToData = sys.argv[1]
csv_file = codecs.open("post_office_zips.csv", 'w', encoding=encoding)
    
for (state, abbrev) in sorted(abbrevs.items()):
    parser = etree.HTMLParser()
    file_name = pathToData + state + ".html"
    html_doc = etree.parse(open(file_name), parser)
    path_info = "/body/table/tr/td/table/tr/td/table/tr/td//a[@alt]/../.."
    data = html_doc.findall(path_info)
    for office in data:
        zip_code = office[0][0].text.strip()
        city = office[1].text.strip()
        if zip_code and city:
            out_line = "|".join([city, abbrev, zip_code[0:3]])
            csv_file.write(out_line + "\n")

csv_file.close()

    