# Plots the distribution of outcomes for every instruction or PC, depending on what user wants
# X axis - instructions/PC
# Y axis - distribution of outcomes

# arg 1 : app name


import gzip
import io
import os
import sys
import random
import collections
import operator

def add_dicts(dict_1, dict_2):
    ret_dict = {}
    for i in dict_1:
        ret_dict[i] = dict_1[i] + dict_2[i]
    return ret_dict


def get_pc_tick_map(tick_pc_database):
    pc_tick_map = {}
    with open(tick_pc_database) as tick_pc:
        for line in tick_pc:
            pc = line.split(" ")[1].strip("x").strip("\n").split("x")[1].strip("")
            tick = line.split(" ")[0].strip("")
            if pc in pc_tick_map:
                pc_tick_map[pc].append(tick)
            else:
                pc_tick_map[pc] = [tick]
    return pc_tick_map

def get_pc_inst(disAssembly):
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
    return pc_inst


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

    # output_file_name = selected_inj_list_loc + app_name + '_inj_list_pc_' + sys.argv[2]


    raw_output_dir = approx_dir + '/gem5/outputs/' + 'x86/'
    outcomes_file = raw_output_dir + '/' + app_name + '.outcomes_raw'
    

# 1. Read the outcomes_raw 
# get ticks, regs and outcomes:
# tick : [[reg, outcomes]....]
# read the database of tick and pc : get pc  : tick map
# get pc: inst map
# go through each pc find the inst, find the tick,, iterate through the list of outcomes

    pc_tick_map = get_pc_tick_map(tick_pc_database)
    pc_inst = get_pc_inst(disAssembly)


    tick_reg_outcome = {}
    for pc in pc_tick_map:
        for tick in pc_tick_map[pc]:
            tick_reg_outcome[tick] = []

    with open(outcomes_file) as raw_out:
        for line in raw_out:
            tick = line.split(",")[1].strip("")
            reg = line.split(",")[2].strip("")
            if "Masked" in line:
                outcome = "Masked"
            elif "SDC" in line:
                outcome = "SDC"
            elif "Detected" in line:
                outcome = "Detected"

            tick_reg_outcome[tick].append([reg, outcome])

    
    pc_outcome_count = {}
    inst_outcome_count = {}
    for pc in pc_tick_map:
        pc_outcome_count[pc] = {"SDC" : 0, "Masked" : 0, "Detected" : 0}
    for pc in pc_tick_map:
        inst_outcome_count[pc_inst[pc]] = {"SDC" : 0, "Masked" : 0, "Detected" : 0}




    for pc in pc_tick_map:
        inst = pc_inst[pc]
        for tick in pc_tick_map[pc]:
            list_outcome_tick = tick_reg_outcome[tick]
            for pair in list_outcome_tick:
                # each pair is [reg, outcome]
                pc_outcome_count[pc][pair[1]] += 1
                inst_outcome_count[inst][pair[1]] += 1

    # for pc in pc_outcome_count:
    #     print (pc, pc_outcome_count[pc]) 

    # for inst in inst_outcome_count:
    #     print(inst, inst_outcome_count[inst])



    possible_instr = ["xor", "add", "mov", "push", "pop", "cmp", "sub", "ucomisd", "callq", "sqrt", "neg", "shl", "lea", "ret", "mul", "cvtsi2sd", "ja", "jle", "jne", "jg", "test", "jmp", "nop", "cvttsd2si" ]

    inst_type_outcome_map = {}
    for inst in possible_instr:
        inst_type_outcome_map[inst] = {"SDC" : 0, "Masked" : 0, "Detected" : 0}
    def_val = {"SDC" : 0, "Masked" : 0, "Detected" : 0}

    for inst in inst_outcome_count:
        found = 0
        for poss_i in possible_instr:
            if poss_i in inst:
                # inst_type_outcome_map[poss_i] = inst_type_outcome_map[poss_i] + inst_outcome_count[inst]
                found  = 1
                inst_type_outcome_map[poss_i] = add_dicts(inst_type_outcome_map[poss_i], inst_outcome_count[inst])
                break    
        if found == 0:
            print ("Add this :", inst)
    
    for inst in inst_type_outcome_map:
        if inst_type_outcome_map[inst] != def_val:
            # for i in inst_type_outcome_map[inst]:
            print inst, inst_type_outcome_map[inst]["SDC"], inst_type_outcome_map[inst]["Masked"], inst_type_outcome_map[inst]["Detected"]
        # else:
        #     print("NOT IN PROGRAM:::::",  inst)








