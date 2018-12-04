## Getting the data
1.	If you don't have git-lfs you'll need to download:
    * The "All Names" file from the Topical Gazetteers from 
    https://geonames.usgs.gov/domestic/download_data.htm.
    Unzip it and place it in **preprocessing/gbd_metadata/src/zip3Data/usgs_geonames/**.
    There may be some issues with null bytes in the "All Names" file.
    It is suggested to run  
    `tr < AllNames_*.txt -d '\000' > holder`  
    and then replace the "All Names" file with _holder_.
    The included _AllNames\_*.txt_ has been preprocessed.
    * The _INV\_COUNTY\_YY\_YY.TXT_ and _INVENTOR\_YY.TXT_ files from the USPTO's patent data DVD.
    These files are placed in **preprocessing/gbd_metadata/data/uspto_data/**.

2.	If you do have git-lfs and pulled this for the first time from this directory you'll need to 
    run  
    `bzip2 -dk preprocessing/gbd_metadata/data/uspto_data/INV_COUNTY_*.TXT.bz2`  
    `bzip2 -dk preprocessing/gbd_metadata/data/uspto_data/INVENTOR_*.TXT.bz2`  
	`bzip2 -dk preprocessing/gbd_metadata/src/zip3Data/usgs_geonames/*.txt.bz2`  
	If the bzip files change you'll need to rerun this.

3.	In **dat_to_xml** and **xml_rewrite** run  
	`./get_uspto_data.sh`  
	which will download the required data from the USPTO website.
	Verify the files downloaded correctly to the directories
	**dat_to_xml/dat_files** and 
	**xml_rewrite/rewriter/raw_xml_files**.


## Setting up the Python environment
The code was run with a standard Anaconda Python 3 environment (https://www.anaconda.com).


## Running the code
After getting the data and setting up the Python environment,
the entire process that follows can be run with the convenience script  
`nohup ./doitall.sh number_of_threads_to_use &`  
* The outputs in **outputs/for_carra/** are post-processed and then sent to CARRA for PIKing.
* The file _metadata.csv_ in **outputs/csv_output/** is used later for triangulation.
* From **outputs/json_output** the files
_city\_state\_to\_zip3.json_,
_city\_mispellings.json_,
_inventors.json_ and
_close_city_spellings.json_
are also used later.
* **outputs/xml_output** contains the XML data where we have **xml_with_inventors/** and
**xml_without_inventors/**.


## The individual pieces of the code
1.	See the _README.md_ in **dat_to_xml**.  
	> This doesn't depend on any other piece of the code.

2.	See the _README.md_ in **xml_rewrite**.  
	> This doesn't depend on any other piece of the code.

3.	The **preprocessing** module collects together patent metadata and prepares the dat
	XML files for sending to CARRA.
	Many of the intermediate files may be of value as well.
-	**gbd_metadata** is run to generate JSON files
	for attaching zip3s, and correcting city-state and inventor information.
	The files in **outputs/json_output/** are  
	_zip3\_cities.json_,  
	_city_mispellings.json_: contains various misspellings of city+state combinations,  
	_inventors.json_ : contains all city+state combinations for inventors base on last, 
	first and middle names and  
	_close_city_spellings.json_
	> This doesn't depend on any other piece of the code.  
	
The class and functions provided in **make_gdb_metadata.py** are:
```
SetEncoder(json.JSONEncoder):
	To export the sets in CLOSE_CITY_SPELLINGS.
```
```
init_close_city_spellings(zip_file, city_file):
	Creates CLOSE_CITY_SPELLINGS

	zip_file -- JSON file of city+state to zip3s
	city_file -- JSON file of aliases/misspellings of city names
```
```
make_gbd_metadata(xml_files):
	Generates the patent metadata from the USPTO XML files

	xml_files -- path to XML files
```

The functions provided in **src/city_names.py** are:
```
add_to_inventors_dict(prdn, inv_seq, state, city, alias=False):
	Add city misspelling information to global dictionary

	prdn -- patent number
	inv_seq -- inventor sequence number
	state -- state the city is located in
	city -- city name
	alias -- find an alternate spelling of city (default False)?
```
```
add_to_cities_dict(state, city, alias):
	Add city misspelling information to global dictionary

	state -- state the city is located in
	city -- city name
	alias -- alternate spelling of city
```
```
create_city_json(working_dir):
	Maps state+city to potential aliases/misspellings of the city name

	working_dir -- path to input data
```

The functions provided in **src/city_state_to_zip3.py** are:
```
create_abbreviations(line):
	Expands abbreviations or creates them

	line -- string to work on
```
```
csv_reader_skip_headers(in_file, delimiter=','):
	Returnes a csv reader skipping over the header line.

	in_file -- name of the file to read in
	delimiter -- (Default ',')
```
```
process_state_html(file):
	Gets zips out of the USPS HTML

	file -- file name to process
```
```
read_zcta_line(line):
	This maps the geoid to zip3s.

	line -- string to process
```
```
read_states_line(line):
	This collects together state information.

	line -- string to process
```
```
read_sparql_line(line):
	Reads in a SPARQL query result

	line -- string to process
```
```
read_dbpedia_line(line):
	Reads in a line from the DBPedia dataset

	line -- string to process
```
```
read_other_line(line):
	Generic processing of a string

	line -- string to process
```
```
read_allname_line(line):
	This collects alternate names for each geoid.

	line -- string to process
```
```
state_city_to_zip3():
	Creates the city+state to zip3 mapping.
```
```
update_zip3_mapping(state, name, zip3):
	Add new zip3 to dictionary

	state -- state the zip3 is in
	name -- city name of the zip3
	zip3 -- the zip3
```
```
create_zip3_mapping(working_dir):
	Main programm to create the city+state to zip3 mappings

	working_dir -- location of data files
```

The functions provided in **src/inventor_names.py** are:
```
add_to_inventors_dict(ln, fn, mn, city, state):
	Add applicant information to global dictionary

	ln -- inventor's last name
	fn -- inventor's first name
	mn -- inventor's middle name
	city -- inventor's city on the patent
	state -- inventor's state on the patent
```
```
create_inventor_json(directories, working_dir):
	Creates the JSON file of inventor information that is used for
	auto-correcting inventor city+state information

	directories -- location of bz2 XML files
	working_dir -- location where intermediate working files should be put
```
```
xml_to_json_doc(xml_doc, grant_year):
	Takes information from the XML files and places it into JSON format

	xml_doc -- name of the XML file that's being processed
	grant_year -- grant year of patent
```
-	**carra_files** prepares the inventor data to be shipped to CARRA for PIKing.
	In particular, this attempts to:
	* correct any misspellings of the city and/or state;
	* assign prior city and states to inventors;
	* attach zip3s to the inventors' cities.  
	The resulting files in **outputs/for_carra/** are post-processed and then sent to CARRA for 
	PIKing.  
	> This depends on the output of **create_GBD_metadata**, **dat_to_xml** and **xml_rewrite**.  

The functions provided in **make_carra_files.py** are:
```
make_carra_files(xml_files, NUMBER_OF_PROCESSES, path_to_json):
	Generates the files to be sent to CARRA

	xml_files -- locations of the XML files
	NUMBER_OF_PROCESSES -- number of Python threads to use
	path_to_json -- location of JSON files containing city+state and inventor information
```

The functions provided in **src/xml_parser.py** are:
```

```

-	**patent_metadata** collects some basic information about each patent.
	The final **outputs/csv_output/prdn_metadata.csv** file is used later for triangulation.  
	> This depends on the output of **dat_to_xml** and **xml_rewrite**.
