


import gzip
import io
import os
import sys
import random
import collections
import operator



if __name__ == '__main__':

    if len(sys.argv) != 2:
        print('Usage: python prune_trace.py [app]') 
        exit()

    isa = 'x86'
    approx_dir = os.environ.get('APPROXGEM5')
    app_name = sys.argv[1]

    # get the tick from here
    masked_inj_loc = approx_dir + '/workloads/' + isa + '/apps/' + app_name
    masked_inj_file = masked_inj_loc + '/' + app_name + '_inj_masked_list.txt'
    total_inj = masked_inj_loc + '/' + app_name + '_inj_100_list.txt'

    # get the pc from here:
    tick_pc_database = masked_inj_loc + '/' + app_name + '_clean_dump_parsed_merged.txt'
    inst_parsed = masked_inj_loc + '/' + app_name + '_parsed.txt'

    # get the pc and instruction from here
    disAssembly = masked_inj_loc + '/' + app_name + '.dis'


    selected_inj_list_loc = masked_inj_loc + '/selected_inj_list/'
    pc_list_name = selected_inj_list_loc + 'masked_pc_list.txt'

    # output_file_name = selected_inj_list_loc + app_name + '_inj_list_pc_' + sys.argv[2]


    raw_output_dir = approx_dir + '/gem5/outputs/' + 'x86/raw_out/'
    raw_outcomes = raw_output_dir + app_name + '.outcomes_raw'
    outcomes_file = app_name + '_dynamic_masked_outcomes.txt'


    masked_inj_set = set()
    total_masked = 0
    with open(masked_inj_file) as masked:
        for line in masked:
            total_masked += 1
            masked_inj_set.add(line.strip("\n"))


    injection_outcome_map = {}
    with open(raw_outcomes) as raw:
        for line in raw:
            injection = line.split("::")[0].strip(" ")
            outcome = line.split("::")[1].strip("\n").strip(" ")
            injection_outcome_map[injection] = outcome


    estimated_masked = 0
    correctly_estimated_masked = 0
    wrongly_estimated_cnt = 0
    correctly_estimated = []
    wrongly_estimated = {}
    with open(outcomes_file) as file1:
        for line in file1:
            estimated_masked += 1
            msk = line.strip("\n")
            if msk in masked_inj_set:
                correctly_estimated_masked += 1
                correctly_estimated.append(msk)
            else:
                actual_outcome = injection_outcome_map[msk]
                wrongly_estimated[msk] = actual_outcome
                wrongly_estimated_cnt += 1


    print ("Total masked errors:     ", total_masked)
    print ("Estimated masked errors: ", estimated_masked ,"\t", str((float(estimated_masked)/float(total_masked))* 100) + "% of total masked")
    print ("Correct Estimations:     ", correctly_estimated_masked,"\t", str((float(correctly_estimated_masked)/float(total_masked))* 100) + "% of total masked")
    print ("False Positives:         ", wrongly_estimated_cnt, "\t", str((float(estimated_masked - correctly_estimated_masked)/float(estimated_masked)) * 100) + "% of total estimates")

    for i in wrongly_estimated:
        print (i, "::", wrongly_estimated[i])

