# -*- coding: utf-8 -*-
#!/usr/bin/env python
import os,sys,string
from ASTType import *
from SymbolTable import *
from mangle import *
from context import *
from Operand import *
from ASTCalleeArgType1 import *
from ASTCalleeArgType2 import *
from ASTListGenerateType1 import *
from Value import *

#from graph import *
import Intel

Seperator = '$'

def genRandomString(length):
  chars  = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_"
  locs  = [random.randint(0, len(chars)-1) for i in range(0, length)]
  return "".join(map(lambda loc: chars[loc], locs))
    
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
    self.dataSection = {}

  def checkTemporaryReg(self, regList, loc):
    for elem in regList:
      if self.machine.isTemporaryRegister(elem) == True:
        self.registerLoc(elem.name, loc)

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

  def emitMove(self, src, dst):
    operand = self.machine.OpMove(src, dst)
    self.context.append(operand)
    self.checkTemporaryReg(regList = [src, dst], loc = len(self.context))

    print "mov %s, %s" % (dst, src)

  def emitAdd(self, srcA, srcB, dst):
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
    operand = self.machine.OpPush(target)
    self.context.append(operand)

    print "push %s" % (target)

  def emitPop(self, target):
    operand = self.machine.OpPop(target)
    self.context.append(operand)

    print "pop %s" % (target)

  def emitCall(self, target, args, ret = False):
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
        elif reg.type == 'System.lang.Integer':
          tmpreg = IImm(reg['@value'])  
        else:
          print reg.type, reg.value
          raise NotImplementedError 
      elif isinstance(reg, IStorage):
        tmpreg = reg
      elif isinstance(reg, Value):
        tmpreg = reg.reg
      else:
        print reg
        raise NotImplementedError

      if num < len(parameterList):
        self.emitMove(tmpreg, parameterList[num])
      else:
        self.emitPush(tmpreg)

    # return 변수가 있을 경우, 일단 있다고 가정...
    #self.context.append(self.machine.OpPush(IReg('rax')))
    #self.context.append(self.machine.OpMove(IImm(0), IReg('rax')))
    operand = self.machine.OpCall(target, len(args), ret = ret)
    self.context.append(operand)

    print "call %s" % (target)

    for reg in reversed(pushedRegisters):
      self.emitPop(reg)

  def emitComp(self, target1, target2):
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
    operand = self.machine.OpJumpToReg(reg)
    self.context.append(operand)
    print "jmp %s" % (reg)

  def emitLabel(self, labelname):
    self.context.append(self.machine.MarkLabel(labelname))
    print "%s:" % (labelname)

  def calStackSize(self):
    pass

  def getRegisterAllocation(self, args):
#    g = graph(directional = True)
#    for operand in self.context:
#      if isinstance(operand, self.machine.OpMove):
#        g.addEdge(operand.src, operand.dst)
        
    # to analysis
      
    return self.machine.doRegisterAllocation(self.context, args)

  # register 재배치 알고리즘을 돌린 결과
  def reallocRegisters(self):
    pass

  def registerInDataSection(self, data):
    name = self.makeDataAlias()
    self.dataSection[name] = data
    return IConstVar(name)

  def makeDataAlias(self):
    return genRandomString(16)

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
  def __init__(self, symbolTable, mustCompileSet):
    print "initializing translate"

    #self.globalSymbolTable = globalSymbolTable
    self.mustCompileSet = mustCompileSet

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
    print "starting generateMachineCode", self.mustCompileSet
    if isinstance(self.mustCompileSet, list):
      raise NotImplementedError
    else:
      tree, name = self.mustCompileSet
      print tree
      if not tree.has_key('@type'):
        raise KeyError

      if tree['@type'] == 'def':
        self.procFunc(tree)
 
  def getLastContext(self):
    return self.context[-1]

  def procFunc(self, tree):
    context = Context()
    self.context.append(context)

    # 일단 함수 인자들을 machine stack에 밀어넣는다.
    context = self.getLastContext()

    # 여기서 system dependent한 메모리 레지스터를 사용하는 것은 좋아보이지 않는다.
    # Intel.py로 코드를 이동시켜야할듯.(2013/03/12)
    args = tree['@args']
    for pos, arg in enumerate(args):
      content = {}
      name = None
      if isinstance(arg, ASTDefArg):
        name = arg.name
        content['@type'] = arg.type
      else:
        raise NotImplementedError

      if name == None:
        raise SyntaxError

      content['@loc'] = pos

      self.external[name] = content

    self.info = tree
    body = tree['@body']
    if isinstance(body, ASTExprs):
      self.procExprs(body)
    elif isinstance(body, ASTExpr):
      self.procExpr(body)
    elif isinstance(body, ASTSimpleExprs):
      self.procSimpleExprs(body)
    else:
      print tree, type(tree)
      raise NotImplementedError

    opcode = context.machine.OpRet()
    context.context.append(opcode)
    self.info = None

    self.codes = context.getRegisterAllocation(args)
    self.datas = context.dataSection

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
    elif isinstance(tree, ASTIf):
      raise Exception("ASTIf in procExpr", "Not Implemented")
    elif isinstance(tree, ASTFor):
      self.procFor(tree)
    elif isinstance(tree, ASTOperator):
      # 여기 이렇게 놓으면 안될듯한 느낌이..
      return self.procOperator(tree)
    elif isinstance(tree, ASTReturn):
      self.procReturn(tree)
    elif isinstance(tree, ASTFuncCall):
      # 양쪽의 Argument들은 Evaluate되어야만 한다.
      new_args = []
      for argument in tree.args:
        new_args.append(self.procExpr(argument))
      
      nativeName = encodeSymbolName(name = tree.name, args = new_args)
      regs = []
      for arg in tree.args:
        ret = self.procExpr(arg)
        regs.append(ret)
        
      context = self.getLastContext()
      context.emitCall(nativeName, regs, ret = False)
    else:
      print tree, type(tree)
      raise Exception("procExpr", "Not Implemented")

    return None

  def procFor(self, tree):
    midLabelStr = genTemporaryString()
    lastLabelStr = genTemporaryString()

    context = self.getLastContext()
    if isinstance(tree.generator, ASTListGenerateType1):
      # List Generator를 생성하는 생성자를 호출한다.
      symbolInitFunc = encodeSymbolName(name = 'System.lang.Array.Array', args = [])  
      context.emitPush(self.machine.getRetReg())
      context.emitCall(symbolInitFunc, [], ret = True)
      tmpReg = genTempRegister()
      context.emitMove(self.machine.getRetReg(), tmpReg)
      context.emitPop(self.machine.getRetReg())

      context.emitLabel(midLabelStr)

      # TODO(2013.10.18.) : 더 이상 남은게 없는지 확인해서 마지막으로 가는 코드가 필요하다.
      # 특정 flag를 이용해서 다른데로 갈 수 있지만...
      # iterator는 어떻게 쓰는지 몰라서 다른 언어에서의 사용법을 먼저 확인하고 코딩해야한다.
      # 일단 지금은 물어본다.
      # 나중에 함수 하나로 어떻게 안될까낭?? (가장 nice한 방법은 python처럼 yield keyword가 있는 구조라고 생각된다.)
      nativeName = encodeSymbolName(name = 'System.lang.Array.end', args = ['System.lang.Array'])
      context.emitPush(self.machine.getRetReg())
      context.emitCall(nativeName, [tmpReg], ret = True)

      # return이 1이면, end로 가야한다.
      context.emitComp(self.machine.getRetReg(), self.machine.IInteger(1))
      context.emitPop(self.machine.getRetReg())  # control bit가 바뀌지 않을지 걱정해야 한다.

      # zero flag가 1이면(즉, 0)
      context.emitJumpZeroFlag(lastLabelStr)

      # 보통 오른쪽에 있는 것은 iterator가 가능한 object가 됨
      context.emitPush(self.machine.getRetReg())
      nativeName = encodeSymbolName(name = 'System.lang.Array.getNext', args = ['System.lang.Array'])
      context.emitCall(nativeName, [tmpReg], ret = True)

    if isinstance(tree.cond, ASTOperator):
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
        nativeName = encodeSymbolName(name = 'System.lang.Array.end', args = [ret.type])
        context.emitPush(self.machine.getRetReg())
        context.emitCall(nativeName, [ret.reg], ret = True)

        # return이 1이면, end로 가야한다.
        context.emitComp(self.machine.getRetReg(), self.machine.IInteger(1))
        context.emitPop(self.machine.getRetReg())  # control bit가 바뀌지 않을지 걱정해야 한다.

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
      if True:
        generator = self.procSimpleExpr(tree.generator)

        context.emitLabel(midLabelStr)

        # TODO(2013.10.18.) : 더 이상 남은게 없는지 확인해서 마지막으로 가는 코드가 필요하다.
        # 특정 flag를 이용해서 다른데로 갈 수 있지만...
        # iterator는 어떻게 쓰는지 몰라서 다른 언어에서의 사용법을 먼저 확인하고 코딩해야한다.
        # 일단 지금은 물어본다.
        # 나중에 함수 하나로 어떻게 안될까낭?? (가장 nice한 방법은 python처럼 yield keyword가 있는 구조라고 생각된다.)
        nativeName = encodeSymbolName(name = 'System.lang.Array.end', args = [generator.type])
        context.emitPush(self.machine.getRetReg())
        context.emitCall(nativeName, [generator.reg], ret = True)

        # return이 1이면, end로 가야한다.
        context.emitComp(self.machine.getRetReg(), self.machine.IInteger(1))
        context.emitPop(self.machine.getRetReg())  # control bit가 바뀌지 않을지 걱정해야 한다.

        # zero flag가 1이면(즉, 0)
        context.emitJumpZeroFlag(lastLabelStr)

        # 보통 오른쪽에 있는 것은 iterator가 가능한 object가 됨
        context.emitPush(self.machine.getRetReg())
        nativeName = encodeSymbolName(name = 'System.lang.Array.getNext', args = [generator.type])
        context.emitCall(nativeName, [generator.reg], ret = True)
      else: 
        print tree, type(tree)
        print tree.cond, type(tree.cond)
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
          print arg
          raise NotImplementedError
      
      nativeName = encodeSymbolName(tree.name.array)
      context.emitCall(nativeName, args)
    elif isinstance(tree, ASTCalleeArgType1):
      raise NotImplementedError
    elif isinstance(tree, ASTCalleeArgType2):
      raise NotImplementedError
    else:
      print "procSimpleExpr : ",
      print tree, type(tree)
      raise Exception('procSimpleExpr', 'Not implemented')

  def procListGeneratorType1(self, tree):
    left = self.procSimpleExpr(tree.start)
    right = self.procSimpleExpr(tree.end)
    
    nativeName = encodeSymbolName('System.lang.Array.toRange', args = [left.type, right.type])
    #print nativeName

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
    #print "Searching %s" % (name)
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

  def convertToASTType(self, obj):
    if isinstance(obj, ASTType):
      return obj
    elif isinstance(obj, ASTWord):
      return obj.type
    elif isinstance(obj, Value):
      return obj.type
    else:
      print obj
      raise NotImplementedError

  # 모든 type 정보는 ASTType을 사용하도록??
  def procOperator(self, tree):
    context = self.getLastContext()

    left = self.procExpr(tree.left)
    right = self.procExpr(tree.right)

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
      print left, tree, opName
      nativeName = encodeSymbolName(opName, args = [left.type])
      #print nativeName 
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
      symtbl = self.info['@symbols'][-1]
      if not symtbl.has_key(tree.value):
        raise Exception('Error', 'Unknown type : %s' % (tree.value))

      info = symtbl[tree.value]
      if isinstance(info, dict):
        if not info.has_key('@vtype'):
          print info
          raise Exception('Error', 'Error')
        
        info = info['@vtype']
      
      if isinstance(info, ASTType) == False:
        print info
        raise Exception('Error', 'Not ASTType')

      return Value(type = info, reg = self.machine.IUserReg(tree.value))
    else:
      print tree, type(tree)
      raise NotImplementedError

    return Value(type = tree.getType(), reg = tmpReg)
