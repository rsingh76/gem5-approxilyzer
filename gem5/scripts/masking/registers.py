
import os
import sys
import random
import collections


all_regs = set()
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

# TODO: do the above for t0 - t12
temp_regs = ["t0", "t1", "t2", "t3", "t4", "t5", "t6", "t7", "t8", "t9", "t10", "t11", "t12"]

reg_alias_map["t0"]  = ["t0"] 
reg_alias_map["t0d"] = ["t0", "t0d"]
reg_alias_map["t0w"] = ["t0", "t0d", "t0w"]
reg_alias_map["t0b"] = ["t0", "t0d", "t0w", "t0b"]

reg_alias_map["t1"]  = ["t1"] 
reg_alias_map["t1d"] = ["t1", "t1d"]
reg_alias_map["t1w"] = ["t1", "t1d", "t1w"]
reg_alias_map["t1b"] = ["t1", "t1d", "t1w", "t1b"]

reg_alias_map["t2"]  = ["t2"] 
reg_alias_map["t2d"] = ["t2", "t2d"]
reg_alias_map["t2w"] = ["t2", "t2d", "t2w"]
reg_alias_map["t2b"] = ["t2", "t2d", "t2w", "t2b"]

reg_alias_map["t3"]  = ["t3"] 
reg_alias_map["t3d"] = ["t3", "t3d"]
reg_alias_map["t3w"] = ["t3", "t3d", "t3w"]
reg_alias_map["t3b"] = ["t3", "t3d", "t3w", "t3b"]

reg_alias_map["t4"]  = ["t4"] 
reg_alias_map["t4d"] = ["t4", "t4d"]
reg_alias_map["t4w"] = ["t4", "t4d", "t4w"]
reg_alias_map["t4b"] = ["t4", "t4d", "t4w", "t4b"]

reg_alias_map["t5"]  = ["t5"] 
reg_alias_map["t5d"] = ["t5", "t5d"]
reg_alias_map["t5w"] = ["t5", "t5d", "t5w"]
reg_alias_map["t5b"] = ["t5", "t5d", "t5w", "t5b"]

reg_alias_map["t6"]  = ["t6"] 
reg_alias_map["t6d"] = ["t6", "t6d"]
reg_alias_map["t6w"] = ["t6", "t6d", "t6w"]
reg_alias_map["t6b"] = ["t6", "t6d", "t6w", "t6b"]

reg_alias_map["t7"]  = ["t7"] 
reg_alias_map["t7d"] = ["t7", "t7d"]
reg_alias_map["t7w"] = ["t7", "t7d", "t7w"]
reg_alias_map["t7b"] = ["t7", "t7d", "t7w", "t7b"]

reg_alias_map["t8"]  = ["t8"] 
reg_alias_map["t8d"] = ["t8", "t8d"]
reg_alias_map["t8w"] = ["t8", "t8d", "t8w"]
reg_alias_map["t8b"] = ["t8", "t8d", "t8w", "t8b"]

reg_alias_map["t9"]  = ["t9"]
reg_alias_map["t9d"] = ["t9", "t9d"]
reg_alias_map["t9w"] = ["t9", "t9d", "t9w"]
reg_alias_map["t9b"] = ["t9", "t9d", "t9w", "t9b"]

reg_alias_map["t10"] = ["t10"]
reg_alias_map["t10d"] = ["t10", "t10d"]
reg_alias_map["t10w"] = ["t10", "t10d", "t10w"]
reg_alias_map["t10b"] = ["t10", "t10d", "t10w", "t10b"]

reg_alias_map["t11"] = ["t11"]
reg_alias_map["t11d"] = ["t11", "t11d"]
reg_alias_map["t11w"] = ["t11", "t11d", "t11w"]
reg_alias_map["t11b"] = ["t11", "t11d", "t11w", "t11b"]

reg_alias_map["t12"] = ["t12"] 
reg_alias_map["t12d"] = ["t12", "t12d"]
reg_alias_map["t12w"] = ["t12", "t12d", "t12w"]
reg_alias_map["t12b"] = ["t12", "t12d", "t12w", "t12b"]

reg_alias_map["t16"] = ["t16"] 
reg_alias_map["t16d"] = ["t16", "t16d"]
reg_alias_map["t16w"] = ["t16", "t16d", "t16w"]
reg_alias_map["t16b"] = ["t16", "t16d", "t16w", "t16b"]

reg_alias_map["t17"] = ["t17"] 
reg_alias_map["t17d"] = ["t17", "t17d"]
reg_alias_map["t17w"] = ["t17", "t17d", "t17w"]
reg_alias_map["t17b"] = ["t17", "t17d", "t17w", "t17b"]

reg_alias_map["t18"] = ["t18"] 
reg_alias_map["t18d"] = ["t18", "t18d"]
reg_alias_map["t18w"] = ["t18", "t18d", "t18w"]
reg_alias_map["t18b"] = ["t18", "t18d", "t18w", "t18b"]

reg_alias_map["t19"] = ["t19"] 
reg_alias_map["t19d"] = ["t19", "t19d"]
reg_alias_map["t19w"] = ["t19", "t19d", "t19w"]
reg_alias_map["t19b"] = ["t19", "t19d", "t19w", "t19b"]

reg_alias_map["t21"] = ["t21"] 
reg_alias_map["t21d"] = ["t21", "t21d"]
reg_alias_map["t21w"] = ["t21", "t21d", "t21w"]
reg_alias_map["t21b"] = ["t21", "t21d", "t21w", "t21b"]

reg_alias_map["xmm0"]         = ["xmm0"]
reg_alias_map["xmm0_high"]    = ["xmm0", "xmm0_high"]
reg_alias_map["xmm0_low"]     = ["xmm0", "xmm0_low"]

reg_alias_map["xmm1"]         = ["xmm1"]
reg_alias_map["xmm1_high"]    = ["xmm1", "xmm1_high"]
reg_alias_map["xmm1_low"]     = ["xmm1", "xmm1_low"]

reg_alias_map["xmm2"]         = ["xmm2"]
reg_alias_map["xmm2_high"]    = ["xmm2", "xmm2_high"]
reg_alias_map["xmm2_low"]     = ["xmm2", "xmm2_low"]

reg_alias_map["xmm3"]         = ["xmm3"]
reg_alias_map["xmm3_high"]    = ["xmm3", "xmm3_high"]
reg_alias_map["xmm3_low"]     = ["xmm3", "xmm3_low"]

reg_alias_map["xmm4"]         = ["xmm4"]
reg_alias_map["xmm4_high"]    = ["xmm4", "xmm4_high"]
reg_alias_map["xmm4_low"]     = ["xmm4", "xmm4_low"]

reg_alias_map["xmm5"]         = ["xmm5"]
reg_alias_map["xmm5_high"]    = ["xmm5", "xmm5_high"]
reg_alias_map["xmm5_low"]     = ["xmm5", "xmm5_low"]

reg_alias_map["xmm6"]         = ["xmm6"]
reg_alias_map["xmm6_high"]    = ["xmm6", "xmm6_high"]
reg_alias_map["xmm6_low"]     = ["xmm6", "xmm6_low"]

reg_alias_map["xmm7"]         = ["xmm7"]
reg_alias_map["xmm7_high"]    = ["xmm7", "xmm7_high"]
reg_alias_map["xmm7_low"]     = ["xmm7", "xmm7_low"]

reg_alias_map["xmm8"]         = ["xmm8"]
reg_alias_map["xmm8_high"]    = ["xmm8", "xmm8_high"]
reg_alias_map["xmm8_low"]     = ["xmm8", "xmm8_low"]

reg_alias_map["xmm9"]         = ["xmm9"]
reg_alias_map["xmm9_high"]    = ["xmm9", "xmm9_high"]
reg_alias_map["xmm9_low"]     = ["xmm9", "xmm9_low"]

reg_alias_map["xmm10"]         = ["xmm10"]
reg_alias_map["xmm10_high"]    = ["xmm10", "xmm10_high"]
reg_alias_map["xmm10_low"]     = ["xmm10", "xmm10_low"]

reg_alias_map["xmm11"]         = ["xmm11"]
reg_alias_map["xmm11_high"]    = ["xmm11", "xmm11_high"]
reg_alias_map["xmm11_low"]     = ["xmm11", "xmm11_low"]

reg_alias_map["xmm12"]         = ["xmm12"]
reg_alias_map["xmm12_high"]    = ["xmm12", "xmm12_high"]
reg_alias_map["xmm12_low"]     = ["xmm12", "xmm12_low"]

reg_alias_map["xmm13"]         = ["xmm13"]
reg_alias_map["xmm13_high"]    = ["xmm13", "xmm13_high"]
reg_alias_map["xmm13_low"]     = ["xmm13", "xmm13_low"]

reg_alias_map["xmm14"]         = ["xmm14"]
reg_alias_map["xmm14_high"]    = ["xmm14", "xmm14_high"]
reg_alias_map["xmm14_low"]     = ["xmm14", "xmm14_low"]

reg_alias_map["xmm15"]         = ["xmm15"]
reg_alias_map["xmm15_high"]    = ["xmm15", "xmm15_high"]
reg_alias_map["xmm15_low"]     = ["xmm15", "xmm15_low"]

reg_alias_map["ufp1"]         = ["ufp1"]
reg_alias_map["ufp2"]         = ["ufp2"]
reg_alias_map["bpl"]          = ["bpl"]
reg_alias_map["sil"]          = ["sil"]
reg_alias_map["sil"]          = ["cc0"]
reg_alias_map["sil"]          = ["cc1"]

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
control_ops = ["jo","jno","js","jns","je","jz","jne","jnz","jb","jnae","jc","jnb","jae","jnc","jbe","jna","ja","jnbe","jl","jnge","jge","jnl","jle","jng","jg","jnle","jp","jpe","jnp","jpo","jcxz","jecxz","set","cmov","call","callq","loop","ret","jmp","jmpq"]

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
instr_flag_affect_map["SF"] = ['add', 'sub', 'neg', 'adc', 'sbb', 'inc', 'dec', 'test', 'cmp', 'and', 'or', 'xor', 'maxsd', 'sqrt', 'limm']
instr_flag_affect_map["CF"] = ['add', 'sub', 'mul', 'div', 'neg', 'adc', 'sbb', 'inc', 'dec', 'and', 'or', 'xor', 'not', 'rotate', 'test', 'cmp', 'ucomisd', 'maxsd', 'sqrt']
instr_flag_affect_map["ZF"] = ['add', 'sub', 'mul', 'div', 'neg', 'adc', 'sbb', 'inc', 'dec', 'and', 'or', 'xor', 'not', 'rotate', 'test', 'cmp', 'ucomisd', 'maxsd','sqrt','limm']
instr_flag_affect_map["PF"] = ['all']    # all instructions except bad

# TODO: figure out - cvtsi2sd,  cvttsd2si, cvtdq2pd, pshufd