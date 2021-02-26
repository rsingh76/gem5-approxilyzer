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




if __name__ == '__main__':

    
    if len(sys.argv) != 3:
        print('Usage: python create_selected_inj_list.py [app] [pc ("create" or an actual PC)] ') 
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

    output_file_name = selected_inj_list_loc + app_name + '_inj_list_pc_' + sys.argv[2]

    
    if sys.argv[2] == "create":
        
        # We have to create a list of PCs
        # 1. go through each injection in masked_inj_list
        # 2. get the list of ticks and regs (if multiple regs - create two entries)
        # 3. match the tick from tick_pc_database and get the PC
        # 4. get the instruction from disAssembly
        # format of the line -  |     PC       |        Dynamic Instances      |       bitflipped REGS        |     INST
        
        # Step 1
        tick_reg_map = {}
        tick_set = set()
        with open(masked_inj_file) as masked:
            for line in masked:
                tick = line.split(",")[1].strip("")
                if tick not in tick_set:
                    tick_set.add(tick)
                    tick_reg_map[tick] = set()
                reg = (line.split(",")[2].strip(""))
                tick_reg_map[tick].add(reg)
        
        # Step 2
        tick_pc_map = {}
        with open (tick_pc_database) as tick_pc:
            for line in tick_pc:
                tick = line.split(" ")[0].strip("")
                pc = line.split(" ")[1].strip("x").strip("\n").split("x")[1].strip("")
                tick_pc_map[tick] = pc
        
        # Step 3
        relevant_pc = {}
        pc_regs = {}
        for ticks in tick_reg_map:
            if ticks in tick_pc_map:
                rel_pc = tick_pc_map[ticks]
                if rel_pc not in relevant_pc:
                    relevant_pc[rel_pc] = 1
                else:
                    relevant_pc[rel_pc]  = relevant_pc[rel_pc] + 1
                pc_regs[rel_pc] = tick_reg_map[ticks]

        # print (len(relevant_pc))
        # print (len(pc_regs))
        pc_inst = {}
        with open (disAssembly) as dis:
            for line in dis:
                split_line = line.split(":")
                if len(split_line) > 1:
                    if len (split_line[1]) > 2:
                        pc = line.split(":")[0].strip(" ")
                        inst = line.strip("\t").strip("\n")
                        pc_inst[pc] = inst
                    else:
                        continue
                else:
                    continue


        pc_write = {}
        for pc in relevant_pc:
            to_write = []
            to_write.append(pc)
            to_write.append(relevant_pc[pc])
            regs = "( "
            for i in pc_regs[pc]:
                regs = regs + i + " "
            regs = regs + ")"
            # to_write.append(pc_regs[pc])
            to_write.append(regs)            
            to_write.append(pc_inst[pc].split("\t")[2].strip(""))
            pc_write[pc] = to_write
        

        sorted_relevant_pc =  collections.OrderedDict(sorted(pc_write.items(), key=operator.itemgetter(0)))
        
        # for pc in sorted_relevant_pc:
        #     print (sorted_relevant_pc[pc])
        

        with open(pc_list_name, 'w') as file:
            file.write("PC, Dynamic Instances, bitflipped REGS, INST\n")
            for nested_list in sorted_relevant_pc.values():
                for word in nested_list:
                    file.write(str(word) + ' , ')
                file.write('\n')


    else:
        pc_tick_map = {}
        ticks = set()
        with open (tick_pc_database) as tick_pc:
            for line in tick_pc:
                if sys.argv[2] in line:
                    tick = line.split(" ")[0].strip("")
                    ticks.add(tick)
                    pc = line.split(" ")[1].strip("x").strip("\n").split("x")[1].strip("")
                    if pc in pc_tick_map:
                        pc_tick_map[pc].append(tick)
                    else:
                        pc_tick_map[pc] = [tick]


        tick_write = {}
        with open (masked_inj_file) as masked:
            for fline in masked:
                for tick in ticks:
                    if tick in fline:
                        if tick in tick_write:
                            tick_write[tick].append(fline.strip("\n"))
                        else:
                            tick_write[tick] = [fline.strip("\n")]
                        break
            

        
        # for ticks in tick_write.values():
        #     for vals in ticks:
        #         print vals
                
        with open(output_file_name, 'w') as file2:
            for nested_list in tick_write.values():
                for vals in nested_list:
                    file2.write(('%s\n' % vals))














