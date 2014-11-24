#!/usr/bin/env python

def ParseFile(filename):# [I_registers, FP_registers, Memory, Code]
    import re
    
    I_registers = []*100
    FP_registers = [0]*100
    Memory = [0]*1000
    Code = [None]*1000

    readIRegisters=0
    readFPRegisters=0
    readMemory=0
    readCode = 0
    
    file = open(filename, 'r')
    
    for line in file:
        #print(line)
        if 'CODE' in line:
            readCode=1
            readMemory=0
            print("reading CODE")
        elif 'MEMORY' in line:
            readMemory=1
            readFPRegisters=0
            print("reading MEMORY")
        elif 'FP-REGISTERS' in line:
            readFPRegisters=1
            readIRegisters=0
            print("reading FP-REGISTERS")
        elif 'I-REGISTERS' in line:
            readIRegisters=1
            print("reading I-REGISTERS")
        elif readCode>0:
            if line[:3]=="L.D":
                lineMatch = re.match("[ 	]*L\.D[ 	]+F([0-9]*),[ 	]+([-0-9]*)\(R([0-9]*)\)",line)
                Code[readCode] = ["L.D", lineMatch.group(1), lineMatch.group(2), lineMatch.group(3)]
                readCode += 1
            if line[:3]=="S.D":
                lineMatch = re.match("[ 	]*S\.D[ 	]+([-0-9]*)\(R([0-9]*)\),[ 	]+F([0-9]*)",line)
                Code[readCode] = ["S.D", lineMatch.group(1), lineMatch.group(2), lineMatch.group(3)]
                readCode += 1
            if line[:5] == "MUL.D":
                lineMatch = re.match("[ 	]*MUL\.D[ 	]+F([0-9]*),[ 	]+F([0-9]*),[ 	]+F([0-9]*)",line)
                Code[readCode] = ["MUL.D", lineMatch.group(1), lineMatch.group(2), lineMatch.group(3)]
                readCode += 1
            if line[:5] == "ADD.D":
                lineMatch = re.match("[ 	]*ADD\.D[ 	]+F([0-9]*),[ 	]+F([0-9]*),[ 	]+F([0-9]*)",line)
                Code[readCode] = ["ADD.D", lineMatch.group(1), lineMatch.group(2), lineMatch.group(3)]
                readCode += 1
            if line[:5] == "SUB.D":
                lineMatch = re.match("[ 	]*SUB\.D[ 	]+F([0-9]*),[ 	]+F([0-9]*),[ 	]+F([0-9]*)",line)
                Code[readCode] = ["SUB.D", lineMatch.group(1), lineMatch.group(2), lineMatch.group(3)]
                readCode += 1
            if line[:5] == "DIV.D":
                lineMatch = re.match("[ 	]*DIV\.D[ 	]+F([0-9]*),[ 	]+F([0-9]*),[ 	]+F([0-9]*)",line)
                Code[readCode] = ["DIV.D", lineMatch.group(1), lineMatch.group(2), lineMatch.group(3)]
                readCode += 1
            #print(Code[readCode-1])
                
        elif readMemory==1:
            lineMatch = re.match("([0-9]*) (.*)",line)
            try:
                Memory[int(lineMatch.group(1))] = float(lineMatch.group(2))
                print("read: mem @ " + lineMatch.group(1) + " = " + lineMatch.group(2))
            except:
                print("Blank Line")
        elif readFPRegisters==1:
            lineMatch = re.match("F([0-9]*) (.*)",line)
            try:
                FP_registers[int(lineMatch.group(1))] = int(lineMatch.group(2))
                print("read: F" + lineMatch.group(1) + " = " + lineMatch.group(2))
            except:
                print("Blank Line")
        elif readIRegisters==1:
            lineMatch = re.match("R([0-9]*) (.*)",line)
            try:
                I_registers[int(lineMatch.group(1))] = int(lineMatch.group(2))
                print("read: R" + lineMatch.group(1) + " = " + lineMatch.group(2))
            except:
                print("Blank Line")
                
    Code = [x for x in Code if x is not None]
    return [I_registers, FP_registers, Memory, Code]
    
    file.close()
    

    



#filename = raw_input("Filename? ")
filename = "test_jerzy2.txt"

[I_registers, FP_registers, Memory, Code] = ParseFile(filename)
I_inUse = [False]*len(I_registers)
FP_inUse = [False]*len(FP_registers)

print(Code)

#def Pipeline([I_registers, FP_registers, Memory, readCode]):

for instruction in Code:
