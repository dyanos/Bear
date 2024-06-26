# -*- coding: utf-8 -*-
# !/usr/bin/env python
import os, sys, string

import CSEL.TypeTable
from .ASTType import *
from .SymbolTable import *
from .mangle import *
from .context import *
from .Operand import *
from .Value import *
from .Intel import *
from .TypeTable import *

# from graph import *
from . import Intel
import traceback


Seperator = '$'


def genRandomString(length):
  chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_"
  locs = [random.randint(0, len(chars) - 1) for i in range(0, length)]
  return "".join([chars[loc] for loc in locs])


# 3-state machine code
class Context:
  def __init__(self):
    self.context = []
    
    self.machine = Intel
    self.sizeOfMachineRegister = 8  # bytes
    self.reservedStackSize = 0
    
    # 이건 머징??
    self.undef = {}
    
    self.arguments = {}
    self.narguments = 8
    self.dataSection = {}
  
  def checkTemporaryReg(self, regList, loc):
    for elem in regList:
      if self.machine.isTemporaryRegister(elem) == True:
        self.registerLoc(elem.name, loc)
  
  def registerLoc(self, name, loc):
    if name not in self.undef:
      self.undef[name] = [loc]
    else:
      self.undef[name].append(loc)
  
  def increaseReservedStackSize(self):
    self.reservedStackSize += self.sizeOfMachineRegister
  
  # 일단 늘어나면 안 줄어들텐데...
  def decreaseReservedStackSize(self):
    self.reservedStackSize -= self.sizeOfMachineRegister
  
  def emitMove(self, src, dst):
    operand = self.machine.OpMove(src, dst)
    self.context.append(operand)
    self.checkTemporaryReg(regList=[src, dst], loc=len(self.context))
    
    print("mov %s, %s" % (dst, src))
  
  def emitAdd(self, srcA, srcB, dst):
    context = self.context
    if self.machine == Intel:
      tmpReg = genTempRegister()
      self.emitMove(srcA, tmpReg)
      context.append(self.machine.OpAdd(srcB, tmpReg))
      print("add %s, %s" % (tmpReg, srcB))
      self.emitMove(tmpReg, dst)
    else:
      print("add %s, %s, %s" % (dst, srcB, srcA))

  def emitMul(self, srcA, srcB, dst):
    context = self.context
    if self.machine == Intel:
      tmpReg = genTempRegister()
      self.emitMove(srcA, tmpReg)
      context.append(self.machine.OpMul(srcB, tmpReg))
      print("mul %s, %s" % (tmpReg, srcB))
      self.emitMove(tmpReg, dst)
    else:
      print("mul %s, %s, %s" % (dst, srcB, srcA))
  
  def emitDiv(self, srcA, srcB, dst):
    context = self.context
    if self.machine == Intel:
      tmpReg = genTempRegister()
      self.emitMove(srcA, tmpReg)
      context.append(self.machine.OpDiv(srcB, tmpReg))
      print("div %s, %s" % (tmpReg, srcB))
      self.emitMove(tmpReg, dst)
    else:
      print("div %s, %s, %s" % (dst, srcB, srcA))

  def emitPush(self, target):
    operand = self.machine.OpPush(target)
    self.context.append(operand)
    
    print("push %s" % (target))
  
  def emitPop(self, target):
    operand = self.machine.OpPop(target)
    self.context.append(operand)
    
    print("pop %s" % (target))
  
  def emitCall(self, target, args, ret=False):
    parameterList = [IReg('rcx'), IReg('rdx'), IReg('r8'), IReg('r9')]
    pushedRegisters = []
    # http://msdn.microsoft.com/en-US/library/zthk2dkh(v=vs.80).aspx
    for num, reg in enumerate(args):
      tmpreg = None
      if isinstance(reg, ASTWord):
        if reg.type == 'id':
          tmpreg = IUserReg(reg.value)
        elif reg.type == ASTType('System.lang.String'):
          tmpreg = self.registerInDataSection(reg.value)
        elif reg.type == 'System.lang.Int':
          tmpreg = IImm(reg['@value'])
        else:
          print(reg.type, reg.value)
          raise NotImplementedError
      elif isinstance(reg, IStorage):
        tmpreg = reg
      elif isinstance(reg, Value):
        tmpreg = reg.reg
      else:
        print(reg)
        raise NotImplementedError
      
      if num < len(parameterList):
        _reg = parameterList[num]
        self.emitPush(_reg)
        pushedRegisters.append(_reg)
        self.emitMove(tmpreg, _reg)
      else:
        self.emitPush(tmpreg)
    
    # return 변수가 있을 경우, 일단 있다고 가정...
    # self.context.append(self.machine.OpPush(IReg('rax')))
    # self.context.append(self.machine.OpMove(IImm(0), IReg('rax')))
    # if ret == True:
    #  self.context.append(self.machine.OpPush(IReg('rax')))
    #  self.context.append(self.machine.OpMove(IImm(0), IReg('rax')))
    
    operand = self.machine.OpCall(target, len(args), ret=ret)
    self.context.append(operand)
    
    print("call %s" % (target))
    
    for reg in reversed(pushedRegisters):
      self.emitPop(reg)
  
  def emitComp(self, target1, target2):
    operand = self.machine.OpComp(target1, target2)
    self.context.append(operand)
    print("cmp %s, %s" % (target1, target2))
  
  def emitJump(self, label):
    operand = self.machine.OpJump(label)
    self.context.append(operand)
    print("jmp %s" % (label))
  
  def emitJumpZeroFlag(self, label):
    operand = self.machine.OpJumpZeroFlag(label)
    self.context.append(operand)
    print("jz %s" % (label))
  
  def emitJumpUsingReg(self, reg):
    operand = self.machine.OpJumpToReg(reg)
    self.context.append(operand)
    print("jmp %s" % (reg))
  
  def emitLabel(self, labelname):
    self.context.append(self.machine.MarkLabel(labelname))
    print("%s:" % (labelname))
  
  def calStackSize(self):
    pass
  
  def getRegisterAllocation(self, args):
    #    g = graph(directional = True)
    #    for operand in self.context:
    #      if isinstance(operand, self.machine.OpMove):
    #        g.addEdge(operand.src, operand.dst)
    
    # to analysis
    
    return RegisterAllocation.doRegisterAllocation(self.context, args)
  
  # register 재배치 알고리즘을 돌린 결과
  def reallocRegisters(self):
    pass
  
  def registerInDataSection(self, data):
    name = self.makeDataAlias()
    self.dataSection[name] = data
    return IConstVar(name)
  
  def makeDataAlias(self):
    return genRandomString(16)


# TODO: Unused Symbol에 대한 처리코드가 필요?
# TODO: iadd, imul과 같은 특수 명령어에 대한 처리 기능 추가?
# TODO: 오류 출력 기능 향상 : 파일 이름, 현재 파싱되고 있는 line, 오류 출력시 해당 line번호 출력 - token parsing할때 token정보에 관련 정보 출력하도록 
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
  def __init__(self, symbolTable):
    print("initializing translate")

    self.isdebug = False
    
    # self.globalSymbolTable = globalSymbolTable
    self.symbolTable = symbolTable
    
    self.context = []
    self.external = {}
    self.reservedStackSize = 0
    self.info = None
    
    self.machine = Intel
    
    self.codes = None
    self.datas = None
    self.extern = None
    
    self.generateMachineCode()
  
  # TODO 일단 DataSection을 다음과 같이 읽어가도록 한다.
  def getDataSection(self):
    return self.datas
  
  def generateMachineCode(self):
    if "main" in self.symbolTable:
      self.procFunc(self.symbolTable["main"])
  
  def getLastContext(self):
    return self.context[-1]
  
  def procFunc(self, tree: FuncType):
    self.context.append(Context())
    
    # 일단 함수 인자들을 machine stack에 밀어넣는다.
    ctxt = self.getLastContext()
    
    # 여기서 system dependent한 메모리 레지스터를 사용하는 것은 좋아보이지 않는다.
    # Intel.py로 코드를 이동시켜야할듯.(2013/03/12)
    args = tree.args
    for pos, arg in enumerate(args):
      content, name = {}, None
      if isinstance(arg, ASTDefArg):
        name = arg.name
        content['ret_type'] = arg.type
      else:
        print(arg)
        raise NotImplementedError
      
      if name == None:
        raise SyntaxError
      
      content['@loc'] = pos
      
      self.external[name] = content
    
    self.info = tree
    body = tree.body
    if self.isdebug:
      body.printXML()

    # ASTReturn은 아래 것들 중에 걸리는게 없다... 근데 왜 Exception이 안나왔지??
    if isinstance(body, ASTExprs):
      self.procExprs(body)
    elif isinstance(body, ASTExpr):
      self.procExpr(body.expr)
    elif isinstance(body, ASTSimpleExprs):
      self.procSimpleExprs(body)
    else:
      print(tree, type(tree))
      raise NotImplementedError
    
    opcode = ctxt.machine.OpRet()
    ctxt.context.append(opcode)
    self.info = None
    
    self.codes = ctxt.getRegisterAllocation(args)
    self.datas = ctxt.dataSection
    
    self.context.pop()
  
  def procReturn(self, tree):
    retval = self.procExpr(tree.expr)
    if retval == None:
      return None
    
    context = self.getLastContext()
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
    elif isinstance(tree, ASTID):
      return self.procID(tree)
    elif isinstance(tree, ASTIf):
      raise Exception("ASTIf in procExpr", "Not Implemented")
    elif isinstance(tree, ASTFor):
      self.procFor(tree)
    elif isinstance(tree, ASTBinOperator):
      # 여기 이렇게 놓으면 안될듯한 느낌이..
      return self.procOperator(tree)
    elif isinstance(tree, ASTReturn):
      self.procReturn(tree)
    elif isinstance(tree, ASTFuncCall):
      # 양쪽의 Argument들은 Evaluate되어야만 한다.
      new_args = []
      for arg in tree.args:
        if isinstance(arg, ASTBinOperator):
          new_args.append(arg.vtype)
        elif isinstance(arg, ASTType):
          raise SyntaxError
        elif isinstance(arg, ASTWord):
          new_args.append(arg.type)
        elif isinstance(arg, ASTFuncCall):
          new_args.append(self.procExpr(arg))
        elif isinstance(arg, ASTID):
          new_args.append(self.procExpr(arg))
        else:
          print(type(arg), arg.type, isinstance(arg.type, CSEL.TypeTable.Type))
          raise NotImplementedError
      
      print(list(self.symbolTable.table.keys()))
      if isinstance(tree.name, ASTNames):
        sym = self.symbolTable.glob(path=".".join(tree.name.array), args=new_args)
      else:
        if isinstance(tree.name, ASTID):
          path = tree.name.name

        sym = self.symbolTable.glob(path=path, args=new_args)

      if sym is None:
        print(f"Error) failed to find {tree.name}")
        raise SyntaxError
      
      nativeName = mangling(sym)
      
      # return value가 있는지 체크해야만 한다.
      if sym is None:
        raise Exception("procExpr", "Symbol Not Found")
      
      retv = False
      if sym != UnitType():
        retv = True
      
      regs = []
      for arg in tree.args:
        ret = self.procExpr(arg)
        regs.append(ret)
      
      context = self.getLastContext()
      context.emitCall(nativeName, regs, ret=retv)
      
      if retv == True:
        return Value(type=sym, reg=self.machine.getRetReg())
    elif isinstance(tree, ASTCalleeArgType1):
      ret = self.procExpr(tree.value)
      #print(ret)
    elif isinstance(tree, ASTListGenerateType1):
      return self.procListGeneratorType1(tree)
    else:
      print(tree, type(tree))
      tree.printXML()
      raise Exception("procExpr", "Not Implemented")
    
    return None
  
  def procFor(self, tree):
    midLabelStr = genTemporaryString()
    lastLabelStr = genTemporaryString()
    
    context = self.getLastContext()
    if isinstance(tree.generator, ASTListGenerateType1):
      # List Generator를 생성하는 생성자를 호출한다.
      symbolInitFunc = encodeSymbolName(name='System.lang.Array.Array', args=[])
      context.emitPush(self.machine.getRetReg())
      context.emitCall(symbolInitFunc, [], ret=True)
      tmpReg = genTempRegister()
      context.emitMove(self.machine.getRetReg(), tmpReg)
      context.emitPop(self.machine.getRetReg())
      
      context.emitLabel(midLabelStr)
      
      # TODO(2013.10.18.) : 더 이상 남은게 없는지 확인해서 마지막으로 가는 코드가 필요하다.
      # 특정 flag를 이용해서 다른데로 갈 수 있지만...
      # iterator는 어떻게 쓰는지 몰라서 다른 언어에서의 사용법을 먼저 확인하고 코딩해야한다.
      # 일단 지금은 물어본다.
      # 나중에 함수 하나로 어떻게 안될까낭?? (가장 nice한 방법은 python처럼 yield keyword가 있는 구조라고 생각된다.)
      nativeName = encodeSymbolName(name='System.lang.Array.end', args=['System.lang.Array'])
      context.emitPush(self.machine.getRetReg())
      context.emitCall(nativeName, [tmpReg], ret=True)
      
      # return이 1이면, end로 가야한다.
      context.emitComp(self.machine.getRetReg(), self.machine.IInteger(1))
      context.emitPop(self.machine.getRetReg())  # control bit가 바뀌지 않을지 걱정해야 한다.
      
      # zero flag가 1이면(즉, 0)
      context.emitJumpZeroFlag(lastLabelStr)
      
      # 보통 오른쪽에 있는 것은 iterator가 가능한 object가 됨
      context.emitPush(self.machine.getRetReg())
      nativeName = encodeSymbolName(name='System.lang.Array.getNext', args=['System.lang.Array'])
      context.emitCall(nativeName, [tmpReg], ret=True)
      context.emitMove(self.machine.getRetReg(), tmpReg)
      context.emitPop(self.machine.getRetReg())
    
    if isinstance(tree.cond, ASTBinOperator):
      cond = tree.cond
      # 'for var <= list:'
      if cond.name == '<=':
        left = self.procSimpleExpr(tree.cond.left)
        context.emitMove(self.machine.getRetReg(), left.reg)
        context.emitPop(self.machine.getRetReg())
        
        # 이 경우 right쪽은 initialization code라 생각한다.
        ret = self.procSimpleExpr(cond.right)
        
        context.emitLabel(midLabelStr)
        
        # TODO(2013.10.18.) : 더 이상 남은게 없는지 확인해서 마지막으로 가는 코드가 필요하다.
        # 특정 flag를 이용해서 다른데로 갈 수 있지만...
        # iterator는 어떻게 쓰는지 몰라서 다른 언어에서의 사용법을 먼저 확인하고 코딩해야한다.
        # 일단 지금은 물어본다.
        # 나중에 함수 하나로 어떻게 안될까낭?? (가장 nice한 방법은 python처럼 yield keyword가 있는 구조라고 생각된다.)
        nativeName = encodeSymbolName(name='System.lang.Array.end', args=[ret.type])
        context.emitPush(self.machine.getRetReg())
        context.emitCall(nativeName, [ret.reg], ret=True)
        
        # return이 1이면, end로 가야한다.
        context.emitComp(self.machine.getRetReg(), self.machine.IInteger(1))
        context.emitPop(self.machine.getRetReg())  # control bit가 바뀌지 않을지 걱정해야 한다.
        
        # zero flag가 1이면(즉, 0)
        context.emitJumpZeroFlag(lastLabelStr)
        
        # 보통 오른쪽에 있는 것은 iterator가 가능한 object가 됨
        context.emitPush(self.machine.getRetReg())
        nativeName = encodeSymbolName(name='System.lang.Array.getNext', args=[ret.type])
        context.emitCall(nativeName, [ret.reg], ret=True)
        
        left = self.procSimpleExpr(cond.left)
        context.emitMove(self.machine.getRetReg(), left.reg)
        context.emitPop(self.machine.getRetReg())
      else:
        print(tree, type(tree))
        raise Exception('procForCond', 'Not implemented')
    else:
      if True:
        generator = self.procSimpleExpr(tree.generator)
        
        context.emitLabel(midLabelStr)
        
        # TODO(2013.10.18.) : 더 이상 남은게 없는지 확인해서 마지막으로 가는 코드가 필요하다.
        # 특정 flag를 이용해서 다른데로 갈 수 있지만...
        # iterator는 어떻게 쓰는지 몰라서 다른 언어에서의 사용법을 먼저 확인하고 코딩해야한다.
        # 일단 지금은 물어본다.
        # 나중에 함수 하나로 어떻게 안될까낭?? (가장 nice한 방법은 python처럼 yield keyword가 있는 구조라고 생각된다.)
        nativeName = encodeSymbolName(name='System.lang.Array.end', args=[generator.type])
        context.emitPush(self.machine.getRetReg())
        context.emitCall(nativeName, [generator.reg], ret=True)
        
        # return이 1이면, end로 가야한다.
        context.emitComp(self.machine.getRetReg(), self.machine.IInteger(1))
        context.emitPop(self.machine.getRetReg())  # control bit가 바뀌지 않을지 걱정해야 한다.
        
        # zero flag가 1이면(즉, 0)
        context.emitJumpZeroFlag(lastLabelStr)
        
        # 보통 오른쪽에 있는 것은 iterator가 가능한 object가 됨
        context.emitPush(self.machine.getRetReg())
        nativeName = encodeSymbolName(name='System.lang.Array.getNext', args=[generator.type])
        context.emitCall(nativeName, [generator.reg], ret=True)
      else:
        print(tree, type(tree))
        print(tree.cond, type(tree.cond))
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
  
  def procSimpleExpr(self, tree: AST):
    if isinstance(tree, ASTWord):
      return self.procWord(tree)
    elif isinstance(tree, ASTID):
      return self.procID(tree)
    elif isinstance(tree, ASTBinOperator):
      return self.procOperator(tree)
    elif isinstance(tree, ASTListGenerateType1):
      return self.procListGeneratorType1(tree)
    elif isinstance(tree, ASTReturn):
      return self.procReturn(tree)
    elif isinstance(tree, ASTFuncCall):
      context = self.getLastContext()
      args = []
      # type체킹은 parser에서 다 끝냈다고 생각하고...
      for arg in tree.args:
        if isinstance(arg, ASTCalleeArgType1):
          args.append(arg.value)
        elif isinstance(arg, ASTWord):
          args.append(arg)
        else:
          print(arg)
          raise NotImplementedError
      
      nativeName = encodeSymbolName(tree.name.array)
      context.emitCall(nativeName, args)
    elif isinstance(tree, ASTCalleeArgType1):
      raise NotImplementedError
    elif isinstance(tree, ASTCalleeArgType2):
      raise NotImplementedError
    elif isinstance(tree, ASTWrap):
      if isinstance(tree.history, ASTSimpleExprs):
        for expr in tree.history.exprs:
          self.procExpr(expr)
      else:
        print(f"tree.history={tree.history}")
        raise NotImplementedError
    else:
      print("procSimpleExpr : ", end=' ')
      print(tree, type(tree), tree.history)
      raise Exception('procSimpleExpr', 'Not implemented')
  
  def procListGeneratorType1(self, tree):
    left = self.procSimpleExpr(tree.start)
    right = self.procSimpleExpr(tree.end)
    
    nativeName = encodeSymbolName('System.lang.Array.toRange', args=[left.type, right.type])
    # print nativeName
    
    context = self.getLastContext()
    context.emitPush(self.machine.getRetReg())
    # template일 경우 어떻게 이름을 정해야 할지...
    context.emitCall(nativeName, [left.reg, right.reg], ret=True)
    
    tmpReg = genTempRegister()
    context.emitMove(self.machine.getRetReg(), tmpReg)
    context.emitPop(self.machine.getRetReg())
    
    return Value(type=ASTType(name='System.lang.Array<{}>'.format(left.type), templ=None, ranks=None), reg=tmpReg)
  
  def isBasicType(self, type: Type):
    if type == IntegerType() \
      or type == FloatType() \
      or type == DoubleType():
      return True
    
    return False
  
  def getRealname(self, name):
    # print "Searching %s" % (name)
    for tbl in reversed(self.symbolTable):
      realname = tbl.getRealname(name)
      if realname: return realname
    
    return None
  
  def getSymbolInfo(self, native):
    for elem in reversed(self.symbolTable):
      if native in elem:
        return elem[native]
    
    return None
  
  def makeFName(self, typeStr, name):
    return ".".join([str(typeStr), str(name)])
  
  def compareTypeStr(self, leftType, rightType):
    return leftType == rightType
  
  def convertToASTType(self, obj: AST) -> Type:
    if isinstance(obj, ASTType):
      return obj
    elif isinstance(obj, ASTWord):
      return obj.type
    elif isinstance(obj, Value):
      return obj.type
    else:
      print(obj)
      raise NotImplementedError
  
  # 모든 type 정보는 ASTType을 사용하도록??
  def procOperator(self, tree):
    #print("calling procOperator")
    #traceback.print_stack()
    
    context = self.getLastContext()
    
    left = self.procExpr(tree.left)
    right = self.procExpr(tree.right)
    
    tmpReg = genTempRegister()
    if self.isBasicType(left.type):
      if left.type == StringType():
        fn = self.makeFName(left.type, tree.name)
        
        context.emitPush(self.machine.getRetReg())
        context.emitCall(fn, [left.reg, right.reg], ret=True)
        
        tmpReg = genTempRegister()
        context.emitMove(self.machine.getRetReg(), tmpReg)
        context.emitPop(self.machine.getRetReg())
        
        return Value(type=left.type, reg=tmpReg)
      else:
        if tree.name == '+':
          if left.type == IntegerType():
            context.emitAdd(left.reg, right.reg, tmpReg)
          else:
            print("Not Implemented about '%s' type" % (left.type))
            raise Exception("procOperator", "Not implemented")
        elif tree.name == '-':
          if left.type == IntegerType():
            context.emitSub(left.reg, right.reg, tmpReg)
          else:
            print("Not Implemented about '%s' type" % (left.type))
            raise Exception("procOperator", "Not implemented")
        elif tree.name == '*':
          if left.type == IntegerType():
            context.emitMul(left.reg, right.reg, tmpReg)
          else:
            print("Not Implemented about '%s' type" % (left.type))
            raise Exception("procOperator", "Not implemented")
        elif tree.name == '/':
          if left.type == IntegerType():
            context.emitDiv(left.reg, right.reg, tmpReg)
          else:
            print("Not Implemented about '%s' type" % (left.type))
            raise Exception("procOperator", "Not implemented")
        elif tree.name == '=':
          if left.type == IntegerType():
            context.emitMove(right.reg, left.reg)
          else:
            print("Not Implemented about '%s' type" % (left.type))
            raise Exception("procOperator", "Not implemented")
        elif tree.name == '+=':
          if left.type == IntegerType():
            context.emitAdd(right.reg, left.reg, left.reg)
          else:
            print("Not Implemented about '%s' type" % (left.type))
            raise Exception("procOperator", "Not implemented")
        else:
          print(tree.name)
          print(tree.left)
          print(tree.right)
          raise Exception("procOperator", "Not implemented")
      
      return Value(type=left.type, reg=tmpReg)
    else:
      opName = self.makeFName(left.type, tree.name)
      #print(left, tree, opName)
      nativeName = encodeSymbolName(opName, args=[left.type])
      # print nativeName
      context.emitPush(self.machine.getRetReg())
      context.emitCall(nativeName, [left.reg, right.reg], ret=True)
      context.emitMove(self.machine.getRetReg(), tmpReg)
      context.emitPop(self.machine.getRetReg())
      
      retType = left.type
      
      return Value(type=retType, reg=tmpReg)
  
  def procWord(self, tree: ASTWord) -> Value:
    tmpReg = genTempRegister()
    
    context = self.getLastContext()
    if isinstance(tree.type, StringType):
      return Value(type=ASTType(name='System.lang.String', templ=None, ranks=None),
                   reg=self.machine.IString(tree.value))
    elif isinstance(tree.type, IntegerType):
      return Value(type=ASTType(name='System.lang.Int', templ=None, ranks=None),
                   reg=self.machine.IInteger(tree.value))
    elif isinstance(tree.type, DoubleType):
      return Value(type=ASTType(name='System.lang.Double', templ=None, ranks=None),
                   reg=self.machine.IDouble(tree.value))
    elif isinstance(tree.type, FloatType):
      return Value(type=ASTType(name='System.lang.Float', templ=None, ranks=None), reg=self.machine.IFloat(tree.value))
    else:
      print(tree, type(tree))
      raise NotImplementedError
    
    return Value(type=tree.getType(), reg=tmpReg)
  
  def procID(self, tree: ASTID) -> Value:
    tmpReg = genTempRegister()
    
    context = self.getLastContext()
    info = tree.type
    if isinstance(info, dict):
      info = info['vtype']

    if not isinstance(info, Type):
      print(info)
      raise Exception('Error', 'Not Type')
    
    return Value(type=info, reg=self.machine.IUserReg(tree.name))
    # return Value(type=tree.getType(), reg=tmpReg)
