# To go through the outcomes of single bit flip experiment and check which ones are "Masked"
# arg 1 : fi_arg
# arg 2 : id
# arg 3 : app_name
# Usage: python comp_exec_trace.py [fi_arg] [id] [app_name]

import gzip
import io
import os
import sys
import random
import collections
import operator
from file_read_backwards import FileReadBackwards

Reg_map = {}
Reg_map["rax"]   = "reg 0"  
Reg_map["eax"]   = "reg 0"  
Reg_map["ax"]   = "reg 0"  
Reg_map["al"]   = "reg 0"  

Reg_map["rcx"]   = "reg 1"
Reg_map["ecx"]   = "reg 1"
Reg_map["cx"]   = "reg 1"
Reg_map["cl"]   = "reg 1"

Reg_map["rdx"]   = "reg 2"
Reg_map["edx"]   = "reg 2"
Reg_map["dx"]   = "reg 2"
Reg_map["dl"]   = "reg 2"

Reg_map["rbx"]   = "reg 3"
Reg_map["ebx"]   = "reg 3"
Reg_map["bx"]   = "reg 3"
Reg_map["bl"]   = "reg 3"

Reg_map["rsp"]   = "reg 4"     
Reg_map["esp"]    = "reg 4" 
Reg_map["sp"] = "reg 4" 
Reg_map["spl"] = "reg 4" 
Reg_map["ah"] = "reg 4" 

Reg_map["rbp"]   = "reg 5"     
Reg_map["ebp"]   = "reg 5"
Reg_map["bp"]   = "reg 5"
Reg_map["bpl"]   = "reg 5"
Reg_map["ch"]   = "reg 5"

Reg_map["rsi"]   = "reg 6"     
Reg_map["esi"]   = "reg 6"  
Reg_map["si"]   = "reg 6"  
Reg_map["sil"]   = "reg 6"  
Reg_map["dh"]   = "reg 6"  

Reg_map["rdi"]   = "reg 7"  
Reg_map["edi"]   = "reg 7"
Reg_map["di"]   = "reg 7"
Reg_map["dil"]   = "reg 7"
Reg_map["bh"]   = "reg 7"

Reg_map["r8"]    = "reg 8" 
Reg_map["r8d"]    = "reg 8"
Reg_map["r8w"]    = "reg 8"
Reg_map["r8b"]    = "reg 8"

Reg_map["r9"]    = "reg 9" 
Reg_map["r9d"]    = "reg 9" 
Reg_map["r9w"]    = "reg 9" 
Reg_map["r9b"]    = "reg 9" 

Reg_map["r10"]   = "reg 10"     
Reg_map["r10d"]   = "reg 10"     
Reg_map["r10w"]   = "reg 10"     
Reg_map["r10b"]   = "reg 10"     

Reg_map["r11"]   = "reg 11"     
Reg_map["r11d"]   = "reg 11"
Reg_map["r11w"]   = "reg 11"
Reg_map["r11b"]   = "reg 11"

Reg_map["r12"]   = "reg 12"     
Reg_map["r12d"]   = "reg 12"     
Reg_map["r12w"]   = "reg 12"     
Reg_map["r12b"]   = "reg 12"     

Reg_map["r13"]   = "reg 13"     
Reg_map["r13d"]   = "reg 13"     
Reg_map["r13w"]   = "reg 13"     
Reg_map["r13b"]   = "reg 13"     

Reg_map["r14d"]   = "reg 14"     
Reg_map["r14w"]   = "reg 14"     
Reg_map["r14b"]   = "reg 14"     
Reg_map["r14"]   = "reg 14"     

Reg_map["r15"]   = "reg 15"     
Reg_map["r15d"]   = "reg 15"     
Reg_map["r15w"]   = "reg 15"     
Reg_map["r15b"]   = "reg 15"    

Reg_map["xmm0"]         =       "float reg 8"                                      
Reg_map["xmm1"]         =       "float reg 10"                                      
Reg_map["xmm2"]         =       "float reg 12"                                      
Reg_map["xmm3"]         =       "float reg 14"                                      
Reg_map["xmm4"]         =       "float reg 16"                                      
Reg_map["xmm5"]         =       "float reg 18"                                      
Reg_map["xmm6"]         =       "float reg 20"                                      
Reg_map["xmm7"]         =       "float reg 22"                                      
Reg_map["xmm8"]         =       "float reg 24"                                      
Reg_map["xmm9"]         =       "float reg 26"                                      
Reg_map["xmm10"]         =       "float reg 28"                                      
Reg_map["xmm11"]         =       "float reg 30"                                      
Reg_map["xmm12"]         =       "float reg 32"                                      
Reg_map["xmm13"]         =       "float reg 34"                                      
Reg_map["xmm14"]         =       "float reg 36"                                      
Reg_map["xmm15"]         =       "float reg 38"



reverse_Reg_map = {}
reverse_Reg_map["reg 0"  ]    =    "rax"        
reverse_Reg_map["reg 1"  ]    =    "rcx"        
reverse_Reg_map["reg 2"  ]    =    "rdx"        
reverse_Reg_map["reg 3"  ]    =    "rbx"        
reverse_Reg_map["reg 4"  ]    =    "rsp"        
reverse_Reg_map["reg 5"  ]    =    "rbp"        
reverse_Reg_map["reg 6"  ]    =    "rsi"        
reverse_Reg_map["reg 7"  ]    =    "rdi"        
reverse_Reg_map["reg 8" ]     =    "r8"         
reverse_Reg_map["reg 9" ]     =    "r9"         
reverse_Reg_map["reg 10" ]    =    "r10"        
reverse_Reg_map["reg 11" ]    =    "r11"        
reverse_Reg_map["reg 12" ]    =    "r12"        
reverse_Reg_map["reg 13" ]    =    "r13"        
reverse_Reg_map["reg 14" ]    =    "r14"        
reverse_Reg_map["reg 15" ]    =    "r15"        



# float_reg_map = {}
# # We are only considering lower 64 bits of XMMs as gem5-approx doesn't support higher 64 bits
# float_reg_map["xmm0"]         =       "float reg 8"                                      
# float_reg_map["xmm1"]         =       "float reg 10"                                      
# float_reg_map["xmm2"]         =       "float reg 12"                                      
# float_reg_map["xmm3"]         =       "float reg 14"                                      
# float_reg_map["xmm4"]         =       "float reg 16"                                      
# float_reg_map["xmm5"]         =       "float reg 18"                                      
# float_reg_map["xmm6"]         =       "float reg 20"                                      
# float_reg_map["xmm7"]         =       "float reg 22"                                      
# float_reg_map["xmm8"]         =       "float reg 24"                                      
# float_reg_map["xmm9"]         =       "float reg 26"                                      
# float_reg_map["xmm10"]         =       "float reg 28"                                      
# float_reg_map["xmm11"]         =       "float reg 30"                                      
# float_reg_map["xmm12"]         =       "float reg 32"                                      
# float_reg_map["xmm13"]         =       "float reg 34"                                      
# float_reg_map["xmm14"]         =       "float reg 36"                                      
# float_reg_map["xmm15"]         =       "float reg 38"                                      



def get_last_line(path_1, path_2):
    with open(path_1, 'rb') as f:
        f.seek(-2, os.SEEK_END)
        while f.read(1) != b'\n':
            f.seek(-2, os.SEEK_CUR)
        last_line_1 = f.readline().decode()
    with open(path_2, 'rb') as f2:
        f2.seek(-2, os.SEEK_END)
        while f2.read(1) != b'\n':
            f2.seek(-2, os.SEEK_CUR)
        last_line_2 = f2.readline().decode()
        # print("######")
        # print (last_line_1)
        # print ("######")
    return last_line_1, last_line_2


def get_val(curr_line):
    ret_val = ""
    if "int" in curr_line:
        ret_val = curr_line.split(":")[3].strip(" ").split(" ")[6].strip(".\n")
    elif "float" in curr_line:
        ret_val = curr_line.split(":")[3].strip(" ").split(" ")[7].strip(",")
    return ret_val


def get_reg(curr_line):
    ret_reg = ""
    if "int" in curr_line:
        ret_reg = "reg " + curr_line.split(":")[3].strip(" ").split(" ")[3]
    elif "float" in curr_line:
        ret_reg = "float reg " + curr_line.split(":")[3].strip(" ").split(" ")[3]
    return ret_reg


def handle_control_flow(path_1, path_2, injection_tick):
    # The idea is to iterate the file bottom up, until you find the divergence point
    # the divergence point can be a different PC being executed, or register/memory values start being different
    # if we reach the injection point (inj_tick) without reaching a divergence point, then we have a potential bug
    
    with FileReadBackwards(path_1, encoding="utf-8") as origF, FileReadBackwards(path_2, encoding="utf-8") as errorF:
    
        o_last_line, e_last_line = get_last_line(path_1, path_2)
        o_last_tick = o_last_line.split(":")[0]
        e_last_tick = e_last_line.split(":")[0]
        # print (e_last_tick, o_last_tick)
        while True:
            ol = origF.readline()
            el = errorF.readline()

            o_tick = ol.split(":")[0]
            e_tick = el.split(":")[0]
            rest_of_ol = ol.split(o_tick)[1]
            rest_of_el = el.split(e_tick)[1]
            
            if rest_of_el != rest_of_ol:
                tot_cycles_after_inj = int(e_last_tick) - int(injection_tick)
                cyc_inj_merging = int(e_tick)  - int(injection_tick)
                cyc_merge_end = int(e_last_tick) - int(e_tick)
                perc_cyc_merge_end_tot = (float(cyc_merge_end)/float(e_last_tick)) * 100
                perc_cyc_merge_end_after_inj = (float(cyc_merge_end)/float(tot_cycles_after_inj)) * 100

                print ("\n")
                print ("Error line = \n"  + el)
                print ("Original line = \n"  + ol)
                print ("Difference (err-orig) in cycle count between error free and faulty execution               =  " + str(int(e_last_tick) - int(o_last_tick)))
                print ("TOTAL Number of cycles after injection point                                               =  " + str (tot_cycles_after_inj))
                print ("Number of cycles between injection and merging states                                      =  " + str(cyc_inj_merging))
                print ("Number of cycles remaining after states were merged                                        =  " + str(cyc_merge_end))
                print ("Percentage of cycles remaining after states were merged (out of total cycles)              =  " + str (perc_cyc_merge_end_tot ))
                print ("Percentage of cycles remaining after states were merged (out of cycles bet inj and end)    =  " + str (perc_cyc_merge_end_after_inj ))
                break
            
    exit(0)

def check_control_flow(path_1, path_2, injection_tick):
    Orig_last_line, Error_last_line = get_last_line(path_1, path_2)
    if Orig_last_line != Error_last_line:
        
        print("CONTROL FLOW DIVERGENCE  :: Not generating the error execution path")
        handle_control_flow(path_1, path_2, injection_tick)
        # print (Orig_last_line)
        # print (Error_last_line)
        exit(0)
    else:
        last_tick =  Orig_last_line.split(":")[0]
        return last_tick


if __name__ == '__main__':

    if len(sys.argv) != 4:
        print('Usage: python comp_exec_trace.py [fi_arg] [id] [app_name] ')
        exit()

    isa = 'x86'
    approx_dir = os.environ.get('APPROXGEM5')
    idNUM = sys.argv[2]
    app_name = sys.argv[3]
    fi_arg = sys.argv[1]

    inj_tick = fi_arg.split(",")[1].strip("")
    inj_src_dst = int(fi_arg.split(",")[5].strip(""))            # 0 is source and 1 is destination
    fi_inj = fi_arg.split(",")[2].strip("")
    inj_reg = Reg_map[fi_inj]

    # raw_output_dir = approx_dir + '/gem5/outputs/' + 'x86/'
    # outcomes_file = raw_output_dir + '/' + sys.argv[2]
    ckpt_dir = approx_dir +  "/workloads/x86/checkpoint/" + app_name
    TMP_DIR = "/scratch/rahuls10/" + app_name + "-m5out_" + idNUM
    
    errorTrace = TMP_DIR  + "/" + app_name + "_dump_micro"
    origTrace = ckpt_dir + "/" + app_name + "_dump_micro"

    inj_point = 1
    track_mismatch = {}                         # Details of regs we are tracking (dictionary)
    # Dict[reg] = [[tick, pc, instr, value, correct value, src_dest]]

    track_regs = set()                             # Set of registers to track
    track_addrs = set()                            # Set of addresses to track
    track_tick = 1
    del_reg = 999
    prev_orig_line = ""
    prev_error_line = ""
    store_inst = 0
    track_dest = 0
    origValue = ""
    pc = ""
    inst = ""
    dst_reg = ""
    dst_orig_val = ""
    dst_mem_loc = ""
    dst_mem_val = ""
    errorValue = ""
    dst_error_value = ""
    dst_mem_error_value = ""



    with open(origTrace) as orig, open(errorTrace) as error:
        origTick = 0
        errorTick = 0
        last_tick = check_control_flow(origTrace, errorTrace, inj_tick)
        # ##### Step 1 :  Reaching the injection point
        #########################################################################################################################################
        #########################################################################################################################################
        while inj_point == 1:
            Oline = orig.readline()
            Eline = error.readline()
            if (inj_tick not in Oline or inj_tick not in Eline):
                continue
            else:
                break
            # elif inj_point == 1:
            #     if Oline ==  Eline and "Setting int reg 16 (16) to 0." in Oline:
            #         continue
            #     else:
            #         inj_point = 0
            


        while inj_tick in Oline:
            if inj_src_dst == 0:
                # we are injecting error in source
                if inj_reg in Oline and "Reading" in Oline:
                    origValue = get_val(Oline)
                elif fi_inj in Oline or "tid" not in Oline:
                    pc = Oline.split(":")[1].strip(" ").split(" ")[1]
                    inst = Oline.split(":")[2].strip(" ") + ": " + Oline.split(":")[3].strip(" ")
                    if "Setting" in prev_orig_line:
                        dst_reg = "reg " + prev_orig_line.split(":")[3].strip(" ").split(" ")[3]
                        dst_orig_val = get_val(prev_orig_line)
                        if "float" in prev_orig_line:
                            dst_reg = "float " + dst_reg
                        
                    elif "A=" in Oline and "st" in inst:
                        store_inst = 1
                        dst_mem_loc = Oline.split(":")[-1].strip(" ")
                        dst_mem_val = origValue                         # TODO: NOt necessarily true, error may have been injected in addr calculation
                    else:
                        print(Oline)
                        print("BUG 1: ERROR: Line just above instruction is weird ")
            else:
                # we are injecting error in destination
                if inj_reg in Oline and "Setting" in Oline:
                    origValue = get_val(Oline)
                    
                elif fi_inj in Oline or "tid" not in Oline:
                    if "TEST" in Oline:
                        origValue = get_val(prev_orig_line)

                    pc = Oline.split(":")[1].strip(" ").split(" ")[1]
                    inst = Oline.split(":")[2].strip(" ") + ": " + Oline.split(":")[3].strip(" ")
            prev_orig_line  = Oline
            Oline = orig.readline()

        # print (origValue)

# For Eline we need to track as well, the destination will be written as a wrong value
        while inj_tick in Eline:
            if inj_src_dst == 0:
                #  We are injecting error in source
                if inj_reg in Eline and "Reading" in Eline:
                    errorValue = get_val(Eline)

                elif fi_inj in Eline or "tid" not in Eline:
                    assert pc == Eline.split(":")[1].strip(" ").split(" ")[1], "EEROR: PC is not same as Orig while injection"
                    assert inst == Eline.split(":")[2].strip(" ") + ": " + Eline.split(":")[3].strip(" "), "ERROR: Instruction is not same as Orig"
                    if "Setting" in prev_error_line and store_inst == 0:
                        
                        if "int" in prev_error_line:
                            assert dst_reg == "reg " + prev_error_line.split(":")[3].strip(" ").split(" ")[3], "dst regs not same in both files"
                            dst_error_value = prev_error_line.split(":")[3].strip(" ").split(" ")[6].strip(".\n")
                        elif "float" in prev_error_line:
                            assert dst_reg == "float reg " + prev_error_line.split(":")[3].strip(" ").split(" ")[3], "dst regs not same in both files"
                            dst_error_value = prev_error_line.split(":")[3].strip(" ").split(" ")[7].strip(",")

                            # if destination is same as source, either the dst val can be same (correct) or wrong
                            # if same: then value just got masked here, exit the program
                            # if different: track the register/memory
                        
                        if dst_orig_val != dst_error_value:
                            track_dest = 1
                        else:
                            
                            if dst_reg == inj_reg:
                                print ( inj_tick, dst_orig_val, dst_error_value)
                                print("Destination same as injected source")
                                exit()            # TODO: understand in more detail, no issues it seems


                    elif "A=" in Eline and "st" in inst:
                        # if the destinations are not equal then error must have been injected in address calculation so add both regs to tracking
                        e_dst_store_addr = Eline.split(":")[-1].strip(" ") 
                        if dst_mem_loc == e_dst_store_addr:
                            dst_mem_error_value = errorValue        
                        else:
                            # different store addresses
                            dst_mem_error_value = "Don't know/Older value in Correct loc"
                            track_addrs.add(e_dst_store_addr)
                            mismatch_details = [inj_tick, pc, inst, "WRONG ADDR Don't know/Older value", get_val(prev_error_line), 1]
                            mismatch_details[2] = mismatch_details[2] + " || Store Addr = " + e_dst_store_addr
                            track_mismatch["MEM " + e_dst_store_addr] =   [mismatch_details]
                    else:
                        print(Eline)
                        print("BUG 2: ERROR: Line just above instruciton is weird ")


            prev_error_line = Eline
            Eline = error.readline()
        
        if inj_src_dst == 1:
            # Error injected in destination, then we need to jump a couple of more instrucitions.
            while "reg 16" in Oline:
                prev_orig_line = Oline
                Oline = orig.readline()
            while "reg 16" in Eline:
                prev_error_line = Eline
                Eline = error.readline()

            if inj_reg in Eline:
                if "Reading" in Eline:
                    prev_error_line = Eline
                    Eline = error.readline()
            
                    if "Setting" in Eline:
                        errorValue = get_val(Eline)

                        prev_error_line = Eline
                        Eline = error.readline()

            while "reg 16" in Eline:
                prev_error_line = Eline
                Eline = error.readline()


        # inst = "xx"
        # pc = "xx"
        prev_error_line = Eline
        prev_orig_line  = Oline

        track_regs.add(inj_reg)
        mismatch_details = [inj_tick, pc, inst, origValue, errorValue, inj_src_dst]
        
        if store_inst == 1:
            track_addrs.add(dst_mem_loc)
            mismatch_details[2] = mismatch_details[2] + " || Store Addr = " + dst_mem_loc
            mismatch_details[4] = dst_mem_error_value
            track_mismatch["MEM " + dst_mem_loc] = [mismatch_details]
        
        track_mismatch[inj_reg] = [mismatch_details]

        if track_dest :
            mismatch_details = [inj_tick, pc, inst, dst_orig_val, dst_error_value, "1"]
            if dst_reg not in track_regs:
                track_regs.add(dst_reg)
                track_mismatch[dst_reg] = [mismatch_details]
            else:
                track_mismatch[dst_reg].append(mismatch_details)


    #  ##### Step 3: Taken care of injection part, now have to go through the entire file looking for differences
    #########################################################################################################################################
    #########################################################################################################################################

        # last_tick = check_control_flow(origTrace, errorTrace)

        while True and (len(track_addrs) > 0 or len(track_regs) > 0) :

            origTick = Oline.split(":")[0]
            errorTick = Eline.split(":")[0]
            
            orig_RegStateMap = {}
            orig_MemStateMap = {}

            err_RegStateMap = {}
            err_MemStateMap = {}

            orig_dst_reg = ""
            err_dst_reg = ""

            orig_store_src_reg = ""
            err_store_src_reg = ""

            pc = "xx"
            inst = "xx"

            e_pc = "xx"
            e_inst = "xx"

            is_store = 0
            is_load = 0

            oreg = "xx"
            oval = "xx"
            store_addr = "xx"
            store_value = "xx"
            load_addr = "xx"

            ereg = "xx"
            e_val = "xx"
            e_store_addr = "xx"
            e_store_value = "xx"
            e_load_addr = "xx"

            merge_details = []
            mismatch_details = []

            assert origTick == errorTick, "ERROR 1: we are checking different ticks, need to synchronize this better"


# Gather states from Orig and Error trace for a particular cycle
            while origTick in Oline:
                # if origTick == "135688814873000":
                #     print (Oline)
                if "tid" in Oline:
                    oreg = get_reg(Oline)
                    oval = get_val(Oline)
                    orig_RegStateMap[oreg] = oval
                elif "system.cpu 0x" in Oline:
                    pc = Oline.split(":")[1].strip(" ").split(" ")[1]
                    inst = Oline.split(":")[2].strip(" ") + ": " + Oline.split(":")[3].strip(" ")
                    
                    if "A=" in Oline and "st" in inst:
                        is_store = 1
                        store_addr = Oline.split(":")[-1].strip(" ")
                        if "Reading" in prev_orig_line:
                            store_value = get_val(prev_orig_line)
                            orig_store_src_reg = get_reg(prev_orig_line)
                            orig_MemStateMap[store_addr] = store_value
                    elif "Setting" in prev_orig_line:
                        orig_dst_reg = get_reg(prev_orig_line)
                    
                    if "A=" in Oline and "ld" in inst:
                        is_load = 1
                        load_addr = Oline.split(":")[-1].strip(" ")
                else:
                    break
                
                prev_orig_line = Oline
                Oline = orig.readline()

            while errorTick in Eline:
                # if errorTick == "135688814873000":
                #     print Eline
                if "tid" in Eline:
                    ereg = get_reg(Eline)
                    e_val = get_val(Eline)
                    err_RegStateMap[ereg] = e_val
                elif "system.cpu 0x" in Eline:
                    e_pc = Eline.split(":")[1].strip(" ").split(" ")[1]
                    e_inst = Eline.split(":")[2].strip(" ") + ": " + Eline.split(":")[3].strip(" ")
                    if "A=" in Eline and "st" in e_inst:
                        e_store_addr = Eline.split(":")[-1].strip(" ")
                        if "Reading" in prev_error_line:
                            # print ("DEBUG:: ", errorTick, origTick, store_addr, e_store_addr)
                            if store_addr == e_store_addr:
                                e_store_value = get_val(prev_error_line)
                                err_store_src_reg = get_reg(prev_error_line)
                                err_MemStateMap[e_store_addr] = e_store_value
                            elif store_addr != e_store_addr and pc == e_pc:
                                e_store_value = "Don't know/Older value in Correct loc"
                                err_store_src_reg = get_reg(prev_error_line)
                                err_MemStateMap[store_addr] = e_store_value
                                if e_store_addr not in track_addrs:
                                    track_addrs.add(e_store_addr)
                                mismatch_details = [origTick, pc, inst, "WRONG ADDR Don't know/Older value", get_val(prev_error_line), 1]
                                mismatch_details[2] = mismatch_details[2] + " || Store Addr = " + e_store_addr
                                if e_store_addr in track_mismatch:
                                    track_mismatch["MEM " + e_store_addr].append(mismatch_details)
                                else:
                                    track_mismatch["MEM " + e_store_addr] =   [mismatch_details]

                    elif "Setting" in prev_error_line:
                        err_dst_reg = get_reg(prev_error_line)
                    if "A=" in Eline and "ld" in e_inst:
                        is_load = 1
                        e_load_addr = Eline.split(":")[-1].strip(" ")
                else:
                    break
                prev_error_line = Eline
                Eline = error.readline()
        

            # if errorTick == "135688814873000":
            #     print(err_RegStateMap)
            #     print (orig_RegStateMap)
            #     exit()

# Compare states gathered above
            # assert pc == e_pc, "ERROR 2:: Working on different PCs"
            # assert inst == e_inst, "ERROR 3:: WOrking on different instructions"
            # assert orig_dst_reg == err_dst_reg, "ERROR 5 :: different destinaiton regs"
            if pc != e_pc:
                print (origTick, pc, inst )
                print(errorTick , e_pc, e_inst)
                print ( "ERROR 2:: Working on different PCs")
                break
            elif inst != e_inst:
                print(origTick, pc, inst )
                print(errorTick , e_pc, e_inst)
                print("ERROR 3:: WOrking on different instructions")
                break
            elif orig_dst_reg != err_dst_reg:
                print(origTick, pc, inst , orig_dst_reg)
                print(errorTick , e_pc, e_inst , err_dst_reg)
                print("ERROR 5 :: different destinaiton regs")
                break
            elif "tid" not in Oline and "system.cpu 0x" not in Oline:
                print (Oline)
                print (Eline)
                print (origTick)
                break

            for each_reg in err_RegStateMap:
                if each_reg == orig_dst_reg:
                    src_dst = 1
                else:
                    src_dst = 0
                
                if err_RegStateMap[each_reg] == orig_RegStateMap[each_reg]:
                    #  values are same, so check if we are tracking, if we are then states have merged for this register
                    if each_reg in track_regs:
                        # MERGED
                        assert is_store == 0, "Store instruction can't correct the register"
                        merge_details = [origTick, pc, inst, orig_RegStateMap[each_reg], err_RegStateMap[each_reg], src_dst, "MERGED"]
                        if is_load == 1:
                            merge_details[2] = merge_details[2] + " || Load Addr = " + e_load_addr
                        track_mismatch[each_reg].append(merge_details)
                        track_regs.remove(each_reg)
                else:
                    
                    mismatch_details = [origTick, pc, inst, orig_RegStateMap[each_reg], err_RegStateMap[each_reg], src_dst]
                    if is_store == 1 :
                        mismatch_details[2]  = mismatch_details[2] + " || Store Addr = " + e_store_addr
                    elif is_load == 1:
                        mismatch_details[2]  = mismatch_details[2] + " || Load Addr = " + e_load_addr

                    if each_reg not in track_regs:
                        track_regs.add(each_reg)

                    if each_reg in track_mismatch:
                        track_mismatch[each_reg].append(mismatch_details)
                    else:
                        assert is_store == 0 ,  "Store instruction shouldn't pollute a register"
                        
                        track_mismatch[each_reg] = [mismatch_details]



            for each_mem in err_MemStateMap:
                assert is_store == 1, "If this is not a store then mem state shouldn't be changed"
                if each_mem not in orig_MemStateMap:
                    # Polluted a new memory location, and didn;t store the actual memory
                    print("WEIRD")
                    track_addrs.add(each_mem)
                    track_addrs.add(store_addr)
                    track_mismatch["MEM " + each_mem]   =   [mismatch_details]
                    track_mismatch["MEM " + store_addr] =   [mismatch_details]
                    
                elif err_MemStateMap[each_mem] == orig_MemStateMap[each_mem]:
                    # storing the same value as orig
                    if each_mem in track_addrs:
                        # MERGED
                        merge_details = [origTick, pc, inst, orig_MemStateMap[each_mem], err_MemStateMap[each_mem], "MERGED"]
                        track_mismatch["MEM " + each_mem].append(merge_details)
                        track_addrs.remove(each_mem)
                elif err_MemStateMap[each_mem] != orig_MemStateMap[each_mem]:
                    mismatch_details = [origTick, pc, inst, orig_MemStateMap[each_mem], err_MemStateMap[each_mem]]
                    if each_mem not in track_addrs:
                        track_addrs.add(each_mem)
                    if each_mem in track_mismatch:
                        track_mismatch["MEM " + each_mem].append(mismatch_details)
                    else:
                        track_mismatch["MEM " + each_mem] = [mismatch_details]

            prev_error_line = Eline
            prev_orig_line  = Oline
            Eline = error.readline()    
            Oline = orig.readline()
            if Oline.split(":")[0] == last_tick:
                print("Reached End of Simulation")
                break

# PRINT

        for keys in track_mismatch:
            print (":: "+ keys)

            for entries in track_mismatch[keys]:
                print (entries)
            print("\n\n")

        print("Final point where things are together::")
        print("Registers not merged =") 
        print(track_regs)
        print("\n")
        print("Memories not merged  = ") 
        print(track_addrs)

        print("\n")
        print ("Error line = \n" + Eline)
        print ("Original line = \n" + Oline)    

        e_tick = Eline.split(":")[0]
        o_tick = Oline.split(":")[0]    

        tot_cycles_after_inj = int(last_tick) - int(inj_tick)
        cyc_inj_merging = int(e_tick)  - int(inj_tick)
        cyc_merge_end = int(last_tick) - int(e_tick)
        perc_cyc_merge_end_tot = (float(cyc_merge_end)/float(last_tick)) * 100
        perc_cyc_merge_end_after_inj = (float(cyc_merge_end)/float(tot_cycles_after_inj)) * 100

        print ("Difference (err-orig) in cycle count between error free and faulty execution               =  " + str(0))
        print ("TOTAL Number of cycles after injection point                                               =  " + str (tot_cycles_after_inj))
        print ("Number of cycles between injection and merging states                                      =  " + str(cyc_inj_merging))
        print ("Number of cycles remaining after states were merged                                        =  " + str(cyc_merge_end))
        print ("Percentage of cycles remaining after states were merged (out of total cycles)              =  " + str (perc_cyc_merge_end_tot ))
        print ("Percentage of cycles remaining after states were merged (out of cycles bet inj and end)    =  " + str (perc_cyc_merge_end_after_inj ))