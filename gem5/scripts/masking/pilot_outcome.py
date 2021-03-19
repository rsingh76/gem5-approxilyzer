# This file was mainly created to get the relevant raw outcomes for LU benchmark.
# It takes a file which is created after postprocessing and gets the pilot from it. then isolates the masked
# errors.
# arg 1: app
# 


import gzip
import io
import os
import sys
import random
import collections
import operator




if __name__ == '__main__':

    if len(sys.argv) != 2:
        print('Usage: python pilot_outcome.py [app]')
        exit()

    isa = 'x86'
    approx_dir = os.environ.get('APPROXGEM5')
    raw_output_dir = approx_dir + '/gem5/outputs/' + 'x86/'
    outcomes_file = raw_output_dir + '/' + sys.argv[1] + '.outcomes_raw'                # this needs to be created

    app_name = sys.argv[1]

    masked_inj_loc = approx_dir + '/workloads/' + isa + '/apps/' + app_name
    masked_inj_file = masked_inj_loc + '/' + app_name + '_inj_masked_list.txt'          # this needs to be created

    inj_list = masked_inj_loc + '/' + app_name + '_inj_100_list.txt'
    postprocessed = masked_inj_loc + '/' + app_name + '_postprocess.txt'

    masked_count = 0
    sdc_count = 0
    detected_count = 0
    total_bitflips = 0

    pilot_list = {}
    pilot_outcome = {}
    write_list = []
    masked_write_list = []

    with open(inj_list) as injFile:
        for line in injFile:
            pilot_list[line.strip("\n")] = 1
    
    with open(postprocessed) as post:
        for line in post:
            inj = line.split("::")[0].split(" ")[1].strip(" ")
            outcome = line.split("::")[1].strip("").strip("\n")
            if inj in pilot_list:
                total_bitflips += 1
                write_list.append(inj + "::" + outcome)
                if "Masked" in line:
                    masked_write_list.append(inj)
                    masked_count += 1
                elif "SDC" in line:
                    sdc_count += 1
                elif "Detected" in line:
                    detected_count += 1
            

    with open(outcomes_file, 'w') as f:
        for i in write_list:
            f.write(('%s\n' % i))

    with open(masked_inj_file, 'w') as f:
        for i in masked_write_list:
            f.write(('%s\n' % i))



    print ("Detected errors = ", detected_count)
    print ("SDCs = ", sdc_count)
    print ("Masked = ", masked_count)
    print ("total injections = ", total_bitflips)

