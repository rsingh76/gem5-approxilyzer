# Gives following info:
# 1. how many errors have control flow div out of the masked ones
# 2. how many states don't converge vs how many do 
# 3. Histogram of how many cycles does it take to converge
# read the raw outcome of masked error injection

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



def read_times(path_1):

    correct_execution_ticks = 0
    faulty_exec_ticks = 0
    Injection_tick = 0
    Diff_orig_error_ticks = 0
    tot_cycles_after_inj = 0
    cyc_inj_merge = 0
    cyc_after_merge = 0
    perc_cyc_merge_end_tot = 0
    perc_cyc_merge_end_after_inj = 0

    line = path_1.readline()
    while  "################################################################################" not in line:
        
        if line == "\n":
            line = path_1.readline()
            continue
        else:
            if "=" in line:
                # print line.split("=")[1]
                value = line.split("=")[1].strip(" ").strip("\n")
            if "Correct Execution ticks" in line:
                correct_execution_ticks = value
            elif "Faulty Execution ticks" in line:
                faulty_exec_ticks = value
            elif "Injeciton at tick number" in line:
                Injection_tick = value
            elif "Difference (err-orig)" in line:
                Diff_orig_error_ticks = value
            elif "TOTAL Number of cycles" in line:
                tot_cycles_after_inj = value
            elif "Number of cycles between injection" in line:
                cyc_inj_merge = value
            elif "Number of cycles remaining after" in line:
                cyc_after_merge = value
            elif "(out of total cycles)" in line:
                perc_cyc_merge_end_tot = value
            elif "(out of cycles bet inj and end)" in line:
                perc_cyc_merge_end_after_inj = value
            
            line = path_1.readline()

    return [correct_execution_ticks, faulty_exec_ticks, Injection_tick,Diff_orig_error_ticks, tot_cycles_after_inj, cyc_inj_merge, cyc_after_merge, perc_cyc_merge_end_tot, perc_cyc_merge_end_after_inj]




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

    masked_outcomes = raw_output_dir + '/' + "masking_attempt_2"                  # TODO: Change this 


    fi_arg = ""
    total_bitflips = 0
    actual_count = 0
    last_bitflip_count = 0
    control_flow_count = 0
    matching_states = 0
    diff_states = 0
    reg_mismatch = 0
    mem_mismatch = 0
    both_mismatch = 0
    new_error_injection = 0

    # times
    correct_execution_ticks = 0
    faulty_exec_ticks = 0
    Injection_tick = 0
    Diff_orig_error_ticks = 0
    tot_cycles_after_inj = 0
    cyc_inj_merge = 0
    cyc_after_merge = 0
    perc_cyc_merge_end_tot = 0
    perc_cyc_merge_end_after_inj = 0
    merged_time_list =                  []
    perc_cyc_merge_end_tot_list =       []
    perc_cyc_merge_end_after_inj_list = []
    line_count = 0
    ctrl_merged_time_list =                  []
    ctrl_perc_cyc_merge_end_tot_list =       []
    ctrl_perc_cyc_merge_end_after_inj_list = []
    ctrl_extra_cycles = []
    

    with open(masked_outcomes) as file_1:
        while True and file_1 != None:
            
            line = file_1.readline()
            if line == "":
                break
            # if (total_bitflips%5000 == 0 and total_bitflips != last_bitflip_count) or total_bitflips > 30000:
            #     print total_bitflips
            #     print line
            last_bitflip_count = total_bitflips
            if line == "\n":
                continue
            if "#New_FI" in line:
                new_error_injection = 1
                actual_count += 1
                continue
            elif "################################################################################" in line:
                new_error_injection = 0
                continue
            # elif "BUG" in line:
            #     while "################################################################################" not in line:
            #         line  = file_1.readline()

            if new_error_injection == 1 and "x86," in line:
                fi_arg = line.strip("\n").strip("")
                new_error_injection = 0
            
            if new_error_injection == 0:
                if "FINAL_OUTPUT" in line:
                    if "Control Flow Divergence" in line:
                        # Book keeping for control flow divergence
                            # count how many control flow divergence out of total
                        total_bitflips += 1
                        control_flow_count += 1 
                        # How many cycles it took to converge
                            # check the time as well
                        time_list = read_times(file_1)
                        ctrl_merged_time_list.append(time_list[5])
                        ctrl_perc_cyc_merge_end_tot_list.append(time_list[7])
                        ctrl_perc_cyc_merge_end_after_inj_list.append(time_list[8])
                        ctrl_extra_cycles.append(time_list[3])
                    elif "FINISH and MATCH" in line:
                        # Bookkeeping for merged states
                            # count how many states merge out of total
                        total_bitflips += 1
                        matching_states += 1
                        # How many cycles did it take to converge states
                            #  check the time
                        time_list = read_times(file_1)
                        merged_time_list.append(time_list[5])
                        perc_cyc_merge_end_tot_list.append(time_list[7])
                        perc_cyc_merge_end_after_inj_list.append(time_list[8])

                    elif "REGs state different" in line:
                        # Book keeping for non merged states and different reg states
                            # keep incrementing this count and diff_regs count
                        reg_mismatch += 1
                        diff_states += 1
                        total_bitflips += 1
                        time_list = read_times(file_1)

                    elif "MEMs state different" in line:
                        # Book keeping for non merged states and different mem states
                            # Keep incremementing diff state and diff_mem count
                        mem_mismatch += 1
                        diff_states += 1
                        total_bitflips += 1
                        time_list = read_times(file_1)

                    elif "BOTH regs and mem states are different" in line:
                        # Book keeping for non merged states and different reg and mem states
                            # keep incrementing both counts
                        both_mismatch += 1
                        diff_states += 1
                        total_bitflips += 1
                        time_list = read_times(file_1)
                    
                    elif "Destination same as injected source" in line:
                        total_bitflips += 1 
                        matching_states += 1

                        # time to merge will be zero
                        time_list = ["x", "x", "x", 0, "x", 0, "x", "x", 100]
                        merged_time_list.append(time_list[5])
                        perc_cyc_merge_end_tot_list.append(time_list[7])
                        perc_cyc_merge_end_after_inj_list.append(time_list[8])

    
    for i in ctrl_extra_cycles:
        print i


    print "\n"
    print "Actual count = ", actual_count
    print "Total bitflips = ",total_bitflips
    print "Number of control flows = ", control_flow_count
    print "Number of merged states = ", matching_states
    print "Num of Diff states = ", diff_states
    print "Num of diff mem states = " , mem_mismatch




                    