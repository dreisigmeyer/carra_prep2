# -*- coding: utf-8 -*-

import glob, os
# import csv

NUMBER_OF_PROCESSES = 10
base_dir = "parse_GBD"
cw_dir = os.getcwd()
fp_dir = cw_dir + "/" + base_dir
pathToData = 'inData/'

launch_it = "python -u -m {BD}.launch {NP} {FP}".format(BD = base_dir, NP = NUMBER_OF_PROCESSES, FP = fp_dir)
os.system(launch_it)

file_names = glob.glob('outData/*.csv')
for file_name in file_names:
    app_year = file_name.split('_')[0]
    zip3_file = "outData/zip3s_" + app_year + ".csv"
    cat_cmd = "echo " + file_name + " >> " + zip3_file
    os.system(cat_cmd)
    # in_file = open(file_name, 'r')
    # csv_reader = csv.reader(in_file)
    # for row in csv_reader:
    #     app_year = row[2]
    #     zip3_file = "outData/zip3s_" + app_year + ".csv"
    #     out_line = ",".join(row)
    #     echo_cmd = "echo " + out_line + " >> " + zip3_file
    #     os.system(echo_cmd)
    # in_file.close()
    os.remove(file_name)
