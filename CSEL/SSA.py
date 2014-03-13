#!/usr/bin/env pythone
# -*- coding: utf-8 -*-
from Intel import *
from SymbolTable import *

class Type:
    Read = 1
    Write = 2
    
class SSA:
    def __init__(self, symtbl, operandList):
        self.symtbl = symtbl
        self.operandList = operandList
        
    def converting(self):
        oldOperandList = self.operandList
        newOperandList = []
        
        version = {}
        def changeName(reg, type):
            if not isinstance(reg, IReg) and not isinstance(reg, IUserReg):
                return reg
            
            regname = str(reg)
            
            if not version.has_key(regname):
                version[regname] = 0
            else:
                if type == Type.Write:
                    version[regname] += 1
                
            nextname = "%s%d" % (regname, version[regname])
            
            return IUserReg(nextname)
    
        for operand in oldOperandList:
            if isinstance(operand, OpMove):
                src = changeName(operand.src, type = Type.Read)
                dst = changeName(operand.dst, type = Type.Write)
                newOperandList.append(OpMove(src, dst))
            elif isinstance(operand, OpAdd):
                src = changeName(operand.src, type = Type.Read)
                dst = changeName(operand.dst, type = Type.Write)
                newOperandList.append(OpAdd(src, dst))
            elif isinstance(operand, OpSub):
                src = changeName(operand.src, type = Type.Read)
                dst = changeName(operand.dst, type = Type.Write)
                newOperandList.append(OpSub(src, dst))
            elif isinstance(operand, OpMul):
                src = changeName(operand.src, type = Type.Read)
                dst = changeName(operand.dst, type = Type.Write)
                newOperandList.append(OpMul(src, dst))
            elif isinstance(operand, OpDiv):
                src = changeName(operand.src, type = Type.Read)
                dst = changeName(operand.dst, type = Type.Write)
                newOperandList.append(OpDiv(src, dst))
            elif isinstance(operand, OpPush):
                target = changeName(operand.target, type = Type.Read)
                newOperandList.append(OpPush(target))
            elif isinstance(operand, OpPop):
                target = changeName(operand.target, type = Type.Write)
                newOperandList.append(OpPush(target))
            elif isinstance(operand, OpJumpToReg):
                reg = changeName(operand.reg, type = Type.Read)
                newOperandList.append(OpJumpToReg(reg))
            elif isinstance(operand, OpComp):
                target1 = changeName(operand.target1, type = Type.Read)
                target2 = changeName(operand.target2, type = Type.Read)
                newOperandList.append(OpComp(target1, target2))
                
                
                