#!/usr/bin/env python

# Parse input file and store info in corresponding arrays ####################################################
def ParseFile(filename):# [I_registers, FP_registers, Memory, Code]
    import re
    
    I_registers = [[0,False] for x in range(32)]
    FP_registers = [[0,False] for x in range(32)]
    Memory = [[0,False] for x in range(993)]
    Code = [None]*1000

    readIRegisters=0
    readFPRegisters=0
    readMemory=0
    readCode = 0
    
    file = open(filename, 'r')
    
    for line in file:
        line = line.strip("\t")
        line = line.lstrip()
        if 'CODE' in line:
            readCode=1
            readMemory=0
            print("reading CODE")
            continue
        elif 'MEMORY' in line:
            readMemory=1
            readFPRegisters=0
            print("reading MEMORY")
            continue
        elif 'FP-REGISTERS' in line:
            readFPRegisters=1
            readIRegisters=0
            print("reading FP-REGISTERS")
            continue
        elif 'I-REGISTERS' in line:
            readIRegisters=1
            print("reading I-REGISTERS")
            continue
        elif readCode>0:
            if line[:3]=="L.D":
                lineMatch = re.match("\s*L\.D\s+F([0-9]*),\s+([-0-9]*)\(R([0-9]*)\)",line)
                Code[readCode] = [["L.D", -1], [lineMatch.group(1), -1], [lineMatch.group(2), -1], [lineMatch.group(3), -1]]
                readCode += 1
                continue
            if line[:3]=="S.D":
                lineMatch = re.match("\s*S\.D\s+([-0-9]*)\(R([0-9]*)\),\s+F([0-9]*)",line)
                Code[readCode] = [["S.D", -1], [lineMatch.group(1), -1], [lineMatch.group(2), -1], [lineMatch.group(3), -1]]
                readCode += 1
                continue
            if line[:5] == "MUL.D":
                lineMatch = re.match("\s*MUL\.D\s+F([0-9]*),\s+F([0-9]*),\s+F([0-9]*)",line)
                Code[readCode] = [["MUL.D", -1], [lineMatch.group(1), -1], [lineMatch.group(2), -1], [lineMatch.group(3), -1]]
                readCode += 1
                continue
            if line[:5] == "ADD.D":
                lineMatch = re.match("\s*ADD\.D\s+F([0-9]*),\s+F([0-9]*),\s+F([0-9]*)",line)
                Code[readCode] = [["ADD.D", -1], [lineMatch.group(1), -1], [lineMatch.group(2), -1], [lineMatch.group(3), -1]]
                readCode += 1
                continue
            if line[:5] == "SUB.D":
                lineMatch = re.match("\s*SUB\.D\s+F([0-9]*),\s+F([0-9]*),\s+F([0-9]*)",line)
                Code[readCode] = [["SUB.D", -1], [lineMatch.group(1), -1], [lineMatch.group(2), -1], [lineMatch.group(3), -1]]
                readCode += 1
                continue
            if line[:5] == "DIV.D":
                lineMatch = re.match("\s*DIV\.D\s+F([0-9]*),\s+F([0-9]*),\s+F([0-9]*)",line)
                Code[readCode] = [["DIV.D", -1], [lineMatch.group(1), -1], [lineMatch.group(2), -1], [lineMatch.group(3), -1]]
                readCode += 1
                continue
            #print(Code[readCode-1])
                
        elif readMemory==1:
            lineMatch = re.match("\s*([0-9]*)\s+(.*)",line)
            try:
                Memory[int(lineMatch.group(1))][0] = float(lineMatch.group(2))
                print("read: mem @ location " + lineMatch.group(1) + "\t= " + lineMatch.group(2))
            except:
                pass
        elif readFPRegisters==1:
            lineMatch = re.match("\s*F([0-9]+)\s+([0-9]+.?[0-9]*)s*",line)
            try:
                FP_registers[int(lineMatch.group(1))][0] = float(lineMatch.group(2))
                print("read: F" + lineMatch.group(1) + " = " + lineMatch.group(2))
            except:
                pass
        elif readIRegisters==1:
            lineMatch = re.match("\s*R([0-9]*)\s+(.*)",line)
            try:
                I_registers[int(lineMatch.group(1))][0] = int(lineMatch.group(2))
                print("read: R" + lineMatch.group(1) + " = " + lineMatch.group(2))
            except:
                pass
                
    Code = [x for x in Code if x is not None]
    
    CodePrinter(Code)
    
    return [I_registers, FP_registers, Memory, Code]
    
    file.close()


# Detect and note all Write Hazards ##########################################################################
def WriteHazardDetect(Code, instruction):
    instruction -= 1
    print("(I" + str(instruction+1) +")  " + "For instruction " + Code[instruction][0][0] + ", we have the following write hazards")
    for previous in range(0,instruction):
        if (Code[instruction][0][0] != "S.D") and (Code[previous][0][0] != "S.D"):
            if Code[instruction][1][0] == Code[previous][1][0]:
                Code[instruction][1][1] = previous
                print("\t\tCurrent instruction output: F" + str(Code[instruction][1][0]))
                print("\t\tPrevious instruction output: F" + str(Code[previous][1][0]))
        if (Code[instruction][0][0] == "S.D") and (Code[previous][0][0] == "S.D"):
            if (Code[instruction][1][0] == Code[previous][1][0]) and (Code[instruction][2][0] == Code[previous][2][0]):
                Code[instruction][1][1] = previous
                print("\t\tCurrent instruction output: " + str(Code[instruction][1][0]) + "(R" + str(Code[instruction][2][0]) + ")")
                print("\t\tPrevious instruction output: " + str(Code[previous][1][0]) + "(R" + str(Code[previous][2][0]) + ")")
    
    # Report where the hazard was found
    if Code[instruction][1][1] == -1:
        print("\t\tNone")
    else:
        print("\tHazard from " + Code[Code[instruction][1][1]][0][0] + " (I" + str(Code[instruction][1][1]+1) + ")")
        
    return Code


# Detect and note all Read Hazards ###########################################################################
def ReadHazardDetect(Code, instruction):
    instruction -= 1
    print("(I" + str(instruction+1) +")  " + "For instruction " + Code[instruction][0][0] + ", we have the following read hazards")
    for previous in range(0,instruction):
        if ((Code[instruction][0][0] == "MUL.D") or (Code[instruction][0][0] == "ADD.D") or (Code[instruction][0][0] == "SUB.D")) and (Code[previous][0][0] != "S.D"):
            if (Code[instruction][2][0] == Code[previous][1][0]):
                print("\t\tCurrent instruction input #1: F" + str(Code[instruction][2][0]))
                print("\t\tPrevious instruction output: F" + str(Code[previous][1][0]))
                Code[instruction][2][1] = previous
            if (Code[instruction][3][0] == Code[previous][1][0]):
                print("\t\tCurrent instruction input #2: F" + str(Code[instruction][3][0]))
                print("\t\tPrevious instruction output: F" + str(Code[previous][1][0]))
                Code[instruction][3][1] = previous
        if (Code[instruction][0][0] == "L.D") and (Code[previous][0][0] == "S.D"):
            #                                            instruction name                 offset                             I-register                           FP-register
            #print("\t(" + str(previous+1) + ")  " + Code[previous][0][0] + " " + str(Code[previous][1][0]) + "(R" + str(Code[previous][2][0]) + "), F" + str(Code[previous][3][0]))
            #        offset                     offset                     I-Register                 I-Register                                     
            if (Code[instruction][2][0] == Code[previous][1][0]) and (Code[instruction][3][0] == Code[previous][2][0]):
                print("\t\tCurrent instruction input: " + str(Code[instruction][2][0]) + "(" + str(Code[instruction][3][0]) + ")")
                print("\t\tPrevious instruction output: " + str(Code[previous][1][0]) + "(" + str(Code[previous][2][0]) + ")")
                Code[instruction][2][1] = previous
                Code[instruction][3][1] = previous
        if (Code[instruction][0][0] == "S.D"):
            if (Code[instruction][3][0] == Code[previous][1][0]) and (Code[previous][0][0] != "S.D"):
                print("\t\tCurrent instruction input: F" + str(Code[instruction][3][0]))
                print("\t\tPrevious instruction output: F" + str(Code[previous][1][0]))
                Code[instruction][3][1] = previous
    
    # Report where the hazard was found
    if (Code[instruction][2][1] == -1) and (Code[instruction][3][1] == -1):
        print("\t\tNone")
    elif (Code[instruction][2][1] == -1) and (Code[instruction][3][1] != -1):
        print("\tHazard from " + Code[Code[instruction][3][1]][0][0] + " (I" + str(Code[instruction][3][1]+1) + ")")    
    elif (Code[instruction][2][1] != -1) and (Code[instruction][3][1] == -1):
        print("\tHazard from " + Code[Code[instruction][2][1]][0][0] + " (I" + str(Code[instruction][2][1]+1) + ")")   
    elif (Code[instruction][2][1] != -1) and (Code[instruction][3][1] != -1):
        print("\tHazard from " + Code[Code[instruction][2][1]][0][0] + " (I" + str(Code[instruction][2][1]+1) + ") and " + Code[Code[instruction][3][1]][0][0] + " (I" + str(Code[instruction][3][1]+1) + ")")    
    return Code


# Simulate pipeline and write timing and register to file ####################################################
def Pipeline(Code, I_registers, FP_registers, Memory, filename):
    INTstages = ["IF", "ID", "EXE", "MEM", "WB"]
    A_Sstages = ["IF", "ID", "A1", "A2", "A3", "A4", "MEM", "WB"]
    MULstages = ["IF", "ID", "M1", "M2", "M3", "M4", "M5", "M6", "M7", "MEM", "WB"]
    
    CodeStages = [""]*len(Code)
    ActualStage = [""]*len(Code)
    
    file = open(filename,'w')
        
    output=""
    for i in range(1,len(Code)+1):
        output += "\t\tI#" + str(i)
    output += "\n"
    file.writelines([output])
    
    

    current_instruction = 1
    clock_cycle = 0
    Code[0][0][1] = -1
    while Code[7][0][1] != -2:#Code[len(Code)-1][0][1] != -2:
        
        OldCode = Code
        
        # Write the current clock cycle to first column
        if clock_cycle+1<10:
            output = "c#" + str(clock_cycle+1) + " \t"
        else:
            output = "c#" + str(clock_cycle+1) + "\t"
        
        
        if Code[0][0][1] != -2:
            if Code[0][0][0] == "L.D" or Code[0][0][0] == "S.D":
                Code[0][0][1] += 1 
                output += "\t" + INTstages[Code[0][0][1]]
                ActualStage[0] = INTstages[Code[0][0][1]]
                try:
                    CodeStages[0] = INTstages[Code[0][0][1]+2]
                except:
                    CodeStages[0] = "WB"
                if Code[0][0][1] == len(INTstages)-1:
                    Code[0][0][1] = -2
                    
            elif Code[0][0][0] == "ADD.D" or Code[0][0][0] == "SUB.D":
                Code[0][0][1] += 1 
                output += "\t" + A_Sstages[Code[0][0][1]]
                ActualStage[0] = A_Sstages[Code[0][0][1]]
                try:
                    CodeStages[0] = A_Sstages[Code[0][0][1]+2]
                    #print(CodeStages[0])
                except:
                    CodeStages[0] = "WB"
                if Code[0][0][1] == len(A_Sstages)-1:
                    Code[0][0][1] = -2
                    
            elif Code[0][0][0] == "MUL.D" or Code[0][0][0] == "DIV.D":
                Code[0][0][1] += 1 
                output += "\t" + MULstages[Code[0][0][1]]
                ActualStage[0] = MULstages[Code[0][0][1]]
                try:
                    CodeStages[0] = MULstages[Code[0][0][1]+2]
                except:
                    CodeStages[0] = "WB"
                if Code[0][0][1] == len(MULstages)-1:
                    Code[0][0][1] = -2
                    
        else:
            output += "\t"
                
        for instruction in range(1,len(Code)):
            # check if current instruction has already finished
            if (Code[instruction][0][1] != -2):
            
                next_instruction = 0
                for other in range(0,instruction):
#                    print("cc: " + str(clock_cycle) + "(" + str(instruction+1) + ")" + "   " + ActualStage[instruction] + " and " + ActualStage[other])
                    if (ActualStage[other] == "WB") and (ActualStage[instruction] == "WB"):
                        output += "\t\ts"
                        next_instruction = 1
#                        print("cc:" + string(clock_cycle) + "   error")
                if next_instruction == 1:
                    continue
            
                
                # Check which instruction class is issued                
                if Code[instruction][0][0] == "L.D" or Code[instruction][0][0] == "S.D":
                    # check if previous instruction has been issued yet
                    if (Code[instruction-1][0][1] > 0) or (Code[instruction-1][0][1] == -2):
                        # After previous instruction has forwarded...
                        if (Code[instruction][0][1] >= 0) and ((CodeStages[Code[instruction][2][1]] == "WB")+(Code[instruction][2][1] == -1)) and ((CodeStages[Code[instruction][3][1]] == "WB")+(Code[instruction][3][1] == -1)):
                            Code[instruction][0][1] += 1
                            output += "\t\t" + INTstages[Code[instruction][0][1]]
                            ActualStage[instruction] = INTstages[Code[instruction][0][1]]
                            try:
                                CodeStages[instruction] = INTstages[Code[instruction][0][1]+2]
                            except:
                                CodeStages[instruction] = "WB"

                                
                        # just issues and previous hasn't written yet?
                        if (Code[instruction][0][1] == -1):# and (CodeStages[Code[instruction][2][1]] != "WB") and (CodeStages[Code[instruction][3][1]] != "WB"):
                            Code[instruction][0][1] = 0
                            output += "\t\t" + INTstages[Code[instruction][0][1]]
                            ActualStage[instruction] = INTstages[Code[instruction][0][1]]
                        # issued and previous hasn't written yet?
                        elif (Code[instruction][0][1] == 0):# and ((CodeStages[Code[instruction][2][1]] != "WB") or (Code[instruction][2][1] == -1)) and ((CodeStages[Code[instruction][3][1]] != "WB") or (Code[instruction][3][1] == -1)):
                            output += "\t\ts"
                    
                    # if previous instruction hasn't been issued yet, output whitespace
                    else:
                        output += "\t\t"
                        
                    # Check if current instruction has finished executing
                    if (Code[instruction][0][1] == len(INTstages)-1):
                        Code[instruction][0][1] = -2
                        
                        
                # Check which instruction class is issued                
                if Code[instruction][0][0] == "MUL.D" or Code[instruction][0][0] == "DIV.D":
                    # check if previous instruction has been issued yet
                    if (Code[instruction-1][0][1] > 0) or (Code[instruction-1][0][1] == -2):
                        # After previous instruction has forwarded...
                        if (Code[instruction][0][1] >= 0) and ((CodeStages[Code[instruction][2][1]] == "WB")+(Code[instruction][2][1] == -1)) and ((CodeStages[Code[instruction][3][1]] == "WB")+(Code[instruction][3][1] == -1)):
                            Code[instruction][0][1] += 1
                            output += "\t\t" + MULstages[Code[instruction][0][1]]
                            ActualStage[instruction] = MULstages[Code[instruction][0][1]]
                            try:
                                CodeStages[instruction] = MULstages[Code[instruction][0][1]+2]
                            except:
                                CodeStages[instruction] = "WB"
                        
                        #print("cc " + str(clock_cycle) + ":    (" + str(instruction+1) + ")   " + str(Code[instruction][0][1]) + " dependent on " + str(CodeStages[Code[instruction][2][1]]) + ", " + str(CodeStages[Code[instruction][3][1]]))
                        # just issues and previous hasn't written yet?
                        if (Code[instruction][0][1] == -1):# and (CodeStages[Code[instruction][2][1]] != "WB") and (CodeStages[Code[instruction][3][1]] != "WB"):
                            Code[instruction][0][1] = 0
                            output += "\t\t" + MULstages[Code[instruction][0][1]]
                            ActualStage[instruction] = MULstages[Code[instruction][0][1]]
                        # issued and previous hasn't written yet?
                        elif (Code[instruction][0][1] == 0):# and ((CodeStages[Code[instruction][2][1]] != "WB") or (Code[instruction][2][1] == -1)) and ((CodeStages[Code[instruction][3][1]] != "WB") or (Code[instruction][3][1] == -1)):
                            output += "\t\ts"
                    
                    # if previous instruction hasn't been issued yet, output whitespace
                    else:
                        output += "\t\t"
                        
                    # Check if current instruction has finished executing
                    if (Code[instruction][0][1] == len(MULstages)-1):
                        Code[instruction][0][1] = -2
                        
                        
                # Check which instruction class is issued                
                if Code[instruction][0][0] == "SUB.D" or Code[instruction][0][0] == "ADD.D":
                    # check if previous instruction has been issued yet
                    if (Code[instruction-1][0][1] > 0) or (Code[instruction-1][0][1] == -2):
                        # After previous instruction has forwarded...
                        if (Code[instruction][0][1] >= 0) and ((CodeStages[Code[instruction][2][1]] == "WB")+(Code[instruction][2][1] == -1)) and ((CodeStages[Code[instruction][3][1]] == "WB")+(Code[instruction][3][1] == -1)):
                            Code[instruction][0][1] += 1
                            output += "\t\t" + A_Sstages[Code[instruction][0][1]]
                            ActualStage[instruction] = A_Sstages[Code[instruction][0][1]]
                            try:
                                CodeStages[instruction] = A_Sstages[Code[instruction][0][1]+2]
                            except:
                                CodeStages[instruction] = "WB"
                        
                        #print("cc " + str(clock_cycle) + ":    (" + str(instruction+1) + ")   " + str(Code[instruction][0][1]) + " dependent on " + str(CodeStages[Code[instruction][2][1]]) + ", " + str(CodeStages[Code[instruction][3][1]]))
                        # just issues and previous hasn't written yet?
                        if (Code[instruction][0][1] == -1):# and (CodeStages[Code[instruction][2][1]] != "WB") and (CodeStages[Code[instruction][3][1]] != "WB"):
                            Code[instruction][0][1] = 0
                            output += "\t\t" + A_Sstages[Code[instruction][0][1]]
                            ActualStage[instruction] = A_Sstages[Code[instruction][0][1]]
                        # issued and previous hasn't written yet?
                        elif (Code[instruction][0][1] == 0):# and ((CodeStages[Code[instruction][2][1]] != "WB") or (Code[instruction][2][1] == -1)) and ((CodeStages[Code[instruction][3][1]] != "WB") or (Code[instruction][3][1] == -1)):
                            output += "\t\ts"
                    
                    # if previous instruction hasn't been issued yet, output whitespace
                    else:
                        output += "\t\t"
                        
                    # Check if current instruction has finished executing
                    if (Code[instruction][0][1] == len(A_Sstages)-1):
                        Code[instruction][0][1] = -2
            
            
            # write blank space if instruction has already completed
            else:
                output += "\t\t"
                
            
            
        file.writelines([output + "\n"])
        
        
        clock_cycle += 1
        
        
    file.close()
    return FP_registers


# Print code line-by-line ####################################################################################
def CodePrinter(Code):
    for i in range(0,len(Code)):
        print("(" + str(i+1) + "):  " + str(Code[i]))


def Compute(Code, I_registers, FP_registers, Memory):
    for instruction in range(0,len(Code)):
        arg1 = int(Code[instruction][1][0])
        arg2 = int(Code[instruction][2][0])
        arg3 = int(Code[instruction][3][0])
        if Code[instruction][0][0] == "L.D":
            FP_registers[arg1][0] = float(Memory[arg2 + int(I_registers[arg3][0])][0])
        if Code[instruction][0][0] == "S.D":
#            print(str(arg1 + I_registers[arg2][0]))
#            print(arg3)
            Memory[arg1 + I_registers[arg2][0]][0] = float(FP_registers[arg3][0])
        if Code[instruction][0][0] == "ADD.D":
            FP_registers[arg1][0] = float(FP_registers[arg2][0]) + float(FP_registers[arg3][0])
        if Code[instruction][0][0] == "SUB.D":
            FP_registers[arg1][0] = float(FP_registers[arg2][0]) - float(FP_registers[arg3][0])
        if Code[instruction][0][0] == "MUL.D":
            FP_registers[arg1][0] = float(FP_registers[arg2][0]) * float(FP_registers[arg3][0])
            
    return [I_registers, FP_registers, Memory]

# Runner function (gets file names and calls necessary functions) ############################################
def Runner():
    # Get input filename
    try:
        filename = raw_input("Input (instruction, registers, and memory) filename? ")
    except:
        filename = input("Input (instruction, registers, and memory) filename? ")
#    filename = "test_xms2.txt"

    
    # Parse file for registers, memory, instructions
    print("\n")
    [I_registers, FP_registers, Memory, Code] = ParseFile(filename)
    
    
    print("\n")
    # Note all Read Hazards
    for instruction in range(1, len(Code)+1):
        Code = ReadHazardDetect(Code, instruction)
        
    
    print("\n")
    # Note all Write Hazards
    for instruction in range(1, len(Code)+1):
        Code = WriteHazardDetect(Code, instruction)
    
    print("\nCode (with hazards noted):")
    CodePrinter(Code)

    # Get timing output filename
    try:
        filename = raw_input("Timing output filename? ")
    except: 
        filename = input("Timing output filename? ")
#    filename = "test_xms2_timing_output.txt"

    # Determine timings
    FP_registers = Pipeline(Code, I_registers, FP_registers, Memory, filename)
    
    file = open(filename,"r")
    for line in file:
        print(line)
    file.close()

    
    # Get register output filename
    try:
        filename = raw_input("Register content output filename? ")
    except:
        filename = input("Register content output filename? ")
#    filename = "test_xms2_FPregister_output.txt"
    # Determine FP register contents
    [I_registers, FP_registers, Memory] = Compute(Code, I_registers, FP_registers, Memory)
    file = open(filename,'w')
    # Output FP register header
    header = ""
    for register in range(0,len(FP_registers)):
        header += "F" + str(register) + "\t\t\t"
    file.write(header + "\n")
    # Output FP register contents
    values = ""
    for register in range(0,len(FP_registers)):
        if len(str(FP_registers[register][0])) >= 16:
            values += str(FP_registers[register][0]) + "\t"
        elif len(str(FP_registers[register][0])) >= 8:
            values += str(FP_registers[register][0]) + "\t\t"
        else :
            values += str(FP_registers[register][0]) + "\t\t\t"
    
    file.write(values + "\n")
         
    header = header.split("\t")
    values = values.split("\t")
    header = [x for x in header if x]
    values = [x for x in values if x]
    for i in range(0,len(values)):
        print(header[i] + " = " + str(values[i]))
    file.close()
    
    
Runner()




