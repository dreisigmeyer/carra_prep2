---- 
You need git-lfs installed to correctly pull large files down.

If you have just pulled this for the first time you will need to run
bzip2 -d create_GBD_metadata/pythonCode/zip3Data/infobox_properties_en.nt.bz2
from this directory
----


* GBD_1976_2001_dat_to_xml/process_pre_2002GBD.py will process any
pre-2002 patents in the dat format.  The resulting XML files will be placed
into python_validation/inData.  This likely won't need to be done 
again.

* create_GBD_metadata/__main__.py can be run to generate XML files
for attaching zip3s, correcting city-state informatuion etc:
        nohup python -m create_GBD_metadata &
Updated USPTO DVD files are placed in 
-> create_GBD_metadata/pythonCode/usptoData
-> assignee/assignee_information_mp
This likely won't need to be done (often).
NOTE: This requires USPTO DVD files, e.g.,:
-INV_COUNTY_00_13.TXT
-INVENTOR_14.TXT

1)
* USPTO bulk download files into python_validation/inData
* Any new DTD files into python_validation/DTDs
* In python_validation/ run: 
nohup ./runit &
* Copy the files in python_validation/outData to
-> CARRA_20YY/inData
-> patent_metadata/inData
-> assignee/assignee_information_mp/inData

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
