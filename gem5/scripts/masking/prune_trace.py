

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



reg_alias_map = {}

reg_alias_map["rax"]  = ["rax"]  
reg_alias_map["eax"]  = ["rax", "eax"]  
reg_alias_map["ax"]   = ["rax", "eax", "ax"]   
reg_alias_map["ah"]   = ["rax", "eax", "ax", "ah"]  
reg_alias_map["al"]   = ["rax", "eax", "ax", "al"]  

reg_alias_map["rcx"]   =["rcx"]  
reg_alias_map["ecx"]   =["rcx", "ecx"]  
reg_alias_map["cx"]   = ["rcx", "ecx", "cxx"]   
reg_alias_map["ch"]   = ["rcx", "ecx", "cx", "ch"]  
reg_alias_map["cl"]   = ["rcx", "ecx", "cx", "cl"]  

reg_alias_map["rdx"]  =  ["rdx"]  
reg_alias_map["edx"]  =  ["rdx", "edx"]  
reg_alias_map["dx"]   =  ["rdx", "edx", "dx"]   
reg_alias_map["dh"]   =  ["rdx", "edx", "dx", "dh"]  
reg_alias_map["dl"]   =  ["rdx", "edx", "dx", "dl"]  

reg_alias_map["rbx"]  = ["rbx"]  
reg_alias_map["ebx"]  = ["rbx", "ebx"]  
reg_alias_map["bx"]   = ["rbx", "ebx", "bx"]   
reg_alias_map["bh"]   = ["rbx", "ebx", "bx", "bh"]  
reg_alias_map["bl"]   = ["rbx", "ebx", "bx", "bl"]  

reg_alias_map["si"]   = ["rsi", "si"]
reg_alias_map["esi"]  = ["rsi", "esi"]
reg_alias_map["edi"]  = ["rsi" , "edi"]
reg_alias_map["rsi"]  = ["rsi"]

reg_alias_map["di"]  =  ["rdi", "di" ]
reg_alias_map["rdi"]  = ["rdi" ]

reg_alias_map["sp"]   = ["rsp", "sp" ]
reg_alias_map["esp"]  = ["rsp", "esp" ]
reg_alias_map["rsp"]  = ["rsp" ]

reg_alias_map["rbp"]   = ["rbp"]
reg_alias_map["ebp"]   = ["rbp", "ebp"]
reg_alias_map["bp"]   =  ["rbp", "bp"]

reg_alias_map["ip"]   =  ["rip", "ip"]
reg_alias_map["eip"]   =  ["rip", "eip"]
reg_alias_map["rip"]   =  ["rip"]

reg_alias_map["r8"]  = ["r8"] 
reg_alias_map["r8d"] = ["r8", "r8d"]
reg_alias_map["r8w"] = ["r8", "r8d", "r8w"]
reg_alias_map["r8b"] = ["r8", "r8d", "r8w", "r8b"]

reg_alias_map["r9"]  = ["r9"]
reg_alias_map["r9d"] = ["r9", "r9d"]
reg_alias_map["r9w"] = ["r9", "r9d", "r9w"]
reg_alias_map["r9b"] = ["r9", "r9d", "r9w", "r9b"]

reg_alias_map["r10"] = ["r10"]
reg_alias_map["r10d"] = ["r10", "r10d"]
reg_alias_map["r10w"] = ["r10", "r10d", "r10w"]
reg_alias_map["r10b"] = ["r10", "r10d", "r10w", "r10b"]

reg_alias_map["r11"] = ["r11"]
reg_alias_map["r11d"] = ["r11", "r11d"]
reg_alias_map["r11w"] = ["r11", "r11d", "r11w"]
reg_alias_map["r11b"] = ["r11", "r11d", "r11w", "r11b"]

reg_alias_map["r12"] = ["r12"] 
reg_alias_map["r12d"] = ["r12", "r12d"]
reg_alias_map["r12w"] = ["r12", "r12d", "r12w"]
reg_alias_map["r12b"] = ["r12", "r12d", "r12w", "r12b"]

reg_alias_map["r13"] = ["r13"] 
reg_alias_map["r13d"] = ["r13", "r13d"]
reg_alias_map["r13w"] = ["r13", "r13d", "r13w"]
reg_alias_map["r13b"] = ["r13", "r13d", "r13w", "r13b"]

reg_alias_map["r14"] = ["r14"]
reg_alias_map["r14d"] = ["r14", "r14d"]
reg_alias_map["r14w"] = ["r14", "r14d", "r14w"]
reg_alias_map["r14b"] = ["r14", "r14d", "r14w", "r14b"]

reg_alias_map["r15"] = ["r15"]
reg_alias_map["r15d"] = ["r15", "r15d"]
reg_alias_map["r15w"] = ["r15", "r15d", "r15w"]
reg_alias_map["r15b"] = ["r15", "r15d", "r15w", "r15b"]

reg_alias_map["xmm1"]         = ["xmm1"]
reg_alias_map["xmm2"]         = ["xmm2"]
reg_alias_map["xmm3"]         = ["xmm3"]
reg_alias_map["xmm0"]         = ["xmm0"]
reg_alias_map["xmm4"]         = ["xmm4"]
reg_alias_map["xmm5"]         = ["xmm5"]
reg_alias_map["xmm6"]         = ["xmm6"]
reg_alias_map["xmm7"]         = ["xmm7"]
reg_alias_map["xmm8"]         = ["xmm8"]
reg_alias_map["xmm9"]         = ["xmm9"]
reg_alias_map["xmm10"]         = ["xmm10"]
reg_alias_map["xmm11"]         = ["xmm11"]
reg_alias_map["xmm12"]         = ["xmm12"]
reg_alias_map["xmm13"]         = ["xmm13"]
reg_alias_map["xmm14"]         = ["xmm14"]
reg_alias_map["xmm15"]         = ["xmm15"]

reg_alias_map["fpr0"]         = ["fpr0"]
reg_alias_map["fpr1"]         = ["fpr1"]
reg_alias_map["fpr2"]         = ["fpr2"]
reg_alias_map["fpr3"]         = ["fpr3"]
reg_alias_map["fpr4"]         = ["fpr4"]
reg_alias_map["fpr5"]         = ["fpr5"]
reg_alias_map["fpr6"]         = ["fpr6"]
reg_alias_map["None"]         = ["None"]


control_flag_map = {}
instr_flag_affect_map = {}
all_flag_track_map = {}

control_flag_map["jo"] = ["OF"]
control_flag_map["jno"] = ["OF"]
control_flag_map["js"] = ["SF"]
control_flag_map["jns"] = ["SF"]
control_flag_map["je"] = ["ZF"]
control_flag_map["jz"] = ["ZF"]
control_flag_map["jne"] = ["ZF"]
control_flag_map["jnz"] = ["ZF"]
control_flag_map["jb"] = ["CF"]
control_flag_map["jnae"] = ["CF"]
control_flag_map["jc"] =  ["CF"]
control_flag_map["jnb"] = ["CF"]
control_flag_map["jae"] = ["CF"]
control_flag_map["jnc"] = ["CF"]
control_flag_map["jbe"] = ["CF", "ZF"]
control_flag_map["jna"] = ["CF", "ZF"]
control_flag_map["ja"] = ["CF", "ZF"]
control_flag_map["jnbe"] = ["CF", "ZF"]
control_flag_map["jl"] = ["SF", "OF"]
control_flag_map["jnge"] = ["SF", "OF"]
control_flag_map["jge"] = ["SF", "OF"]
control_flag_map["jnl"] = ["SF", "OF"]
control_flag_map["jle"] = ["ZF", "SF", "OF"]
control_flag_map["jng"] = ["ZF", "SF", "OF"]
control_flag_map["jg"] = ["ZF", "SF", "OF"]
control_flag_map["jnle"] = ["ZF", "SF", "OF"]
control_flag_map["jp"] = ["PF"]
control_flag_map["jpe"] = ["PF"]
control_flag_map["jnp"] = ["PF"]
control_flag_map["jpo"] = ["PF"]
control_flag_map["jcxz"] = ["cx"]
control_flag_map["jecxz"] = ["ecx"]
control_flag_map["set"] = ["OF", "CF", "ZF", "SF","PF"]            
control_flag_map["cmov"] = ["OF", "CF", "ZF", "SF","PF"]    
control_flag_map["call"] =  []          
control_flag_map["callq"] = []   
control_flag_map["loop"] = ["ZF", "ecx"]
control_flag_map["ret"]  = []
control_flag_map["jmp"] = []
control_flag_map["jmpq"] = []

all_flag_track_map["OF"] = "clean"
all_flag_track_map["SF"] = "clean"
all_flag_track_map["CF"] = "clean"
all_flag_track_map["ZF"] = "clean"
all_flag_track_map["PF"] = "clean"


instr_flag_affect_map["OF"] = ['add', 'sub', 'mul','neg', 'adc', 'sbb', 'inc', 'dec','shl', 'test', 'sqrt']
instr_flag_affect_map["SF"] = ['add', 'sub', 'neg', 'adc', 'sbb', 'inc', 'dec', 'test', 'cmp', 'and', 'or', 'xor', 'maxsd', 'sqrt']
instr_flag_affect_map["CF"] = ['add', 'sub', 'mul', 'div', 'neg', 'adc', 'sbb', 'inc', 'dec', 'and', 'or', 'xor', 'not', 'rotate', 'test', 'cmp', 'ucomisd', 'maxsd', 'sqrt']
instr_flag_affect_map["ZF"] = ['add', 'sub', 'mul', 'div', 'neg', 'adc', 'sbb', 'inc', 'dec', 'and', 'or', 'xor', 'not', 'rotate', 'test', 'cmp', 'ucomisd', 'maxsd','sqrt']
instr_flag_affect_map["PF"] = ['all']    # all instructions except bad

# TODO: figure out - cvtsi2sd,  cvttsd2si, cvtdq2pd, pshufd


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


def get_pc_details(pc, inst_parsed):
    with open(inst_parsed) as file2:
        for line in file2:
            # print line
            if pc in line:
                # print "do i reach here ", pc
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
                 
                return op, is_ctrl, all_src, all_src_mem, is_mem, dst_reg



# def check_masking(fi_arg, inst_parsed, tick_pc_database, tick_pc):
def check_masking(tup):
    
    fi_arg = tup[0] 
    inst_parsed = tup[1]
    tick_pc_database = tup[2]
    tick_pc = tup[3]
    prev_line = "x"
    # return 1 if the error is going to be masked 
    corrupted_count = 1
    instr_exectued = 0
    corrupted_map = {}
    inj_tick, inj_reg, src_dst, inj_pc = get_inj_details(fi_arg)
    inj_alias_reg = reg_alias_map[inj_reg]
    corrupted_map[inj_reg] = inj_alias_reg
    with open(tick_pc_database) as tp_d:
        
        found = 0
        for line in tp_d:
            # if found ==1:
            #     print (line, corrupted_count, corrupted_map)
            if not corrupted_map:
        
                return [1 , fi_arg]
            elif instr_exectued > 10000 :
                return [0 , fi_arg]

            is_load = 0
            is_store = 0
            store_loc = "x"
            load_loc = "x"
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
            
            tick = line.split(" ")[0]
            pc = tick_pc[tick].strip("\n")

            op, is_ctrl, src_regs, src_mem_reg, is_mem, dst_reg = get_pc_details(pc, inst_parsed)
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
    outcomes_file = app_name + '_masked_outcomes.txt'

    tick_pc = get_tick_pc(tick_pc_database)

    masked_inj = []
    masked_map = set()

#################################################################################


    with open(equivalence_inj) as file1:
        processing_tuple = []
        results = []
        fi = []
        for line in file1:
            # fill up the parallel tasks
            if len(processing_tuple) < MAXWORKERS:
                fi_arg = line.split("\n")[0]
                tup = [fi_arg, inst_parsed, tick_pc_database, tick_pc, dyn_trace]
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

    # fi_arg = "135689617878000,xmm0,0"
    # inj_tick, inj_reg, src_dst, inj_pc = get_inj_details(fi_arg)
    
    
    # # print fi_arg
    # tup = [fi_arg, inst_parsed, tick_pc_database, tick_pc, dyn_trace]
    # masking = check_masking(tup)
    
    # print (masking[0] ,  "##################")
            
    # exit(0)

    # print (len(masked_inj))

    with open(outcomes_file, 'w') as f:
        for i in masked_inj:
            f.write(('%s\n' % i))


