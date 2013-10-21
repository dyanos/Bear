#!/usr/bin/env python
import os,sys,string

class IRStorage:
    def __init__(self):
        pass

    def __str__(self):
        return "IRStorage"
    
class IRRegister(IRStorage):
    R0 = 0 # return
    R1 = 1
    R2 = 2
    R3 = 3
    R4 = 4
    R5 = 5
    R6 = 6
    R7 = 7
    R8 = 8
    R9 = 9
    R10 = 10
    R11 = 11
    R12 = 12
    R13 = 13 # stack address
    R14 = 14
    R15 = 15 # return address
    
    def __init__(self, regid):
        self.id = regid

    def __str__(self):
        return self.toString()
    
    def toString(self):
        if self.id == IRRegister.R0:
            return "r0"
        elif self.id == IRRegister.R1:
            return "r1"
        elif self.id == IRRegister.R2:
            return "r2"
        elif self.id == IRRegister.R3:
            return "r3"
        elif self.id == IRRegister.R4:
            return "r4"
        elif self.id == IRRegister.R5:
            return "r5"
        elif self.id == IRRegister.R6:
            return "r6"
        elif self.id == IRRegister.R7:
            return "r7"
        elif self.id == IRRegister.R8:
            return "r8"
        elif self.id == IRRegister.R9:
            return "r9"
        elif self.id == IRRegister.R10:
            return "r10"
        elif self.id == IRRegister.R11:
            return "r11"
        elif self.id == IRRegister.R12:
            return "r12"
        elif self.id == IRRegister.R13:
            return "r13"
        elif self.id == IRRegister.R14:
            return "r14"
        elif self.id == IRRegister.R15:
            return "r15"

class IRImm(IRStorage):
    def __init__(self, value):
        if isinstance(value, int):
            raise TypeError()
        
        self.value = value

    def __str__(self):
        return self.toString()
    
    def toString(self):
        return "%d" % (self.value)

class IRMem(IRStorage):
    def __init__(self, base, index, imm):
        if isinstance(base, IRRegister):
            raise TypeError()
        elif index != None:
            if isinstance(index, IRRegister):
                raise TypeError()
        elif imm != None:
            if isinstance(imm, int):
                raise TypeError()

        self.base = base
        self.index = index
        self.imm = imm

    def __str__(self):
        return self.toString()

    def toString(self):
        if self.index == None and self.imm == 0:
            return "[%s]" % (self.base)
        elif self.index == None and self.imm != 0:
            return "[%s+(%s)]" % (self.base, self.imm)
        elif self.index != None and self.imm == 0:
            return "[%s+%s]" % (self.base, self.index)
        
        return "[%s+%s+(%s)]" % (self.base, self.index, self.imm)

# Basically, IR is based on 3-state machine (specially, ARM).
class IROp:
    def __init__(self):
        pass

    def __str__(self):
        return "IROp"
    
# move a, b
# meaning: a <- b
# a : register
# b : register or imm
class IROpMove(IROp):
    def __init__(self, srcReg, dstVal):
        if not isinstance(srcReg, IRRegister):
            raise TypeError()
        if not isinstance(dstVal, IRRegister) or not isinstance(dstVal, IRImm):
            raise TypeError()
        
        self.src = srcReg
        self.dst = dstVal

    def __str__(self):
        return self.toString()
    
    def toString(self):
        return "move %s, %s" % (self.src, self.dst)

# add a, b, c
# meaning : a + b = c
#    a = register, imm
#    b = register, imm
#    c = register
class IROpAdd(IROp):
    def __init__(self, srcReg, midReg, dstReg):
        if not isinstance(dstReg, IRRegister):
            raise TypeError()
        elif not isinstance(srcReg, IRRegister) or not isinstance(srcReg, IRImm):
            raise TypeError()
        elif not isinstance(midReg, IRRegister) or not isinstance(midReg, IRImm):
            raise TypeError()

        self.src = srcReg
        self.mid = midReg
        self.dst = dstReg

    def __str__(self):
        return self.toString()

    def toString(self):
        return "add %s, %s, %s" % (self.src, self.mid, self.dst)

class IROpPush(IROp):
    def __init__(self, reg):
        if not isinstance(reg, IRRegister) or not isinstance(reg, IRImm):
            raise TypeError()

        self.reg = reg
        
    def __str__(self):
        return self.toString()

    def toString(self):
        return "push %s" % (self.reg)

class IROpPop(IROp):
    def __init__(self, reg):
        if not isinstance(reg, IRRegister) or not isinstance(reg, IRImm):
            raise TypeError()

        self.reg = reg

    def __str__(self):
        return self.toString()

    def toString(self):
        return "pop %s" % (self.reg)

# load loc, dst
# meaing : [loc] -> dst
class IROpLoad(IROp):
    def __init__(self, loc, dst):
        if not isinstance(loc, IRStorage):
            raise TypeError()
        elif not isinstance(dst, IRRegister):
            raise TypeError()

        self.loc = loc
        self.dst = dst

    def __str__(self):
        return self.toString()

    def toString(self):
        return "load %s, %s" % (self.loc, self.dst)

# save src, loc
# meaing : src -> [loc]
class IROpLoad(IROp):
    def __init__(self, src, loc):
        if not isinstance(loc, IRStorage):
            raise TypeError()
        elif not isinstance(src, IRRegister):
            raise TypeError()

        self.loc = loc
        self.src = src

    def __str__(self):
        return self.toString()

    def toString(self):
        return "save %s, %s" % (self.src, self.loc)

    
