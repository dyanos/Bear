# -*- coding: utf-8 -*-
#!/usr/bin/env python
import os,sys,string
from ASTType import *
from SymbolTable import *
from mangle import *
from context import *
from Operand import *
import Intel

Seperator = '$'

# value는 그냥 값을 가지고 있으면 되공,
# data는 data section의 위치를 가지고 있으면 되공...
class Value:
    def __init__(self, **kargs):
        for key, value in kargs.iteritems():
            setattr(self, key, value)

# 3-state machine code
class Context: 
    def __init__(self):
        self.context = []

        self.machine = Intel
        self.sizeOfMachineRegister = 8 # bytes
        self.reservedStackSize = 0

        # 이건 머징??
        self.undef = {}

        self.arguments = {}
        self.narguments = 8

    def checkTemporaryReg(self, regList, loc):
        for elem in regList:
            if self.machine.isTemporaryRegister(elem) == True:
                self.registerLoc(elem.name, loc)

    def setArgVar(self, name):
        self.arguments[name] = IMem(base=IReg('rbp'), imm=self.narguments)
        self.narguments += 8

        return self.arguments[name]
    
    def convertArgumentToReg(self, pos):
        # argument로 사용되는 register들 
        argreg = [IReg('rcx'), IReg('rdx'), IReg('r8'), IReg('r9')]
        if pos < len(argreg):
            return argreg[pos]
        
        return None

    def registerLoc(self, name, loc):
        if not self.undef.has_key(name):
            self.undef[name] = [loc]
        else:
            self.undef[name].append(loc)

    def increaseReservedStackSize(self):
        self.reservedStackSize += self.sizeOfMachineRegister

    # 일단 늘어나면 안 줄어들텐데...
    def decreaseReservedStackSize(self):
        self.reservedStackSize -= self.sizeOfMachineRegister

    def convertReg(self, name):
        if self.arguments.has_key(str(name)):
            return self.arguments[str(name)]
        return name

    def emitMove(self, src, dst):
        src = self.convertReg(src)
        dst = self.convertReg(dst)
        operand = self.machine.OpMove(src, dst)
        self.context.append(operand)
        self.checkTemporaryReg(regList = [src, dst], loc = len(self.context))

        print "mov %s, %s" % (dst, src)

    def emitAdd(self, srcA, srcB, dst):
        srcA = self.convertReg(srcA)
        srcB = self.convertReg(srcB)
        dst = self.convertReg(dst)

        context = self.context
        if self.machine == Intel:
            tmpReg = genTempRegister()
            self.emitMove(srcA, tmpReg)
            context.append(self.machine.OpAdd(srcB, tmpReg))
            print "add %s, %s" % (tmpReg, srcB)
            self.emitMove(tmpReg, dst)
        else:
            print "add %s, %s, %s" % (dst, srcB, srcA)

    def emitPush(self, target):
        target = self.convertReg(target)
        operand = self.machine.OpPush(target)
        self.context.append(operand)

        print "push %s" % (target)

    def emitPop(self, target):
        target = self.convertReg(target)
        operand = self.machine.OpPop(target)
        self.context.append(operand)

        print "pop %s" % (target)

    def emitCall(self, target, args, ret = False):
        parameterList = [IReg('rcx'), IReg('rdx'), IReg('r8'), IReg('r9')]
        pushedRegisters = []
        for regnum in range(0, len(args)):
            if len(args) >= len(parameterList):
                # stack을
                self.emitMove(args[regnum], IMem(IReg('rbp'), None, None))
            else:
                self.emitPush(parameterList[regnum])
                pushedRegisters.append(parameterList[regnum])
                self.emitMove(args[regnum], parameterList[regnum])

        # return 변수가 있을 경우, 일단 있다고 가정...
        #self.context.append(self.machine.OpPush(IReg('rax')))
        #self.context.append(self.machine.OpMove(IImm(0), IReg('rax')))
        operand = self.machine.OpCall(target, len(args), ret = ret)
        self.context.append(operand)

        print "call %s" % (target)

        for reg in reversed(pushedRegisters):
            self.emitPop(reg)

    def emitComp(self, target1, target2):
        target1 = self.convertReg(target1)
        target2 = self.convertReg(target2)
        operand = self.machine.OpComp(target1, target2)
        self.context.append(operand)
        print "cmp %s, %s" % (target1, target2)

    def emitJump(self, label):
        operand = self.machine.OpJump(label)
        self.context.append(operand)
        print "jmp %s" % (label)

    def emitJumpZeroFlag(self, label):
        operand = self.machine.OpJumpZeroFlag(label)
        self.context.append(operand)
        print "jz %s" % (label)

    def emitJumpUsingReg(self, reg):
        reg = self.convertReg(reg)
        operand = self.machine.OpJumpToReg(reg)
        self.context.append(operand)
        print "jmp %s" % (reg)

    def emitLabel(self, labelname):
        self.context.append(self.machine.MarkLabel(labelname))
        print "%s:" % (labelname)

    def calStackSize(self):
        pass

    def getRegisterAllocation(self, args):
        self.machine.allocateRegister(self.context, args)

    # register 재배치 알고리즘을 돌린 결과
    def reallocRegisters(self):
        pass

# Symbol Table은 Java의 Symbol Table의 모습을 따른다.
#
# long name
# argument info
# body ...
# 식으로...

# 모든 register는 IStorage의 subclass들중에 하나여야 한다.
# 모든 Return은 Value를 끼고 있어야 한다.
# 모든 Type은 일단 ASTType을 중심으로 돌아야 한다.
class Translate:
    def __init__(self, globalSymbolTable, mustCompileSet):
        #self.globalSymbolTable = globalSymbolTable
        self.mustCompileSet = mustCompileSet

        self.symbolTable = []
        self.symbolTable += globalSymbolTable

        self.context = []
        self.localSymbolList = []

        self.machine = Intel

        self.generateMachineCode()

    def getRootSymbolTable(self):
        return self.symbolTable[0]

    def getRecentSymbolTable(self):
        return self.symbolTable[-1]

    def generateMachineCode(self):
        if isinstance(self.mustCompileSet, FunctionSymbol):
            self.symbolTable.append(SymbolTable())

            funcinfo = self.mustCompileSet

            localSymbolTable = self.getRecentSymbolTable()

            # 인자를 등록합니다.
            argNameList = []
            for arg in funcinfo.args:
                localSymbolTable.registerVariable(arg.name, arg.type)
                argNameList.append(arg.name)

            funcbody = funcinfo.body
            self.procFunc(funcbody, argNameList)

            # remove last one
            self.symbolTable.pop()

    def getLastContext(self):
        return self.context[-1]

    def procFunc(self, tree, args):
        context = Context()
        self.context.append(context)

        # 일단 함수 인자들을 machine stack에 밀어넣는다.
        context = self.getLastContext()

        # 여기서 system dependent한 메모리 레지스터를 사용하는 것은 좋아보이지 않는다.
        # Intel.py로 코드를 이동시켜야할듯.(2013/03/12)
        for pos, arg in enumerate(args):
            memReg = context.setArgVar(arg)
            opcode = context.machine.OpMove(context.convertArgumentToReg(pos), memReg)
            context.context.append(opcode)
            print "mov %s, %s" % (str(memReg), context.convertArgumentToReg(pos))

            # we will suppose that alignment's size is 8 bytes.
            context.increaseReservedStackSize()

        if isinstance(tree, ASTExprs):
            self.procExprs(tree)
        elif isinstance(tree, ASTExpr):
            self.procExpr(tree)
        else:
            #print tree, type(tree)
            #raise Exception("procFunc", "Not implemented some feature")
            self.procExpr(tree)

        self.getLastContext().getRegisterAllocation(args)

        self.context.pop()

    def procReturn(self, tree):
        retval = self.procExpr(tree.expr)
        
        context = self.getLastContext()
        if retval == None:
            # 되돌려지는게 없다면, return type에 맞추어서 무엇인가를 보내야한다? TODO
            context.emitMove(IImm(0), self.machine.getRetReg())
        else:
            context.emitMove(retval.reg, self.machine.getRetReg())
        
        # 끝이기 때문에 별도로 되돌려줄 무엇인가가 없다          
        return None

    def procExprs(self, tree):
        result = None
        for subtree in tree.exprs:
            result = self.procExpr(subtree)
        return result

    def procExpr(self, tree):
        if isinstance(tree, ASTSimpleExprs):
            return self.procSimpleExprs(tree)
        elif isinstance(tree, ASTWord):
            return self.procWord(tree)
        elif isinstance(tree, ASTIf):
            raise Exception("ASTIf in procExpr", "Not Implemented")
        elif isinstance(tree, ASTFor):
            self.procFor(tree)
        elif isinstance(tree, ASTOperator):
            # 여기 이렇게 놓으면 안될듯한 느낌이..
            return self.procOperator(tree)
        elif isinstance(tree, ASTReturn):
            self.procReturn(tree)
        else:
            print tree, type(tree)
            raise Exception("procExpr", "Not Implemented")

        return None

    def procFor(self, tree):
        midLabelStr = genTemporaryString()
        lastLabelStr = genTemporaryString()

        context = self.getLastContext()
        if isinstance(tree.cond, ASTOperator):
            cond = tree.cond
            # 'for var <= list:'
            if cond.name == '<=':
                # 이 경우 right쪽은 initialization code라 생각한다.
                ret = self.procSimpleExpr(cond.right)

                context.emitLabel(midLabelStr)

                # TODO(2013.10.18.) : 더 이상 남은게 없는지 확인해서 마지막으로 가는 코드가 필요하다.
                # 특정 flag를 이용해서 다른데로 갈 수 있지만...
                # iterator는 어떻게 쓰는지 몰라서 다른 언어에서의 사용법을 먼저 확인하고 코딩해야한다.
                # 일단 지금은 물어본다.
                # 나중에 함수 하나로 어떻게 안될까낭?? (가장 nice한 방법은 python처럼 yield keyword가 있는 구조라고 생각된다.)
                nativeName = encodeSymbolName(name = 'System.lang.Array.end', args = [ret.type])
                context.emitPush(self.machine.getRetReg())
                context.emitCall(nativeName, [ret.reg], ret = True)

                # return이 1이면, end로 가야한다.
                context.emitComp(self.machine.getRetReg(), self.machine.IInteger(1))
                context.emitPop(self.machine.getRetReg())   # control bit가 바뀌지 않을지 걱정해야 한다.

                # zero flag가 1이면(즉, 0)
                context.emitJumpZeroFlag(lastLabelStr)

                # 보통 오른쪽에 있는 것은 iterator가 가능한 object가 됨
                context.emitPush(self.machine.getRetReg())
                nativeName = encodeSymbolName(name = 'System.lang.Array.getNext', args = [ret.type])
                context.emitCall(nativeName, [ret.reg], ret = True)

                left = self.procSimpleExpr(cond.left)
                context.emitMove(self.machine.getRetReg(), left.reg)
                context.emitPop(self.machine.getRetReg())
            else:
                print tree, type(tree)
                raise Exception('procForCond', 'Not implemented')
        else:
            print tree, type(tree)
            raise Exception('procForCond', 'Not implemented')

        ret = self.procExprs(tree.body)
        context.emitJump(midLabelStr)
        context.emitLabel(lastLabelStr)

    def procSimpleExprs(self, tree):
        result = None
        for expr in tree.exprs:
            result = self.procSimpleExpr(expr)
        # 마지막에 걸리는 type을 가준으로 한다.
        return result

    def procSimpleExpr(self, tree):
        if isinstance(tree, ASTWord):
            return self.procWord(tree)
        elif isinstance(tree, ASTOperator):
            return self.procOperator(tree)
        elif isinstance(tree, ASTListGenerateType1):
            return self.procListGeneratorType1(tree)
        elif isinstance(tree, ASTReturn):
            return self.procReturn(tree)
        else:
            print tree, type(tree)
            raise Exception('procSimpleExpr', 'Not implemented')

    def procListGeneratorType1(self, tree):
        left = self.procSimpleExpr(tree.start)
        right = self.procSimpleExpr(tree.end)
        
        nativeName = encodeSymbolName('System.lang.Array.toRange', args = [left.type, right.type])
        print nativeName

        context = self.getLastContext()
        context.emitPush(self.machine.getRetReg())
        # template일 경우 어떻게 이름을 정해야 할지...
        context.emitCall(nativeName, [left.reg, right.reg], ret = True)

        tmpReg = genTempRegister()
        context.emitMove(self.machine.getRetReg(), tmpReg)
        context.emitPop(self.machine.getRetReg())

        return Value(type = ASTType(name = 'System.lang.Array', templ = None, ranks = None), reg = tmpReg)

    def isBasicType(self, type):
        if type == 'System.lang.Integer' \
            or type == 'System.lang.Float' \
            or type == 'System.lang.Double':
            return True

        return False

    def getRealname(self, name):
        print "Searching %s" % (name)
        for tbl in reversed(self.symbolTable):
            realname = tbl.getRealname(name)
            if realname: return realname

        return None

    def getSymbolInfo(self, native):
        for elem in reversed(self.symbolTable):
            if elem.has_key(native):
                return elem[native]

        return None

    def makeFName(self, typeStr, name):
        return ".".join([str(typeStr), str(name)])

    def compareTypeStr(self, leftType, rightType):
        return leftType == rightType

    # 모든 type 정보는 ASTType을 사용하도록??
    def procOperator(self, tree):
        left = self.procExpr(tree.left)
        right = self.procExpr(tree.right)
        if not self.compareTypeStr(left.type, right.type):
            print "Error: mismatched type"
            print "type of left tree = '%s'" % (left.type)
            print "type of right tree = '%s'" % (right.type)
            return None

        context = self.getLastContext()

        tmpReg = genTempRegister()
        if self.isBasicType(left.type):            
            if left.type == 'System.lang.String':
                fn = self.makeFName(left.type, tree.name)

                context.emitPush(self.machine.getRetReg())
                context.emitCall(fn, [left.reg, right.reg], ret = True)

                tmpReg = genTempRegister()
                context.emitMove(self.machine.getRetReg(), tmpReg)
                context.emitPop(self.machine.getRetReg())

                return Value(type = left.type, reg = tmpReg)
            else:
                if tree.name == '+':
                    if left.type == 'System.lang.Integer':
                        context.emitAdd(left.reg, right.reg, tmpReg)
                    else:
                        print "Not Implemented about '%s' type" % (left.type)
                        raise Exception("procOperator", "Not implemented")
                elif tree.name == '-':
                    if left.type == 'System.lang.Integer':
                        context.emitSub(left.reg, right.reg, tmpReg)
                    else:
                        print "Not Implemented about '%s' type" % (left.type)
                        raise Exception("procOperator", "Not implemented")
                elif tree.name == '*':
                    if left.type == 'System.lang.Integer':
                        context.emitMul(left.reg, right.reg, tmpReg)
                    else:
                        print "Not Implemented about '%s' type" % (left.type)
                        raise Exception("procOperator", "Not implemented")
                elif tree.name == '/':
                    if left.type == 'System.lang.Integer':
                        context.emitDiv(left.reg, right.reg, tmpReg)
                    else:
                        print "Not Implemented about '%s' type" % (left.type)
                        raise Exception("procOperator", "Not implemented")
                elif tree.name == '=':
                    if left.type == 'System.lang.Integer':
                        context.emitMove(right.reg, left.reg)
                    else:
                        print "Not Implemented about '%s' type" % (left.type)
                        raise Exception("procOperator", "Not implemented")
                elif tree.name == '+=':
                    if left.type == 'System.lang.Integer':
                        context.emitAdd(right.reg, left.reg, left.reg)
                    else:
                        print "Not Implemented about '%s' type" % (left.type)
                        raise Exception("procOperator", "Not implemented")
                else:
                    print tree.name 
                    print tree.left
                    print tree.right
                    raise Exception("procOperator", "Not implemented")
 
            return Value(type = left.type, reg = tmpReg)
        else:
            opName = self.makeFName(left.type, tree.name)
            nativeName = encodeSymbolName(opName, args = [left.right])
            print nativeName 
            context.emitPush(self.machine.getRetReg())
            context.emitCall(nativeName, [left.reg, right.reg], ret = True)
            context.emitMove(self.machine.getRetReg(), tmpReg)
            context.emitPop(self.machine.getRetReg())

            retType = left.type

            return Value(type = retType, reg = tmpReg)

    def procWord(self, tree):
        tmpReg = genTempRegister()

        context = self.getLastContext()
        if tree.isType('System.lang.String'):
            return Value(type = ASTType(name = 'System.lang.String', templ = None, ranks = None), reg = self.machine.IString(tree.value))
        elif tree.isType('System.lang.Integer'):
            return Value(type = ASTType(name = 'System.lang.Integer', templ = None, ranks = None), reg = self.machine.IInteger(tree.value))
        elif tree.isType('System.lang.Double'):
            return Value(type = ASTType(name = 'System.lang.Double', templ = None, ranks = None), reg = self.machine.IDouble(tree.value))
        elif tree.isType('System.lang.Float'):
            return Value(type = ASTType(name = 'System.lang.Float', templ = None, ranks = None), reg = self.machine.IFloat(tree.value))
        elif tree.isType('id'):
            valinfo = self.getRealname(tree.value)
            valinfo = self.getSymbolInfo(valinfo)

            if valinfo == None:
                raise Exception('Error', 'Unknown type : %s' % (tree.value))

            return Value(type = valinfo.type, reg = self.machine.IUserReg(tree.value))
        else:
            print tree, type(tree)

        return Value(type = tree.getType(), reg = tmpReg)
