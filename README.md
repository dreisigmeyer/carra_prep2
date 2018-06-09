## Getting the data
1.	If you don't have git-lfs you'll need to download:
	* http://downloads.dbpedia.org/2015-04/core/infobox-properties_en.nt.bz2 
	unzip it and rename it infobox_properties_en.nt (a '-' to an '_'). 
	DBPedia changed the name from earlier releases.
	Put the file into _create_GBD_metadata/pythonCode/zip3Data/_.
	This is the latest version that works with the code.
	DBPedia switched to ttl format after the 2015-04 release.
	* The "All Names" file from the Topical Gazetteers from 
	https://geonames.usgs.gov/domestic/download_data.htm.
	Unzip it and place it in _create_GBD_metadata/pythonCode/zip3Data/usgs_geonames/_.
	* The _INV\_COUNTY\_YY\_YY.TXT_ and _INVENTOR\_YY.TXT_ files from the USPTO's patent data DVD.
	These files are placed in _create_GBD_metadata/pythonCode/usptoData/_.

2.	If you do have git-lfs and pulled this for the first time from this directory you'll need to run  
    `bzip2 -d create_GBD_metadata/pythonCode/usptoData/INV_COUNTY_00_15.TXT.bz2`  
    `bzip2 -d create_GBD_metadata/pythonCode/usptoData/INVENTOR_15.TXT.bz2`  
	`bzip2 -d create_GBD_metadata/pythonCode/zip3Data/infobox_properties_en.nt.bz2`  
	`bzip2 -d create_GBD_metadata/pythonCode/zip3Data/usgs_geonames/AllNames_20180401.txt.bz2`  
	If the bzip files change you'll need to rerun this.

## Setting up the Python environment
Included is an _environment.yml_ file that you can use with Anaconda to set up a Python virtual environment using  
`conda env create -f environment.yml`  
More information is available at https://conda.io/docs/user-guide/tasks/manage-environments.html.

## Running the code
1.	_GBD\_1976\_2001\_dat\_to\_xml_ will process any pre-2002 patents in the dat format.
	The original dat files (1976-2001 as YYYY.zip) are available at 
	https://bulkdata.uspto.gov/
	under the **Patent Grant Bibliographic (Front Page) Text Data (JAN 1976 - PRESENT)** section.
	Place the downloaded files into _GBD\_1976\_2001\_dat\_to\_xml/inData/_
	In _GBD\_1976\_2001\_dat\_to\_xml/_ run:  
	`nohup ./runit.sh &`  
	In the directory _GBD\_1976\_2001\_dat\_to\_xml/outData/_ issue the command  
	`ls *.xml | xargs -n1 -i zip {}.zip {}`  
	and place the resulting zip files into _python\_validation/inData/_.

2.	_create\_GBD\_metadata_ is run to generate XML files
	for attaching zip3s, correcting city-state information, etc.
	From this directory issue  
	`nohup python -m create_GBD_metadata &`  
	The files 
	_ASCII\_zip3\_cities.xml_, 
	_cityMispellings.xml_ and 
	_inventors.xml_
	are copied into _CARRA\_2014/parse\_GBD/_.

3.	_python\_validation_ creates valid XML documents from the original XML files (2002-present) available at 
	https://bulkdata.uspto.gov/
	under the **Patent Grant Bibliographic (Front Page) Text Data (JAN 1976 - PRESENT)** section.
	The file names are of the form _pgbYYYYMMDD_wkXX.zip_ or _ipgbYYYYMMDD_wkXX.zip_.
	The included script _get\_uspto\_data.sh_ will download all the required zip files from the USPTO website.
	Place the downloaded files into _python\_validation/inData/_ alongside the XML files from the _GBD\_1976\_2001\_dat\_to\_xml_ step above.
	DTD files are also in the USPTO download sites.
	All necessary DTD, ent, etc files are included as of 7 Jun 18.
	Place any new DTD files into _python\_validation/DTDs_ as well as _CARRA\_2014/parse_GBD/_.
	The created XML files were also validated but this was turned off because there were too many issues with the USPTO XML files.  
	In _python\_validation/_ run:  
	`nohup ./runit &`  
	Copy the files in _python\_validation/outData/_ to _CARRA\_2014/inData/_ and _patent\_metadata/inData/_.

4.	_CARRA\_2014_ prepares the inventor data to be shipped to CARRA for PIKing.
	In particular, this attempts to:
	* correct any misspellings of the city and/or state;
	* assign prior city and states to inventors;
	* attach zip3s to the inventors' cities.

	In _CARRA\_2014_ run:  
	`nohup ./run_it.sh &`  
	The reulting files in _CARRA\_2014/outData/_ are post-processed and then sent to CARRA for PIKing.

5.	_patent\_metadata_ collects some basic information about each patent.
	In _patent\_metadata_ run:  
	`nohup ./run_it.sh &`  
	which calls _./create\_patent\_metadata.py 10_ where 10 is the number of processes to run.
	You can change the processor count by editing the _run\_it.sh_ file.
	The final _prdn\_metadata.csv_ file is used later for triangulation.

