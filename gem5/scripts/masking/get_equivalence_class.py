# This file was mainly created to get the relevant equivalence class from the injection list.
# Current inj list contains all the bits of each reg, we don't need all the bits of all regs. The output of this will be used in pruning
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
    

    app_name = sys.argv[1]

    masked_inj_loc = approx_dir + '/workloads/' + isa + '/apps/' + app_name
    outcomes_file = masked_inj_loc + '/' + app_name + '_inj_equivalence_class.txt'                # this needs to be created

    inj_list = masked_inj_loc + '/' + app_name + '_inj_100_list.txt'
    postprocessed = masked_inj_loc + '/' + app_name + '_postprocess.txt'

    pilot_list = {}
    
    write_list = []
   


    with open(inj_list) as injFile:
        for line in injFile:
            inj_tick = line.split(",")[1].strip(" ")
            inj_reg = line.split(",")[2].strip(" ")
            inj_src_dst = line.split(",")[5].strip("\n").strip(" ")
            tup = inj_tick + "," + inj_reg + "," +inj_src_dst
            if tup in pilot_list:
                pilot_list[tup] += 1
            else:
                pilot_list[tup] = 1
            
    
    for each in pilot_list:
        write_list.append(each + "," + str(pilot_list[each]))


            

    with open(outcomes_file, 'w') as f:
        for i in write_list:
            f.write(('%s\n' % i))

    print len(write_list)

