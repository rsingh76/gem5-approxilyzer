# To go through the outcomes of single bit flip experiment and check which ones are "Masked"
# arg 1 : app name
# arg 2 : raw outcome file from - gem5/outputs/x86/<app_name>.outcomes_raw
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
        print('Usage: python gen_simplified_trace.py [app]')
        exit()

    isa = 'x86'
    approx_dir = os.environ.get('APPROXGEM5')
    raw_output_dir = approx_dir + '/gem5/outputs/' + 'x86/'
    outcomes_file = raw_output_dir + '/' + sys.argv[1] + '.outcomes_raw'
    app_name = sys.argv[1]

    masked_inj_loc = approx_dir + '/workloads/' + isa + '/apps/' + app_name
    masked_inj_file = masked_inj_loc + '/' + app_name + '_inj_masked_list.txt'

    sdc_count = 0
    detected_count = 0
    total_bitflips = 0


    masked_errors = {}  
    with open(outcomes_file) as outcomes:
        for line in outcomes:
            total_bitflips = total_bitflips + 1
            if "Masked" in line:
                inj_detail = line.split("::")[0].strip("")
                tick = line.split("::")[0].split(",")[1].strip("")
                masked_errors[inj_detail] = tick
            if "SDC" in line:
                sdc_count = sdc_count + 1
            if "Detected" in line:
                detected_count = detected_count + 1

    # sort acc to ticks:
    sorted_masked_error =  collections.OrderedDict(sorted(masked_errors.items(), key=operator.itemgetter(1)))
    

    # with open(masked_inj_file, 'w') as f:
    #     for key in sorted_masked_error:
    #         f.write(('%s\n' % key))

    print ("Detected errors = ", detected_count)
    print ("SDCs = ", sdc_count)
    print ("Masked = ", len(sorted_masked_error))
    print ("total injections = ", total_bitflips)
