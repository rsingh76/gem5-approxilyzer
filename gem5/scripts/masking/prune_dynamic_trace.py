

import gzip
import io
import os
import sys
import random
import collections
import operator
import tqdm
import concurrent.futures

from clustering_corrupt import *
from registers import *


def update_flags(op, clean_or_not):
    # check the type of instruction
    # check what flag it will touch
    # check if the instruction has a corrupted register/mem as source if yes, then wirte not_clean to those maps - it already recieves thie as parameter

    for flags in instr_flag_affect_map:
        for inst in instr_flag_affect_map[flags]:
            if inst in op or inst == 'all':
                all_flag_track_map[flags] = clean_or_not
                break

def intersection(lst1, lst2): 
    return list(set(lst1) & set(lst2)) 

def get_corrup_list(corr_map):
    ret_list = []
    for regs in corr_map:
        # temp = reg_alias_map[regs]
        for i in corr_map[regs]:
            ret_list.append(i)
        for key in reg_alias_map:
            if regs in reg_alias_map[key]:
                ret_list.append(key)
    return ret_list

def check_reg_in_corr_map(reg, corr_map):
    if reg == "None":
        return None
    for i in corr_map:
        if reg in corr_map[i] or reg == i:
            return i
    
    return None


def get_inj_details(fi_arg):
    tick = fi_arg.split(",")[0]
    inj_reg = fi_arg.split(",")[1]
    src_dest = fi_arg.split(",")[2]        # src if 0, dst if 1
    inj_pc = tick_pc[tick]
    return tick, inj_reg, src_dest, inj_pc


def get_pc_details(inst_parsed):
    with open(inst_parsed) as file2:
        details = {}
        for line in file2:
            pc = line.split(" ")[0]
            op = line.split(" ")[1]
            is_ctrl = line.split(" ")[2]

            src_regs = line.split(" ")[3]
            if "," in src_regs: 
                num_src = len(src_regs.split(","))
                all_src = []
                for i in range(num_src):
                    all_src.append(src_regs.split(",")[i])
            else:
                all_src = [src_regs]


            src_mem_reg = line.split(" ")[4]
            if "," in src_mem_reg: 
                num_src = len(src_mem_reg.split(","))
                all_src_mem = []
                for i in range(num_src):
                    all_src_mem.append(src_mem_reg.split(",")[i])
            else:
                all_src_mem = [src_mem_reg]


            is_mem = line.split(" ")[5]

            dst_reg = line.split(" ")[6]

            details[pc] = [op, is_ctrl, all_src, all_src_mem, is_mem, dst_reg]
                
        return details

def get_src_mem_reg(line):
    src_mem_reg = ["None"]
    if "+" in line.split(":[")[1].split("]")[0]:
        src_mem_reg = []
        fir = line.split(":[")[1].split("]")[0].split(" ")[0].strip(" ").strip("%")
        sec = line.split(":[")[1].split("]")[0].split(" ")[2].strip(" ").strip("%")
        

        if "*" in fir:
            if fir.split("*")[0] in all_regs:
                src_mem_reg.append(fir.split("*")[0])
            if fir.split("*")[1] in all_regs:
                src_mem_reg.append(fir.split("*")[1])

        if "*" in sec:
            if sec.split("*")[0] in all_regs:
                src_mem_reg.append(sec.split("*")[0])
            if sec.split("*")[1] in all_regs:
                src_mem_reg.append(sec.split("*")[1])
    elif "*" in line.split(":[")[1].split("]")[0]:
        fir = line.split(":[")[1].split("]")[0].split("*")[0]
        sec = line.split(":[")[1].split("]")[0].split("*")[1]
        if fir in all_regs:
            src_mem_reg.append(fir)
        if sec in all_regs:
            src_mem_reg.append(sec)
    else:
        reg = line.split(":[")[1].split("]")[0].strip("\n").strip("%")
        if reg in all_regs:
            src_mem_reg = [reg]


    return src_mem_reg




# def check_masking(fi_arg, inst_parsed, tick_pc_database, tick_pc):
def check_masking(tup):
    
    fi_arg = tup[0] 
    pc_details = tup[1]
    tick_pc_database = tup[2]
    tick_pc = tup[3]
    dyn_trace = tup[4]
    prev_line = "x"
    # return 1 if the error is going to be masked 
    corrupted_count = 1
    instr_exectued = 0
    corrupted_map = {}
    inj_tick, inj_reg, src_dst, inj_pc = get_inj_details(fi_arg)
    inj_alias_reg = reg_alias_map[inj_reg]
    corrupted_map[inj_reg] = inj_alias_reg
    with open(dyn_trace) as tp_d:
        
        found = 0
        for line in tp_d:
            # if found ==1:
            #     print (line, corrupted_count, corrupted_map)
            if not corrupted_map:
                return [1 , fi_arg]
            elif instr_exectued > 10000:
                return [0 , fi_arg]

            is_load = 0
            is_store = 0
            store_loc = "x"
            load_loc = "x"

            if "fault"  in line:
                continue
            # find the inj_tick first
            if inj_tick not in line and found == 0: 
                prev_line = line
                continue
            elif inj_tick in line:
                found = 1
                # TODO: make sure to consider the consequences of this error in this instruction
                # flags, destination regs

                # prev_line = line
                # continue
            # now we are in the insttruction right after injection
            
            tick    = line.split(" ")[0].strip(":")
            pc      = line.split(" ")[2].split(".")[0].split("x")[1].strip(" ")
            op      = "x"
            is_ctrl = "False"
            src_regs = ["None"]
            src_mem_reg = ["None"]
            is_mem = "False"
            dst_reg = "None"
            mem_loc = "x"

            # for i in pc_details:
            #     print (i, pc_details[i])
            
            if pc in pc_details:
                prev_pc = prev_line.split(" ")[2].split(".")[0].split("x")[1].strip(" ")
                if prev_pc == pc:
                    continue
                # print (tick, pc, pc_details[pc])
                op = pc_details[pc][0]
                is_ctrl = pc_details[pc][1]
                src_regs = pc_details[pc][2]
                src_mem_reg = pc_details[pc][3]
                is_mem = pc_details[pc][4]
                dst_reg = pc_details[pc][5]
                
            else:
                # this means that the pc is from a library call and is not in the disassembly, need to get details from the dyn_trace
                op = line.split(":")[3].split("   ")[0]
                if "st" in op and "ldst" not in op and "A=" in line:
                    # it is a store instr
                    is_ctrl = "False"
                    is_mem = "True"
                    src_regs = [line.split(":")[3].split("   ")[1].split(",")[0].strip(" ").strip("%")]
                    mem_loc = line.split("A=")[1].strip("\n").strip(" ")
                    src_mem_reg = get_src_mem_reg(line)

                elif ("ld" in op and "A=" in line):
                    # this is a load
                    is_ctrl = "False"
                    is_mem = "True"
                    dst_reg = line.split(":")[3].split("   ")[1].split(",")[0].strip(" ").strip("%")
                    
                    mem_loc = line.split("A=")[1].strip("\n").strip(" ")

                    src_mem_reg = get_src_mem_reg(line)

                    src_regs = ["None"]

                elif "lea" in line:
                    is_mem = "True"
                    src_mem_reg =  get_src_mem_reg(line)
                    dst_reg = line.split(":")[3].split("   ")[1].split(",")[0].strip(" ").strip("%")
                
                else:
                    is_mem = "False"
                    src_mem_reg = ["None"]
                    dst_reg = line.split(":")[3].split("   ")[1].split(",")[0].strip(" ").strip("%")
                    srcs = []
                    if len(line.split(":")[3].split("   ")[1].split(",")) == 3:          # in total 3 arguements
                        src0 = line.split(":")[3].split("   ")[1].split(",")[1].strip(" ").strip("%")
                        src1 = line.split(":")[3].split("   ")[1].split(",")[2].strip(" ").strip("%")
                        if "0x" not in src0 and src0 != "0" and "ctrl" not in src0 and src0 != " " and src0 != "":
                            srcs.append(src0)
                        if "0x" not in src1 and src1 != "0" and "ctrl" not in src1 and src1 != " " and src1 != "":
                            srcs.append(src1)
                        if srcs == []:
                            srcs.append("None")

                        if srcs[0] == dst_reg and "mov" in line and len(srcs) == 2:
                            src_regs = [srcs[1]]
                            # if "0x" in srcs[1] or srcs[1] == "0" or "ctrl" in srcs[1] or srcs[1] == " ":
                            #     src_regs = ["None"]
                        else:
                            # if ("0x" in srcs[0] or srcs[0] == "0" or "ctrl" in srcs[0] or srcs[0] == " ") and ("0x" not in srcs[1] and srcs[1] != "0" and "ctrl" not in srcs[1] and srcs[1] != " "):
                            #     src_regs = [srcs[1]]
                            # elif ("0x" in srcs[1] or srcs[1] == "0" or "ctrl" in srcs[1] or srcs[1] == " ") and ("0x" not in srcs[0] and srcs[0] != "0" and "ctrl" not in srcs[0] and srcs[0] != " "):
                            #     src_regs = [srcs[0]]
                            # elif ("0x" in srcs[0] or srcs[1] == "0" or "ctrl" in srcs[0] or srcs[0] == " ") and ("0x" in srcs[1] or srcs[1] == "0" or "ctrl" in srcs[1] or srcs[1] == " "):
                            #     src_regs = ["None"]
                            # else:
                                # src_regs = srcs
                            src_regs = srcs

                    elif len(line.split(":")[3].split("   ")[1].split(",")) == 2:
                        srcs = line.split(":")[3].split("   ")[1].split(",")[1].strip(" ").strip("%")
                        if "0x" in srcs or srcs == "0" or srcs == " " or "ctrl" in srcs or srcs == "":
                            src_regs = ["None"]
                        else:
                            src_regs = [srcs]
                    


                    for i in control_ops:
                        if i in op or i in line:
                            is_ctrl = "True"
                    


                if dst_reg not in all_regs:
                        dst_reg = "None"

                # print(len(all_regs))
                # exit(0)

            # print (tick, pc, op, src_regs, src_mem_reg, is_mem, mem_loc, dst_reg)
            # print (tick, pc, op, corrupted_map )
            if is_ctrl == "True" :
                if "set" in op:
                    flags_checked = control_flag_map["set"]
                elif "cmov" in op:
                    flags_checked = control_flag_map["cmov"]
                elif "loop" in op:
                    flags_checked = control_flag_map["loop"]
                elif "ret" in op:
                    flags_checked = control_flag_map["ret"]
                else:
                    flags_checked = control_flag_map[op]
                for fl in flags_checked:
                    if all_flag_track_map[fl] == "not_clean":
                        # print ("CONtrol flow issue")
                        return [0 , fi_arg]
                    elif "cx" in fl:
                        # check corrupted map if ecx is corrupted 
                        corr_list = get_corrup_list(corrupted_map)
                        if "cx" in corr_list or "ch" in corr_list or "cl" in corr_list or "ecx" in corr_list or "rcx" in corr_list:
                            return [0 , fi_arg]

                prev_line = line
                continue


            instr_exectued = instr_exectued + 1
            
            if "Write" in line and is_mem == "True":
                is_store = 1 
                store_loc = line.split(" ")[3].strip("\n")
            if "Read" in line and is_mem == "True":
                is_load = 1
                load_loc = line.split(" ")[3].strip("\n")

            src_reg_alias = []
            src_mem_reg_alias = []
            corrupted_alias_list = get_corrup_list(corrupted_map)

            for i in range(len(src_regs)):
                for j in range(len(reg_alias_map[src_regs[i]])):
                    src_reg_alias.append(reg_alias_map[src_regs[i]][j])

            for i in range(len(src_mem_reg)):
                for j in range(len(reg_alias_map[src_mem_reg[i]])):
                    src_mem_reg_alias.append(reg_alias_map[src_mem_reg[i]][j])


            dst_reg_alias       = reg_alias_map[dst_reg]
            dst_check = check_reg_in_corr_map(dst_reg, corrupted_map)       # returns none if dst is not in corrupted map

            if "set" in op or "cmov" in op:
                # this means that there are no source regs, these use flags to decide whether or not to move something
                # so  if any flag is corrupted - destination is corrupted
                if "set" in op:
                    flags_checked = control_flag_map["set"]
                elif "cmov" in op:
                    flags_checked = control_flag_map["cmov"]
                for fl in flags_checked:
                    if all_flag_track_map[fl] == "not_clean":
                        # put destination in corrupted map
                        if dst_check == None and dst_reg != "None":
                            corrupted_map[dst_reg] = dst_reg_alias
                            corrupted_count += 1



            if intersection(corrupted_alias_list, src_reg_alias) != [] or intersection(corrupted_alias_list, src_mem_reg_alias) != []:
                #  we are most likely corrupting something here - reg or mem
                # source is corrupted
                update_flags(op, "not_clean")
                
                if is_store == 1:
                    # corrupt a mem location, 
                    corrupted_map[store_loc] = ["mem"]
                    corrupted_count += 1

                elif is_load == 1:
                    # loads can be corrupted even if src regs not corrupted (wrong val in mem)
                    #  but since we have reached here, the source reg is on the watch list, so mem location is likely to be different altogether
                    #  better not flag it as masked and actually do the injection
                    return [0 , fi_arg]
                elif dst_check != None:
                    # this means dst is already in corr_map
                    # normally this would mean that we are writing to a corrupted destination, but since source is also corrupted, no masking in this step
                    prev_line = line
                    continue
                elif dst_reg != "None":
                # not store, not load , fresh destination which is getting corrupted here
                    corrupted_map[dst_reg] = dst_reg_alias
                    corrupted_count += 1

            elif dst_check != None:
                # this means that source is clean ? (just check if it is load and with a clean memory) and destination is not, so this will mean masking of this register
                # clear the entry from corrupted map
                
                # corrupted_count += 1
                if is_load == 1:
                    if load_loc not in corrupted_map:
                        # clean load, masking
                        # corrupted_map.remove(dst_check)
                        update_flags(op, "clean")
                        # del corrupted_map[dst_check]
                    elif load_loc in corrupted_map:
                        # dst is not clean, but source is also not clean.
                        update_flags(op, "not_clean")
                        prev_line = line
                        continue
                # corrupted_map.remove(dst_check)
                # check if the error was injected in the same tick in this register, if so then don't delete
                if tick != inj_tick or inj_reg != dst_reg or src_dst != "1":
                    del corrupted_map[dst_check]   
                else:
                    update_flags(op, "not_clean")
              

            elif is_load == 1:
                # everything is clean but there is a load, so just check if load is from clean address
                if load_loc in corrupted_map:
                    update_flags(op, "not_clean")
                    corrupted_map[dst_reg] = dst_reg_alias
                    corrupted_count += 1
            elif is_store == 1:
                update_flags(op, "clean")
                # everything is clean, check the store loc, if it corrupted then this means masking
                if store_loc in corrupted_map:
                    # corrupted_map.remove(store_loc)
                    del corrupted_map[store_loc]
            prev_line = line
    return [0, fi_arg]



if __name__ == '__main__':

    if len(sys.argv) != 3:
        print('Usage: python prune_trace.py [app] [MAX Workers/threads]') 
        exit()

    isa = 'x86'
    approx_dir = os.environ.get('APPROXGEM5')
    app_name = sys.argv[1]
    MAXWORKERS = int(sys.argv[2])

    # get the tick from here
    masked_inj_loc = approx_dir + '/workloads/' + isa + '/apps/' + app_name
    masked_inj_file = masked_inj_loc + '/' + app_name + '_inj_masked_list.txt'
    total_inj = masked_inj_loc + '/' + app_name + '_inj_100_list.txt'

    # get the pc from here:
    tick_pc_database = masked_inj_loc + '/' + app_name + '_clean_dump_parsed_merged.txt'
    inst_parsed = masked_inj_loc + '/' + app_name + '_parsed.txt'

    # get the pc and instruction from here
    disAssembly = masked_inj_loc + '/' + app_name + '.dis'
    dyn_trace = approx_dir + '/workloads/' + isa + '/checkpoint/' + app_name + '/' + app_name + '_dump_micro_small'


    selected_inj_list_loc = masked_inj_loc + '/selected_inj_list/'
    pc_list_name = selected_inj_list_loc + 'masked_pc_list.txt'
    equivalence_inj = masked_inj_loc + '/' + app_name + '_inj_equivalence_class.txt'    ## inj_tick, inj_reg, src_dest, count
    # output_file_name = selected_inj_list_loc + app_name + '_inj_list_pc_' + sys.argv[2]


    raw_output_dir = approx_dir + '/gem5/outputs/' + 'x86/'
    outcomes_file = app_name + 'dynamic_masked_outcomes.txt'

    tick_pc = get_tick_pc(tick_pc_database)

    masked_inj = []
    masked_map = set()

    pc_details = get_pc_details(inst_parsed)

    for regs in reg_alias_map:
        all_regs.add(regs)
#################################################################################


    with open(equivalence_inj) as file1:
        processing_tuple = []
        results = []
        fi = []
        for line in file1:
            # fill up the parallel tasks
            if len(processing_tuple) < MAXWORKERS:
                fi_arg = line.split("\n")[0]
                tup = [fi_arg, pc_details, tick_pc_database, tick_pc, dyn_trace]
                processing_tuple.append(tup)
            else:
            # launch parallel threads
                with concurrent.futures.ProcessPoolExecutor(max_workers=MAXWORKERS) as executor:
                    results = executor.map(check_masking, processing_tuple)
            
                # process the outputs
                for i in results:
                    if i[0] == 1:
                        inj_tick = i[1].split(",")[0]
                        inj_reg = i[1].split(",")[1]
                        inj_src_dst = i[1].split(",")[2]
                        key = inj_tick + ","  + inj_reg + "," + inj_src_dst
                        masked_map.add(key)
                        # masked_inj.append(i[1])
                    # print i
                #
                processing_tuple = []

                # print (len(masked_map))
                # exit(0)

    tot_inj_map = {}
    with open(total_inj) as file2:
        for line in file2:
            fi_arg = line.strip("\n")
            tick = fi_arg.split(",")[1]
            reg = fi_arg.split(",")[2]
            src_dst = fi_arg.split(",")[5]
            key = tick + ","  + reg + "," + src_dst
            if key in masked_map:
                masked_inj.append(fi_arg)



################################################################################## DEBUG

    # fi_arg = "135688813524500,rcx,0"
    # inj_tick, inj_reg, src_dst, inj_pc = get_inj_details(fi_arg)
    
    
    
    # # print fi_arg
    # tup = [fi_arg, pc_details, tick_pc_database, tick_pc, dyn_trace]
    # masking = check_masking(tup)

    # print (masking[0] ,  "##################")

    # exit(0)

    # print (len(masked_inj))

    with open(outcomes_file, 'w') as f:
        for i in masked_inj:
            f.write(('%s\n' % i))


