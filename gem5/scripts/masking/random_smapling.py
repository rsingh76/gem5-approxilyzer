# Creates a list of relevant PCs that the masked injection list contains and also creates an injection list based on the pc
# arg 1 : app name
# arg 2 : pc = NUm of samples to generate (95% confidence level and 1.2% confidence interval)


import gzip
import io
import os
import sys
import random
import collections
import operator
from clustering_corrupt import get_tick_pc



def random_num_gen(start, end, count):
    if count > end-start:
        return range(start,end)
    return random.sample(range(start, end), count)



if __name__ == '__main__':

    
    if len(sys.argv) != 3:
        print('Usage: python create_selected_inj_list.py [app] [num_of_samples]') 
        exit()


    isa = 'x86'
    approx_dir = os.environ.get('APPROXGEM5')
    app_name = sys.argv[1]
    num_samples = int(sys.argv[2])

    # get the tick from here
    masked_inj_loc = approx_dir + '/workloads/' + isa + '/apps/' + app_name
    masked_inj_file = masked_inj_loc + '/' + app_name + '_inj_masked_list.txt'

    # get the pc from here:
    tick_pc_database = masked_inj_loc + '/' + app_name + '_clean_dump_parsed_merged.txt'

    # get the pc and instruction from here
    disAssembly = masked_inj_loc + '/' + app_name + '.dis'


    selected_inj_list_loc = masked_inj_loc + '/selected_inj_list/'
    pc_list_name = selected_inj_list_loc + 'masked_pc_list.txt'

    output_file_name = selected_inj_list_loc + app_name + '_random_sampling_' + str(num_samples) + '.txt' 

   
    total_masked_count = 0
    masked_inj = []
    with open(masked_inj_file) as masked:
        for fline in masked:
            total_masked_count += 1
            inj = fline.strip("\n")
            masked_inj.append(inj)            


    random_indices = random_num_gen(0, len(masked_inj), num_samples)
    
    final_inj_list = []
    for i in random_indices:
        final_inj_list.append(masked_inj[i])


   
    print "total masked errors = ", total_masked_count
    print len(final_inj_list)





    # for ticks in tick_write.values():
    #     for vals in ticks:
    #         print vals


    # exit(0)  
    with open(output_file_name, 'w') as file2:
        for vals in final_inj_list:
            file2.write(('%s\n' % vals))














