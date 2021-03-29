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
from clustering_corrupt import get_tick_pc

ten = 10                                         # 70 for sobel   10,16 work gives 10k injections for sobel, (10,10) gives 12K for LU, ()
five = 5                                        # finally - (10,6) for sobel, (7,5) for LU and (6,5) for Swaptions

def random_num_gen(start, end, count):
    if count > end-start:
        return range(start,end)
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


    tick_inj_map = {}                                               # This is a dictionary of dictionary --> tick -> multiple regs -> multiple inj
    total_masked_count = 0
    with open(masked_inj_file) as masked:
        for fline in masked:
            total_masked_count += 1
            tick = fline.split(",")[1].strip("") 
            inj = fline.strip("\n")
            reg = fline.split(",")[2].strip(" ")
            src_dst = fline.split(",")[5].strip(" ").strip("\n")            #0 if src, 1 if dest

            if tick in tick_inj_map:
                # tick_inj_map[tick].append(inj)
                if reg in tick_inj_map[tick]:                   # this means we already have an entry for this reg
                    if src_dst in tick_inj_map[tick][reg]:
                        tick_inj_map[tick][reg][src_dst].append(inj)
                    else:
                        tick_inj_map[tick][reg][src_dst] = [inj]
                else:
                    tick_inj_map[tick][reg] = {}
                    tick_inj_map[tick][reg][src_dst] = [inj]
            else:
                # tick_inj_map[tick] = [inj]
                tick_inj_map[tick] = {}
                tick_inj_map[tick][reg] = {}
                tick_inj_map[tick][reg][src_dst] = [inj]


    limited_pc_tick = {}
    tick_pc = get_tick_pc(tick_pc_database)

    for ticks in tick_inj_map:
        curr_pc = tick_pc[ticks]
        if curr_pc in limited_pc_tick:
            limited_pc_tick[curr_pc].append(ticks)
        else:
            limited_pc_tick[curr_pc] = [ticks]

    
    
    num_inst = 0
    for i in limited_pc_tick:
        num_inst += len(limited_pc_tick[i]) 
    print len(limited_pc_tick), num_inst



    # if a pc has more than 10 dynamic instances then randomly sample 10 dynamic instances
    for pc in limited_pc_tick:
        if len(limited_pc_tick[pc]) > ten:
            tick_list = limited_pc_tick[pc]
            indices = random_num_gen(0, len(limited_pc_tick[pc]), ten)
            indices.sort()
            new_list = []
            limited_pc_tick[pc] = []
            for i in indices:
                limited_pc_tick[pc].append(tick_list[i])



    # count = 0                                   #1457
    # for pc in limited_pc_tick:            
    #     count += len(limited_pc_tick[pc])

    # print count
    # exit(0)





    # print len(pc_tick_map)
    # print len(tick_inj_map)
    # exit(0)

    count_2 = 0
    count_3 = 0
    final_inj_list = []
    for each_pc in limited_pc_tick:
        for each_tick in limited_pc_tick[each_pc]:
            if each_tick in tick_inj_map:
                for regs in tick_inj_map[each_tick]:
                    for src_dst in tick_inj_map[each_tick][regs]:
                        count_2 += 1
                        if len(tick_inj_map[each_tick][regs][src_dst]) > five:
                            count_3 += 1
                            inj_list_tick = tick_inj_map[each_tick][regs][src_dst]
                            indices = random_num_gen(0, len(tick_inj_map[each_tick][regs][src_dst]) , five)
                            tick_inj_map[each_tick][regs][src_dst] = []
                            for i in indices:
                                tick_inj_map[each_tick][regs][src_dst].append(inj_list_tick[i])

                        for i in tick_inj_map[each_tick][regs][src_dst]:
                            final_inj_list.append(i)

   
    # print "total masked errors = ", total_masked_count
    # print len(final_inj_list)

    num_inst = 0
    for i in limited_pc_tick:
        num_inst += len(limited_pc_tick[i]) 
    print len(limited_pc_tick), num_inst



    # for ticks in tick_write.values():
    #     for vals in ticks:
    #         print vals


    # for inj in final_inj_list:
    #     print inj


    # exit(0)  
    with open(output_file_name, 'w') as file2:
        for vals in final_inj_list:
            file2.write(('%s\n' % vals))














