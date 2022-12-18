#!/usr/bin/python
#
#    a s s e m b l e r . p y
#
import sys, string
 
codes={"hlt":"0", "ld":"1", "sto":"2", "ld#":"3", "ldi":"4", "add":"5", "sub":"6", 
       "mul":"7", "div":"8", "jmp":"A", "jz":"B", "jsr":"C", "rts":"D"}
 
lookup={"r0":"0", "r1":"1", "r2":"2", "r3":"3", "r4":"4", "r5":"5", "r6":"6", "r7":"7",
        "r8":"8", "r9":"9", "rA":"A", "rB":"B", "rC":"C", "rD":"D", "rE":"E", "rF":"F"}
 
def getVal (s) :
    "return numeric value of a symbol or number"
    if not s : return 0       # Empty symbol - zero
    a = lookup.get(s)         # Get value or None if not in lookup
    if a == None : return s   # Just a number
    else         : return a

def getPReg (program) :
    for lin in program :
        flds = lin.split()
        if flds[0] == "org":
            pReg = flds[1]
            return pReg
            break
        else:
            pReg = "100"
            return pReg
            break

def pass1 (program, PReg) :
    "determine addresses for labels and add to the lookup dictionary"
    global lookup
    pReg = int(PReg, 16)
    for lin in program :
        flds = lin.split()
        if flds[0] == "end":
            break
        else:
            if not flds : continue                    # just an empty line
            if lin[0] > ' ' :
                symb = flds[0]                        # A symbol. Save its address in lookup
                lookup[symb] = str(hex(pReg))[2:]
                if len(flds) > 1 :                    # Advance program counter unless only a symbol
                    pReg = pReg + 1
            else : pReg = pReg + 1

def pass1_org (program, PReg) :
    "determine addresses for labels and add to the lookup dictionary"
    global lookup
    pReg = int(PReg, 16)
    for lin in program :
        flds = lin.split()
        if flds[0] == "end":
            break
        else:
            if not flds : continue                    # just an empty line
            if lin[0] > ' ' :
                symb = flds[0]                        # A symbol. Save its address in lookup
                lookup[symb] = str(hex(pReg-1))[2:]
                if len(flds) > 1 :                    # Advance program counter unless only a symbol
                    pReg = pReg + 1
            else : pReg = pReg + 1


def check(value):
    if len(value) == 1:
        return "0000" + value
    if len(value) == 2:
        return "000" + value
    if len(value) == 3:
        return "00" + value
    if len(value) == 4:
        return "0" + value
    if len(value) == 5:
        return value

def assemble (flds) :
    "assemble instruction to machine code"
    opval = codes.get(flds[0])
    if opval == None : return int(flds[0], 16)    # just a number
    if opval ==  "0" : return int("00000000", 16) # Halt. no address
    if opval ==  "D" : return int("0D000000", 16)
    parts  = flds[1].split(",")                   # see if reg,address
    if len(parts) == 1 : parts = ["0",parts[0]]   # No register means 0
    loc1 = getVal(parts[0])
    loc2 = getVal(parts[1])
    instruction = "0" + opval + loc1 + check(loc2)
    return int(instruction, 16)
 
def pass2 (program, PReg) :
    "translate assembly code and symbols to machine code"
    pReg = int(PReg, 16)
    for lin in program :
        flds = lin.split()
        if flds[0] == "end":
            break
        elif flds[0] == "org":
            continue
        elif flds[0] == "word":
            if lin[0] > ' ' : flds = flds[1:]
            num = [0]*0x4
            num[0] = (int(flds[1], 16) >> 24) & 0xFF
            num[1] = (int(flds[1], 16) >> 16) & 0xFF
            num[2] = (int(flds[1], 16) >> 8) & 0xFF
            num[3] = int(flds[1], 16) & 0xFF
            for i in range(0,4):
                print ("%05X %08X   %s" % (pReg, num[i], lin))
                pReg = pReg + 1
        elif flds[0] == "hword":
            if lin[0] > ' ' : flds = flds[1:]
            num = [0]*0x4
            num[0] = (int(flds[1], 16) >> 8) & 0xFF
            num[1] = int(flds[1], 16) & 0xFF
            for i in range(0,2):
                print ("%05X %08X   %s" % (pReg, num[i], lin))
                pReg = pReg + 1
        elif flds[0] == "byte":
            if lin[0] > ' ' : flds = flds[1:]
            num = int(flds[1], 16)
            print ("%05X %08X   %s" % (pReg, num, lin))
            pReg = pReg + 1
        elif flds[0] == "reserveb":
            for i in range(1,int(flds[1])+1):
                print ("%05X %08X   %s" % (pReg, 0, lin))
                pReg = pReg + 1
        elif flds[0] == "reservew":
            for i in range(1,(int(flds[1])*4)+1):
                print ("%05X %08X   %s" % (pReg, 0, lin))
                pReg = pReg + 1
        else:
            if lin[0] > ' ' : flds = flds[1:]           # drop symbol if there is one
            if not flds : print ("            ", lin)   # print now if only a symbol
            else :
                try :
                    instruction = assemble(flds)
                    print ("%05X %08X   %s" % (pReg, instruction, lin))
                    pReg = pReg + 1
                except :
                    print ("***** ********   %s" % lin)
 
def main () :
    program = sys.stdin.readlines()
    print(program)
    pReg = getPReg(program)
    if pReg == "100":
        pass1 (program, pReg)
    else:
        pass1_org(program, pReg)
    pass2 (program, pReg)
 
if __name__ == "__main__" : main ()
