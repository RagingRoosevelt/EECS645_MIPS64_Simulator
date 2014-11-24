#!/usr/bin/env python
import re


#filename = raw_input("Filename? ")
filename = "test_jerzy2.txt"
file = open(filename, 'r')

I_registers = [0]*100
FP_registers = [0]*100
Memory = [0]*1000
Code = [[]]*1000

readIRegisters=0
readFPRegisters=0
readMemory=0
readCode = 0

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
            lineMatch = re.match("L\.D F([0-9]*), ([-0-9]*)\(R([0-9]*)\)",line
            Code[readCode] = ["L.D", lineMatch.group(1), lineMatch.group(2), lineMatch.group(3)]
        if line[:3]=="S.D":
            lineMatch = re.match("S\.D F([0-9]*), ([-0-9]*)\(R([0-9]*)\)",line
            Code[readCode] = ["S.D", lineMatch.group(1), lineMatch.group(2), lineMatch.group(3)]
        if line[:5] = "MUL.D":
            lineMatch = re.match("MUL\.D F([0-9]*), F([0-9]*), F([0-9]*)",line
            Code[readCode] = ["MUL.D", lineMatch.group(1), lineMatch.group(2), lineMatch.group(3)]
        if line[:5] = "ADD.D":
            lineMatch = re.match("ADD\.D F([0-9]*), F([0-9]*), F([0-9]*)",line
            Code[readCode] = ["ADD.D", lineMatch.group(1), lineMatch.group(2), lineMatch.group(3)]
        if line[:5] = "SUB.D":
            lineMatch = re.match("SUB\.D F([0-9]*), F([0-9]*), F([0-9]*)",line
            Code[readCode] = ["SUB.D", lineMatch.group(1), lineMatch.group(2), lineMatch.group(3)]
        if line[:5] = "DIV.D":
            lineMatch = re.match("DIV\.D F([0-9]*), F([0-9]*), F([0-9]*)",line
            Code[readCode] = ["DIV.D", lineMatch.group(1), lineMatch.group(2), lineMatch.group(3)]
            
        print(Code[readCode])
            
    elif readMemory==1:
        lineMatch = re.match("([0-9]*) (.*)",line)
        Memory[int(lineMatch.group(1))] = float(lineMatch.group(2))
        print("read: mem @ " + lineMatch.group(1) + " = " + lineMatch.group(2))
    elif readFPRegisters==1:
        lineMatch = re.match("F([0-9]*) (.*)",line)
        FP_registers[int(lineMatch.group(1))] = int(lineMatch.group(2))
        print("read: F" + lineMatch.group(1) + " = " + lineMatch.group(2))
    elif readIRegisters==1:
        lineMatch = re.match("R([0-9]*) (.*)",line)
        I_registers[int(lineMatch.group(1))] = int(lineMatch.group(2))
        print("read: R" + lineMatch.group(1) + " = " + lineMatch.group(2))