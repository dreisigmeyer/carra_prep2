---- 
You need git-lfs installed to correctly pull large files down.
----
If you don't have git-lfs you'll need to download:
1) http://downloads.dbpedia.org/2015-04/core/infobox-properties_en.nt.bz2
unzip it and rename it infobox_properties_en.nt (a '-' to an '_'). DBPedia
changed the name from earlier releases.  Put the file into
	create_GBD_metadata/pythonCode/zip3Data/
This is the latest version that works with the code.  DBPedia switched to ttl 
format after the 2015-04 release.
2) The "All Names" file from the Topical Gazetteers from 
	https://geonames.usgs.gov/domestic/download_data.htm
Unzip it and place it in
	create_GBD_metadata/pythonCode/zip3Data/usgs_geonames/

If you do have git-lfs and pulled this for the first time:
From this directory you'll need to run
	* bzip2 -d create_GBD_metadata/pythonCode/zip3Data/infobox_properties_en.nt.bz2
	* bzip2 -d create_GBD_metadata/pythonCode/zip3Data/usgs_geonames/AllNames_20180401.txt.bz2
If the bzip files change you'll need to rerun this.


* GBD_1976_2001_dat_to_xml/process_pre_2002GBD.py will process any
pre-2002 patents in the dat format.  The resulting XML files will be placed
into python_validation/inData.  This likely won't need to be done 
again.

* create_GBD_metadata/__main__.py can be run to generate XML files
for attaching zip3s, correcting city-state informatuion etc:
        nohup python -m create_GBD_metadata &
Updated USPTO DVD files are placed in 
- create_GBD_metadata/pythonCode/usptoData
- assignee/assignee_information_mp
This likely won't need to be done (often).
NOTE: This requires USPTO DVD files, e.g.,:
- INV_COUNTY_00_13.TXT
- INVENTOR_14.TXT

1)
* USPTO bulk download files into python_validation/inData
* Any new DTD files into python_validation/DTDs
* In python_validation/ run: 
nohup ./runit &
* Copy the files in python_validation/outData to
- CARRA_20YY/inData
- patent_metadata/inData
- assignee/assignee_information_mp/inData

2)
* In CARRA_20YY do
nohup ./run_it.sh &
* The reulting files in outData go to Wei for processing and then to CARRA.

3)
* In patent_metadata do
nohup ./run_it.sh &
which calls ./create_patent_metadata.py 10 where 10 is the number of processes 
to run.  
* Copy the prdn_metadata.csv file to
-> ../triangulation/triangulation/inData

4)
NOTE: This requires USPTO DVD data, e.g.,:
-ASG_NAMES_UPRD_69_14.TXT
-PN_ASG_UPRD_69_14.TXT
* In assignee/assignee_information_mp do
nohup ./getAssigneeInformation.py 10 &
where 10 is the number of processes to run.
* The results in outData go to Wei for EIN-Firmids and are also copied to
-> ../triangulation/triangulation/inData/assigneeOutData

5)
* In assignee/assignee_information_mp do
nohup ./get_iops.sh &
This gets the prdns-assg_seq of the IOPs.  
* Copy the file iops.csv to
-> ../triangulation/triangulation/inData
