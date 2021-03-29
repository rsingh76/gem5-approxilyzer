import gzip
import io
import os
import sys
import random
import collections
import operator
from comp_exec_trace import *
from plot_instr_distr import *


def get_tick_pc(tick_pc_database):
    tick_pc = {}
    with open(tick_pc_database) as file1:
        for line in file1:
            tick = line.split(" ")[0].strip(" ") 
            pc = line.split(" ")[1].strip(" ").split("x")[1]
            tick_pc[tick] = pc
    
    return tick_pc


def tick_inst_opcode(tick, pc_opcode, tick_pc):
    return pc_opcode[tick_pc[tick].strip("\n")]



if __name__ == '__main__':

    if len(sys.argv) != 2:
        print('Usage: python clustering_corrupt.py [app]') 
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

    masked_outcomes = raw_output_dir  + app_name +  "_masking_results"                  # TODO: Change this 
    interesting_masked_outcomes = raw_output_dir  + "interesting_fi/"  + app_name +  "_masking_results_interesting_large"
    to_check = "interesting_fi/to_check_" + app_name + "_large"
    # if app_name == "sobel":
    #     to_check = to_check + "_2"


    interesting_fi = []
    with open(to_check) as intr_fi:
        for line in intr_fi:
            if "x86" in line:
                interesting_fi.append(line.strip("\n"))


    cluster_affected_regs = {}
    cluster_affected_mems = {}
    cluster_affected_all = {}
    
    for i in range(100):
        cluster_affected_regs[i] = []
        cluster_affected_mems[i] = []
        cluster_affected_all[i] = []




    affected_regs = []
    affected_mem = []
    total_affected = []
    fi_arg = "x"
    inj_reg = "x"
    inj_tick = "x"
    inj_reg_num = "x"
    
    with open(interesting_masked_outcomes) as masked:
        while True and masked != None:
            
            line = masked.readline()
            if line == "":
                break
            if line == "\n":
                continue
            if "#New_FI" in line:
                new_error_injection = 1
                # actual_count += 1
                continue
            elif "################################################################################" in line:
                # this means we are done with this fi_arg: so do the book keeping
                if fi_arg in interesting_fi:
                    cluster_affected_regs[len(affected_regs)].append([inj_tick, inj_reg])
                    cluster_affected_mems[len(affected_mem)].append([inj_tick, inj_reg])
                    cluster_affected_all[len(total_affected)].append([inj_tick, inj_reg])
                affected_regs = []
                affected_mem = []
                total_affected = []
                new_error_injection = 0
                continue

            if new_error_injection == 1 and "x86," in line:
                fi_arg = line.strip("\n").strip("")
                inj_reg = fi_arg.split(",")[2].strip("")
                inj_reg_num = Reg_map[inj_reg]
                inj_tick = fi_arg.split(",")[1].strip("")
                new_error_injection = 0
            
            if fi_arg not in interesting_fi:
                new_error_injection = 1
                continue
            else:
                new_error_injection = 0

            if new_error_injection == 0:

                if ":: reg" in line or ":: float reg" in line:
                    if inj_reg_num not in line and "reg 16" not in line:
                        aff_reg = line.split("::")[1].strip("\n").strip(" ")
                        affected_regs.append(aff_reg)
                        total_affected.append(aff_reg)
                elif ":: MEM" in line:
                    aff_mem = line.split("=")[1].strip("\n").strip("")
                    affected_mem.append(aff_mem)
                    total_affected.append(aff_mem)


    for i in range(100):
        if(cluster_affected_regs[i] == []):
            del cluster_affected_regs[i]
        if(cluster_affected_mems[i] == []):
            del cluster_affected_mems[i]
        if(cluster_affected_all[i] == []):
            del cluster_affected_all[i]

    # print len(cluster_affected_all)
    # print len(cluster_affected_mems)
    # print len(cluster_affected_regs)       
   
    # for i in cluster_affected_all:
    #     print i, len(cluster_affected_all[i])

    print "Affected Regs"
    for i in cluster_affected_regs:
        print i, len(cluster_affected_regs[i])


    print "\nAffected Mem"
    for i in cluster_affected_mems:
        print i, len(cluster_affected_mems[i])

    print ""

    pc_tick_map             = get_pc_tick_map(tick_pc_database)
    pc_inst, pc_opcode      = get_pc_inst(disAssembly)
    tick_pc                 = get_tick_pc(tick_pc_database)

    cluster_opcodes_reg  = {}
    cluster_affected_regs_opcodes = {}
    for i in cluster_affected_regs:
        cluster_affected_regs_opcodes[i] = {}

        temp_list_list = cluster_affected_regs[i]           # list of list [[inj_tick, inj_reg] ........ ]
        for single_inj in temp_list_list:        # list [inj_tick, inj_reg]
            opcode = tick_inst_opcode(single_inj[0], pc_opcode, tick_pc)
            # print opcode
            cluster_opcodes_reg[opcode] = {}
            if opcode in cluster_affected_regs_opcodes[i]:
                cluster_affected_regs_opcodes[i][opcode] += 1 
            else:
                cluster_affected_regs_opcodes[i][opcode] = 1


    

    for i in cluster_affected_regs_opcodes:
        for opcodes in cluster_affected_regs_opcodes[i]:
            cluster_opcodes_reg[opcodes][i] = cluster_affected_regs_opcodes[i][opcodes] 


    # for i in cluster_affected_regs_opcodes:
    #     for opcodes in cluster_affected_regs_opcodes[i]:
    #         print i , opcodes, cluster_affected_regs_opcodes[i][opcodes]

    for opcodes in cluster_opcodes_reg:
        for i in cluster_opcodes_reg[opcodes]:
            print opcodes , i, cluster_opcodes_reg[opcodes][i]
