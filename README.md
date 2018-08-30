## Getting the data
1.	If you don't have git-lfs you'll need to download:
    * http://downloads.dbpedia.org/2015-04/core/infobox-properties_en.nt.bz2 
    unzip it and rename it infobox_properties_en.nt (a '-' to an '_'). 
    DBPedia changed the name from earlier releases.
    Put the file into **preprocessing/gbd_metadata/src/zip3Data/**.
    This is the latest version that works with the code.
    DBPedia switched to ttl format after the 2015-04 release.
    * The "All Names" file from the Topical Gazetteers from 
    https://geonames.usgs.gov/domestic/download_data.htm.
    Unzip it and place it in **preprocessing/gbd_metadata/src/zip3Data/usgs_geonames/**.
    * The _INV\_COUNTY\_YY\_YY.TXT_ and _INVENTOR\_YY.TXT_ files from the USPTO's patent data DVD.
    These files are placed in **preprocessing/gbd_metadata/data/uspto_data/**.

2.	If you do have git-lfs and pulled this for the first time from this directory you'll need to 
    run  
    `bzip2 -dk preprocessing/gbd_metadata/data/uspto_data/INV_COUNTY_00_15.TXT.bz2`  
    `bzip2 -dk preprocessing/gbd_metadata/data/uspto_data/INVENTOR_15.TXT.bz2`  
	`bzip2 -dk preprocessing/gbd_metadata/src/zip3Data/infobox_properties_en.nt.bz2`  
	`bzip2 -dk preprocessing/gbd_metadata/src/zip3Data/usgs_geonames/AllNames_20180401.txt.bz2`  
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
* The outputs in **outputs/for_carra/** are post-processed and then sent to CARRA for PIKing.
* The file _metadata.csv_ in **outputs/csv_output/** is used later for triangulation.
* From **outputs/json_output** the files
_zip3\_cities.json_,
_cityMispellings.json_,
_inventors.json_ and
_close_city_spellings.json_
are also used later.
* **outputs/xml_output** contains the XML data where we have **xml_with_inventors/** and
**xml_without_inventors/**.

## Running individual pieces of the code
1.	See the _README.md_ in **dat_to_xml**.  
	> This doesn't depend on any other piece of the code.

2.	See the _README.md_ in **xml_rewrite**.  
	> This doesn't depend on any other piece of the code.

3.	The **preprocessing** module collects together patent metadata and prepares the dat
	XML files for sending to CARRA.
	Many of the intermediate files may be of value as well.
- 	**gbd_metadata** is run to generate JSON files
	for attaching zip3s, and correcting city-state and inventor information.
	The files in **outputs/json_outpt** are  
	_zip3\_cities.json_,  
	_city_mispellings.json_: contains various misspellings of city+state combinations,  
	_inventors.json_ : contains all city+state combinations for inventors base on last, 
	first and middle names and  
	_close_city_spellings.json_
	> This doesn't depend on any other piece of the code.

-	**for_carra** prepares the inventor data to be shipped to CARRA for PIKing.
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

-	**patent_metadata** collects some basic information about each patent.
	In **patent_metadata** run:  
	`nohup ./run_it.sh &`  
	which calls _./create\_patent\_metadata.py 5_ where 5 is the number of processes to run.
	You can change the processor count by editing the _run\_it.sh_ file.
	The final _prdn\_metadata.csv_ file is used later for triangulation.  
	> This depends on the output of **dat_to_xml** and **xml_rewrite**.
