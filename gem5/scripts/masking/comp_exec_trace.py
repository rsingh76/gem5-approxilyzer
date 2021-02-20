# To go through the outcomes of single bit flip experiment and check which ones are "Masked"
# arg 1 : fi_arg
# arg 2 : error free exec_trace
# arg 3 : erroneous exec trace
# arg 4 : id
# arg 5 : app_name


import gzip
import io
import os
import sys
import random
import collections
import operator


Reg_map = {}
Reg_map["rax"]   = "reg 0"     
Reg_map["rcx"]   = "reg 1"
Reg_map["rdx"]   = "reg 2"
Reg_map["rbx"]   = "reg 3"     
Reg_map["rsp"]   = "reg 4"     
Reg_map["rbp"]   = "reg 5"     
Reg_map["rsi"]   = "reg 6"     
Reg_map["rdi"]   = "reg 7"     
Reg_map["r8"]    = "reg 8" 
Reg_map["r9"]    = "reg 9" 
Reg_map["r10"]   = "reg 10"     
Reg_map["r11"]   = "reg 11"     
Reg_map["r12"]   = "reg 12"     
Reg_map["r13"]   = "reg 13"     
Reg_map["r14"]   = "reg 14"     
Reg_map["r15"]   = "reg 15"     

reverse_Reg_map = {}
reverse_Reg_map["reg 0"  ]    =    "rax"        "reg 0"     
reverse_Reg_map["reg 1"  ]    =    "rcx"        "reg 1"   
reverse_Reg_map["reg 2"  ]    =    "rdx"        "reg 2"   
reverse_Reg_map["reg 3"  ]    =    "rbx"        "reg 3"     
reverse_Reg_map["reg 4"  ]    =    "rsp"        "reg 4"     
reverse_Reg_map["reg 5"  ]    =    "rbp"        "reg 5"     
reverse_Reg_map["reg 6"  ]    =    "rsi"        "reg 6"     
reverse_Reg_map["reg 7"  ]    =    "rdi"        "reg 7"     
reverse_Reg_map["reg 8" ]    =    "r8"         "reg 8" 
reverse_Reg_map["reg 9" ]    =    "r9"         "reg 9" 
reverse_Reg_map["reg 10" ]    =    "r10"        "reg 10"     
reverse_Reg_map["reg 11" ]    =    "r11"        "reg 11"     
reverse_Reg_map["reg 12" ]    =    "r12"        "reg 12"     
reverse_Reg_map["reg 13" ]    =    "r13"        "reg 13"     
reverse_Reg_map["reg 14" ]    =    "r14"        "reg 14"     
reverse_Reg_map["reg 15" ]    =    "r15"        "reg 15"  



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


    with open(origTrace) as orig, open(errorTrace) as error:
        origTick = 0
        errorTick = 0

        # ##### Step 1 :  Reaching the injection point
        #########################################################################################################################################
        #########################################################################################################################################
        while inj_point == 1:
            Oline = orig.readline()
            Eline = error.readline()
            if (inj_tick not in Oline or inj_tick not in Eline):
                continue
            elif inj_point == 1:
                if Oline ==  Eline and "Setting int reg 16 (16) to 0." in Oline:
                    continue
                else:
                    inj_point = 0
            
        inst = "xx"
        pc = "xx"
        prev_error_line = Eline
        prev_orig_line  = Oline

        # print (Oline)
        # print (Eline)
        # exit()
        #  ##### Step 2: Skip the injeciton lines: in case of injeciton in src reg - they are before the execution, otherwise after the execution
        #########################################################################################################################################
        #########################################################################################################################################
        if inj_src_dst == 0:
            # src reg injection
            if "Reading" in Eline:
                errorRegister = Eline.split(":")[3].strip(" ").split(" ")[3]
                origValue = Oline.split(":")[3].strip(" ").split(" ")[6].strip(".\n")
            else:
                print (Oline)
                print (Eline)
                print("ERROR::: BUG ALERT 1")

            Eline = error.readline()

            if "Setting" in Eline:
                errorValue = Eline.split(":")[3].strip(" ").split(" ")[6].strip(".\n")
                temptick = Eline.split(":")[0]
            else:
                print (Oline)
                print (Eline)
                print("ERROR::: BUG ALERT 2")
                exit()

            track_regs.add(errorRegister)

            mismatch_details = [temptick, pc, inst, origValue, errorValue, "src"]
            mismatch_details_2 = []
            prev_error_line = Eline
            Eline = error.readline()

            while "tid" in Oline:
                # Oline = orig.readline()
                # Eline = error.readline()
                if Oline != Eline:
                    if "Reading" in Oline and "Reading" in Eline:
                        curr_reg = Eline.split(":")[3].strip(" ").split(" ")[3]
                        if curr_reg != errorRegister:
                            print (Oline)
                            print (Eline)
                            print("ERROR::: MAJOR BUG 1")
                    elif "Setting" in Oline and "Setting" in Eline:
                        curr_reg = Eline.split(":")[3].strip(" ").split(" ")[3]
                        curr_val = Eline.split(":")[3].strip(" ").split(" ")[6].strip(".\n")
                        right_val = Oline.split(":")[3].strip(" ").split(" ")[6].strip(".\n")
                        if curr_reg == errorRegister:
                            # destination of instruction is the same reg in which we injected error
                            if curr_val != errorValue or right_val != origValue:
                                mismatch_details = [temptick, pc, inst, right_val, curr_val, "src"]
                        else:
                            # different destination and error is propagating
                            track_regs.add(curr_reg)
                            mismatch_details_2 = [temptick, pc, inst, right_val, curr_val, "dst"]

                prev_error_line = Eline
                prev_orig_line  = Oline
                Oline = orig.readline()
                Eline = error.readline()


            pc = Oline.split(":")[1].strip(" ").split(" ")[1]
            inst = Oline.split(":")[2].strip(" ") + ": " + Oline.split(":")[3].strip(" ")
            flag_addr = ""
            if "A=" in Oline:
                if "st" in inst:
                    flag_addr = Oline.split(":")[-1].strip(" ")
                    track_addrs.add(flag_addr)
            mismatch_details[1] = pc
            mismatch_details[2] = inst
            track_mismatch[errorRegister] = [mismatch_details]
            if mismatch_details_2 != []:
                mismatch_details_2[1] = pc
                mismatch_details_2[2] = inst
                track_mismatch[curr_reg] = [mismatch_details_2]

            prev_error_line = Eline
            prev_orig_line  = Oline
            Eline = error.readline()
            Oline = orig.readline()
            # This is ready to begin the comparison
        
        elif inj_src_dst == 1:
            # this means that injection happens after the execution - so note the value of register as a track_regs and so on...
            # skip the lines where there is no difference (difference comes in the next line of execution)
            while "tid" in Oline and Oline == Eline:
                prev_error_line = Eline
                prev_orig_line  = Oline
                Oline = orig.readline()
                Eline = error.readline()
            
            pc = Oline.split(":")[1].strip(" ").split(" ")[1]
            inst = Oline.split(":")[2].strip(" ") + ": " + Oline.split(":")[3].strip(" ")
            
            prev_error_line = Eline
            prev_orig_line  = Oline

            Eline = error.readline()
            Oline = orig.readline()
            # check if the line is setting int reg 16 to 0, if yes then skip an extra line
            if Oline == Eline and "Setting int reg 16 (16) to 0." in Oline:
                prev_error_line = Eline
                prev_orig_line  = Oline
                Oline = orig.readline()
                Eline = error.readline()
            
            # print (Eline)
            # origRegister = Oline.split(":")[3].strip(" ").split(" ")[3]
            if "Reading" in Eline:
                errorRegister = Eline.split(":")[3].strip(" ").split(" ")[3]
                origValue = Eline.split(":")[3].strip(" ").split(" ")[6].strip(".\n")
            else:
                print (Oline)
                print (Eline)
                print("ERROR::: BUG ALERT 3")
                exit()
            # next line will set the value
            prev_error_line = Eline
            Eline = error.readline()
            # We are at line of interest (Error injeciton in Eline) and Oline is at the enxt line from which the comparison will start
            if "Setting" in Eline:
                errorValue = Eline.split(":")[3].strip(" ").split(" ")[6].strip(".\n")
                temptick = Eline.split(":")[0]
            else:
                print (Oline)
                print (Eline)
                print("ERROR::: BUG ALERT 4")
                exit()

            track_regs.add(errorRegister)
            mismatch_details = [temptick, pc, inst, origValue, errorValue, "dst"]
            track_mismatch[errorRegister] = [mismatch_details]
            prev_error_line = Eline
            Eline = error.readline()

            # Now ready to start iterating and comparing Oline and Eline
        # print (track_regs)
        # print (track_mismatch)
        # print (Eline)
        # print (Oline)
        # exit(0)

    #  ##### Step 3: Taken care of injection part, now have to go through the entire file looking for differences
    #########################################################################################################################################
    #########################################################################################################################################

        temp_mismatch = []
        while len(track_regs) > 0 or len(track_addrs) > 0:
            inst = "xx"
            pc = "xx"
            origTick = Oline.split(":")[0]
            errorTick = Eline.split(":")[0]
            if "tid" in Oline and "tid" in Eline:

                errorRegister = Eline.split(":")[3].strip(" ").split(" ")[3]
                origRegister = Oline.split(":")[3].strip(" ").split(" ")[3]
                origValue = Oline.split(":")[3].strip(" ").split(" ")[6].strip(".\n")
                errorValue = Eline.split(":")[3].strip(" ").split(" ")[6].strip(".\n")


                if Oline != Eline:
                    # check if the control flow is different, if yes : leave it for later
                    if errorRegister != origRegister or origTick != errorTick:
                        # COntrol flow problem:
                        print(Eline)
                        print(Oline)
                        print("CONTROL FLOW SEEMS TO HAVE CHANGED")
                        exit(0)

                    else:
                    # otherwise: make entries
                        mismatch_details = [origTick, pc, inst, origValue, errorValue]
                        if "Reading" in Oline and "Reading" in Eline:
                            mismatch_details.append("src")
                        elif "Setting" in Oline and "Setting" in Eline:
                            mismatch_details.append("dst")
                    temp_mismatch.append(errorRegister)
                    if errorRegister not in track_regs:
                        track_regs.add(errorRegister)
                        track_mismatch[errorRegister]= [mismatch_details]
                    else:
                        track_mismatch[errorRegister].append(mismatch_details)
                    # look for the pc and inst, by using while loop, if more mismatches, store in temp mismatch, clear temp_mismatch once we calculate pc and inst
                    prev_error_line = Eline
                    prev_orig_line  = Oline
                    Eline = error.readline()    
                    Oline = orig.readline()

                    while "tid" in Oline and "tid" in Eline:
                        mismatch_details = []
                        if Oline != Eline:
                            curr_reg = Eline.split(":")[3].strip(" ").split(" ")[3]
                            curr_val = Eline.split(":")[3].strip(" ").split(" ")[6].strip(".\n")
                            right_val = Oline.split(":")[3].strip(" ").split(" ")[6].strip(".\n")
                            if "Reading" in Eline and "Reading" in Oline:
                                if curr_reg != errorRegister:
                                    mismatch_details = [errorTick, pc, inst, right_val, curr_val, "src"]
                                else:
                                    if errorValue != curr_val:
                                        print("ERROR::: MAJOR ISSUE")
                                        exit()

                            elif "Setting" in Eline and "Setting" in Oline:
                                if curr_reg == errorRegister:
                                    if curr_val != errorValue or right_val != origValue:
                                        mismatch_details = [errorTick, pc, inst, right_val, curr_val, "dst"]
                                else:
                                    mismatch_details = [errorTick, pc, inst, right_val, curr_val, "dst"]
                            
                            if mismatch_details != []:
                                temp_mismatch.append(curr_reg)
                                if curr_reg not in track_regs:
                                    track_mismatch[curr_reg] = [mismatch_details]
                                    track_regs.add(curr_reg)
                                else:
                                    track_mismatch[curr_reg].append(mismatch_details)
                        prev_error_line = Eline
                        prev_orig_line  = Oline
                        Eline = error.readline()
                        Oline = orig.readline()

                    pc = Eline.split(":")[1].strip(" ").split(" ")[1]
                    inst = Eline.split(":")[2].strip(" ") + ": " + Eline.split(":")[3].strip(" ")

                    for regs in temp_mismatch:
                        track_mismatch[regs][-1][1] = pc
                        track_mismatch[regs][-1][2] = inst
                    
                    if "A=" in Eline:                       # this is a load or store
                        flag_addr = Eline.split(":")[-1].strip(" ")
                        if "ld" in Eline:
                            # in case of loads: get the register from previous instruciton and make sure it is being tracked
                            load_reg = prev_error_line.split(":")[3].strip(" ").split(" ")[3]
                            if load_reg not in track_regs:
                                print("ERROR: Potential bug here")
                                track_regs.add(load_reg)
                                # if load_reg not in track_mismatch:

                        elif "st" in inst:
                            st_reg = prev_error_line.split(":")[3].strip(" ").split(" ")[3]
                            if st_reg in track_regs:
                                track_addrs.add(flag_addr)
                            elif st_reg not in track_regs and flag_addr in track_addrs:
                                track_addrs.remove(flag_addr)
                                
                

                elif Oline == Eline and errorRegister in track_regs and len(track_addrs) == 0:
                    # if track_tick == origTick and errorRegister == del_reg:
                    #     continue
                    if "Reading" in Eline:
                        mismatch_details = [origTick, pc, inst, "MERGED",origValue ,errorValue, "src" ]
                    elif "Setting" in Eline:
                        mismatch_details = [origTick, pc, inst, "MERGED", origValue ,errorValue, "dst" ]
                    track_mismatch[errorRegister].append(mismatch_details)
                    track_tick = origTick
                    del_reg = errorRegister

            elif "tid" not in Eline and "tid" not in Oline:
                pc = Eline.split(":")[1].strip(" ").split(" ")[1]
                inst = Eline.split(":")[2].strip(" ") + ": " + Eline.split(":")[3].strip(" ")
                
                if track_tick == origTick:
                    track_mismatch[del_reg][-1][1] = pc
                    track_mismatch[del_reg][-1][2] = inst
                    track_regs.remove(del_reg)
                
                if "A=" in Eline:
                    flag_addr = Eline.split(":")[-1].strip(" ")
                    ldst_reg = prev_error_line.split(":")[3].strip(" ").split(" ")[3]
                    if "ld" in Eline:
                        if flag_addr in track_addrs:
                            if ldst_reg not in track_regs:
                                print("ERROR::Potential BUG:: load from flagged address - register was not flagged")
                    elif "st" in inst:
                        if flag_addr in track_addrs:
                            if ldst_reg not in track_regs:
                                track_addrs.remove(flag_addr)
                                



            temp_mismatch = []
            prev_error_line = Eline
            prev_orig_line  = Oline
            Eline = error.readline()    
            Oline = orig.readline()



        # print (fi_arg)
        for keys in track_mismatch:
            print ("Register:: "+ keys)
        
            for entries in track_mismatch[keys]:
                print (entries)
            print("\n\n")
        print("Final point where things are together::")
        print (Eline)
        print (Oline)
        
        exit(0)


######################################################################################################
######################################################################################################
######################################################################################################


