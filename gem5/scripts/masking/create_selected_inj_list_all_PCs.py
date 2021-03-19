# Creates a list of relevant PCs that the masked injection list contains and also creates an injection list based on the pc
# arg 1 : app name
# arg 2 : pc = "create" if we don't have a list of relevant PCs ; else enter the PC number


import gzip
import io
import os
import sys
import random
import collections
import operator

ten = 70
five = 20

def random_num_gen(start, end, count):
    return random.sample(range(start, end), count)



if __name__ == '__main__':

    
    if len(sys.argv) != 2:
        print('Usage: python create_selected_inj_list.py [app]') 
        exit()


    isa = 'x86'
    approx_dir = os.environ.get('APPROXGEM5')
    app_name = sys.argv[1]

    # get the tick from here
    masked_inj_loc = approx_dir + '/workloads/' + isa + '/apps/' + app_name
    masked_inj_file = masked_inj_loc + '/' + app_name + '_inj_masked_list.txt'

    # get the pc from here:
    tick_pc_database = masked_inj_loc + '/' + app_name + '_clean_dump_parsed_merged.txt'

    # get the pc and instruction from here
    disAssembly = masked_inj_loc + '/' + app_name + '.dis'


    selected_inj_list_loc = masked_inj_loc + '/selected_inj_list/'
    pc_list_name = selected_inj_list_loc + 'masked_pc_list.txt'

    output_file_name = selected_inj_list_loc + app_name + '_selected_inj_list.txt' 

   
    #  generate a PC - Tick Map
    pc_tick_map = {}
    ticks = set()
    with open (tick_pc_database) as tick_pc:
        for line in tick_pc:
            
            tick = line.split(" ")[0].strip("")
            ticks.add(tick)
            pc = line.split(" ")[1].strip("x").strip("\n").split("x")[1].strip("")
            if pc in pc_tick_map:
                pc_tick_map[pc].append(tick)
            else:
                pc_tick_map[pc] = [tick]


    # if a pc has more than 10 ticks then randomly sample 10 ticks
    for pc in pc_tick_map:
        if len(pc_tick_map[pc]) > ten:
            tick_list = pc_tick_map[pc]
            indices = random_num_gen(0, len(pc_tick_map[pc]), ten)
            indices.sort()
            new_list = []
            pc_tick_map[pc] = []
            for i in indices:
                pc_tick_map[pc].append(tick_list[i])



    # count = 0                                   #1457
    # for pc in pc_tick_map:            
    #     count += len(pc_tick_map[pc])

    # print count
    # # exit(0)



    tick_inj_map = {}
    with open(masked_inj_file) as masked:
        for fline in masked:
            tick = fline.split(",")[1].strip("") 
            inj = fline.strip("\n")
            if tick in tick_inj_map:
                tick_inj_map[tick].append(inj)
            else:
                tick_inj_map[tick] = [inj]

    # print len(pc_tick_map)
    # print len(tick_inj_map)
    # exit(0)

    count = 0
    final_inj_list = []
    for each_pc in pc_tick_map:
        for each_tick in pc_tick_map[each_pc]:
            if each_tick in tick_inj_map:
                count += 1
                if len(tick_inj_map[each_tick]) > five:
                    inj_list_tick = tick_inj_map[each_tick]
                    indices = random_num_gen(0, len(tick_inj_map[each_tick]) , five)
                    tick_inj_map[each_tick] = []
                    for i in indices:
                        tick_inj_map[each_tick].append(inj_list_tick[i])
                
                for i in tick_inj_map[each_tick]:
                    final_inj_list.append(i)

        
    # print count
    # print len(final_inj_list)

    # for ticks in tick_write.values():
    #     for vals in ticks:
    #         print vals


    # exit(0)  
    with open(output_file_name, 'w') as file2:
        for vals in final_inj_list:
            file2.write(('%s\n' % vals))














