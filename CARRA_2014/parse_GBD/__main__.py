# -*- coding: utf-8 -*-

import glob, os


NUMBER_OF_PROCESSES = 10
base_dir = "parse_GBD"
cw_dir = os.getcwd()
fp_dir = cw_dir + "/" + base_dir
pathToData = 'inData/'
launch_it = "python -u -m {BD}.launch {NP} {FP}".format(BD = base_dir, NP = NUMBER_OF_PROCESSES, FP = fp_dir)
os.system(launch_it)
