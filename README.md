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
- 	**gbd_metadata** is run to generate JSON files
	for attaching zip3s, and correcting city-state and inventor information.
	The files in **outputs/json_output/** are  
	_zip3\_cities.json_,  
	_city_mispellings.json_: contains various misspellings of city+state combinations,  
	_inventors.json_ : contains all city+state combinations for inventors base on last, 
	first and middle names and  
	_close_city_spellings.json_
	> This doesn't depend on any other piece of the code.  
	The functions provided are:
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
-	**for_carra** prepares the inventor data to be shipped to CARRA for PIKing.
	In particular, this attempts to:
	* correct any misspellings of the city and/or state;
	* assign prior city and states to inventors;
	* attach zip3s to the inventors' cities.  
	The resulting files in **outputs/for_carra/** are post-processed and then sent to CARRA for 
	PIKing.  
	> This depends on the output of **create_GBD_metadata**, **dat_to_xml** and **xml_rewrite**.

-	**patent_metadata** collects some basic information about each patent.
	The final **outputs/csv_output/prdn_metadata.csv** file is used later for triangulation.  
	> This depends on the output of **dat_to_xml** and **xml_rewrite**.
