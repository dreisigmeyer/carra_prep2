## Getting the data
1.	If you don't have git-lfs you'll need to download:
    * http://downloads.dbpedia.org/2015-04/core/infobox-properties_en.nt.bz2 
    unzip it and rename it infobox_properties_en.nt (a '-' to an '_'). 
    DBPedia changed the name from earlier releases.
    Put the file into **create_GBD_metadata/pythonCode/zip3Data/**.
    This is the latest version that works with the code.
    DBPedia switched to ttl format after the 2015-04 release.
    * The "All Names" file from the Topical Gazetteers from 
    https://geonames.usgs.gov/domestic/download_data.htm.
    Unzip it and place it in **create_GBD_metadata/pythonCode/zip3Data/usgs_geonames/**.
    * The _INV\_COUNTY\_YY\_YY.TXT_ and _INVENTOR\_YY.TXT_ files from the USPTO's patent data DVD.
    These files are placed in **create_GBD_metadata/pythonCode/usptoData/**.

2.	If you do have git-lfs and pulled this for the first time from this directory you'll need to 
    run  
    `bzip2 -dk create_GBD_metadata/pythonCode/usptoData/INV_COUNTY_00_15.TXT.bz2`  
    `bzip2 -dk create_GBD_metadata/pythonCode/usptoData/INVENTOR_15.TXT.bz2`  
	`bzip2 -dk create_GBD_metadata/pythonCode/zip3Data/infobox_properties_en.nt.bz2`  
	`bzip2 -dk create_GBD_metadata/pythonCode/zip3Data/usgs_geonames/AllNames_20180401.txt.bz2`  
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
`nohup ./doitall.sh &`  
* The outputs in **for_carra/outData/** are post-processed and then sent to CARRA for PIKing.
* The file _metadata.csv_ is used later for triangulation.
* From **create_GBD_metadata/** the files
_zip3\_cities.json_,
_cityMispellings.json_,
_inventors.json_ and
_close_city_spellings.json_
are also used later.

## Running individual pieces of the code
1.	See the _README.md_ in **dat_to_xml**.  
	> This doesn't depend on any other piece of the code.

2.	See the _README.md_ in **xml_rewrite**.  
	> This doesn't depend on any other piece of the code.

3.	**create_GBD_metadata** is run to generate JSON files
	for attaching zip3s, correcting city-state information, etc.
	From this directory (i.e., where this README file is located at) issue the command  
	`nohup python -m create_GBD_metadata &`  
	The files 
	_zip3\_cities.json_, 
	_cityMispellings.json_, 
	_inventors.json_ and
	_close_city_spellings.json_
	are copied into **for_carra/parse_GBD/**.
	These are also used later for triangulation.  
	> This doesn't depend on any other piece of the code.

4.	**for_carra** prepares the inventor data to be shipped to CARRA for PIKing.
	In particular, this attempts to:
	* correct any misspellings of the city and/or state;
	* assign prior city and states to inventors;
	* attach zip3s to the inventors' cities.  
	
	This lauches the number of threads specified in _\_\_main.py\_\__  
	`NUMBER_OF_PROCESSES = 5`  
	which you can change by editing that file.
	In **for_carra** run:  
	`nohup ./run_it.sh &`  
	The resulting files in _CARRA\_2014/outData/_ are post-processed and then sent to CARRA for 
	PIKing.  
	> This depends on the output of **create_GBD_metadata**, **dat_to_xml** and **xml_rewrite**.

5.	**patent_metadata** collects some basic information about each patent.
	In **patent_metadata** run:  
	`nohup ./run_it.sh &`  
	which calls _./create\_patent\_metadata.py 5_ where 5 is the number of processes to run.
	You can change the processor count by editing the _run\_it.sh_ file.
	The final _prdn\_metadata.csv_ file is used later for triangulation.  
	> This depends on the output of **dat_to_xml** and **xml_rewrite**.
