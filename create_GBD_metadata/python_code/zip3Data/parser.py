# -*- coding: utf-8 -*-

"""
Parse the DBpedia dump.
"""

import codecs, os, re, sys
from subprocess import Popen, PIPE
from ..helperFunctions import helper_funs as HF

file_dir = os.path.dirname(os.path.relpath(__file__))
os.chdir(file_dir)

states = [
    "Alabama",
    "Alaska",
    "Arizona",
    "Arkansas",
    "California",
    "Colorado",
    "Connecticut",
    "Delaware",
    "Florida",
    "Georgia",
    "Hawaii",
    "Idaho",
    "Illinois",
    "Indiana",
    "Iowa",
    "Kansas",
    "Kentucky",
    "Louisiana",
    "Maine",
    "Maryland",
    "Massachusetts",
    "Michigan",
    "Minnesota",
    "Mississippi",
    "Missouri",
    "Montana",
    "Nebraska",
    "Nevada",
    "New_hampshire",
    "New_jersey",
    "New_mexico",
    "New_york",
    "North_carolina",
    "North_dakota",
    "Ohio",
    "Oklahoma",
    "Oregon",
    "Pennsylvania",
    "Rhode_island",
    "South_carolina",
    "South_dakota",
    "Tennessee",
    "Texas",
    "Utah",
    "Vermont",
    "Virginia",
    "Washington",
    "West_virginia",
    "Wisconsin",
    "Wyoming"
]

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
    "NEW HAMPSHIRE": "NH",
    "NEW JERSEY": "NJ",
    "NEW MEXICO": "NM",
    "NEW YORK": "NY",
    "NORTH CAROLINA": "NC",
    "NORTH DAKOTA": "ND",
    "OHIO": "OH",
    "OKLAHOMA": "OK",
    "OREGON": "OR",
    "PENNSYLVANIA": "PA",
    "RHODE ISLAND": "RI",
    "SOUTH CAROLINA": "SC",
    "SOUTH DAKOTA": "SD",
    "TENNESSEE": "TN",
    "TEXAS": "TX",
    "UTAH": "UT",
    "VERMONT": "VT",
    "VIRGINIA": "VA",
    "WASHINGTON": "WA",
    "WEST VIRGINIA": "WV",
    "WISCONSIN": "WI",
    "WYOMING": "WY"
}

sed_str="""sed '1d' sparql_query_results.csv |\\
sed 's/\\"\\"\\"//g' |\\
sed 's/\\"\\"^^<http:\\/\\/www.w3.org\\/2001\\/XMLSchema#integer>\\"//g' |\\
sed 's/\\"<http:\\/\\/dbpedia.org\\/resource\\///g' |\\
sed 's/>\\"//g' > ./holder.csv
"""
os.system(sed_str)
    
def process_line_sparql(in_line):
    """
    Puts the SPARQL query line into a different format
    """    
    line = in_line.split(',')    
    zip_code = line[0].strip()
    city = line[1].strip()    
    city = HF.clean_it(city)
    state = line[-1].strip()
    state = HF.clean_it(state)    
    abbrev = abbrevs[state]
    if len(zip_code) > 5:
        raise Exception('Zipcode is too long.')
    elif int(zip_code) < 500:
        raise Exception('Zipcode is too small.')
    else:
        zip3 = zip_code.zfill(5)[0:3]
        return '|'.join([city, abbrev, zip3])
    
def process_line_dbpedia(in_line):
    """
    Puts the DBpedia line into a different format
    """
    city_state = re.search('[^/]*(?=>)', in_line).group(0)
    city_array = city_state.split(',_')
    city = city_array[0]
    city = HF.clean_it(city)
    state = city_array[-1]
    state = HF.clean_it(state)    
    abbrev = abbrevs[state]        
    zip_code = re.search('(?<=").*(?="\^\^<http://www.w3.org/2001/XMLSchema#int>)', in_line).group(0)
    if len(zip_code) > 5:
        raise Exception('Zipcode is too long.')
    elif int(zip_code) < 500:
        raise Exception('Zipcode is too small.')
    else:
        zip3 = zip_code.zfill(5)[0:3]
        return '|'.join([city, abbrev, zip3])
  
encoding = 'utf-8'
out_file = codecs.open("to_remove.csv", "w", encoding=encoding)

# bring it in as a byte string to deal with the HTML encoding issues
in_file = codecs.open("holder.csv", "r", encoding=encoding)
for line in in_file:
    try:
        holder = process_line_sparql(line.strip())
    except Exception:
        continue
    out_file.write(holder + "\n")
in_file.close()

file_str = sys.argv[2]
for state in states:
    grep_str = state + ".*postalCode>.*<http://www.w3.org/2001/XMLSchema#int>"
    results = Popen(['grep', '-i', grep_str, file_str], stdout=PIPE).communicate()[0]
    for line in results.split('\n'):        
        try:
            holder = process_line_dbpedia(line)
        except Exception:        
            continue
        out_file.write(holder + "\n")
out_file.close()

'''
There were some major issues having things correctly save as utf-8 even
though they had utf-8 characters in them.  Having a line early in the file
with utf-8 characters in it took care of things?
'''
os.system('echo "A UTF-8 character to enforce saving the file as UTF-8: Ñ" > us_towns.csv')
os.system('sort -u to_remove.csv >> us_towns.csv')
os.system("rm holder.csv to_remove.csv")
