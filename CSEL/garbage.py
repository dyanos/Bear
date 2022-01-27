# -*- coding: cp949 -*-
import os,sys,string

def convertIntToHex(value):
  string = str(value)
  if string[:2] == '0x':
    return hex(int(string[2:], 16))
  elif string[0] == '0':
    try:
      return hex(int(string, 8))
    except:
      return hex(int(string))
  else:
    return hex(int(string))

  return None

def convertFloatToHex(value):
  string = str(value)
  return None

# �Ʒ� �ڵ�� ������ ������  
class Transformation:
  def __init__(self, symtbl):
    self.symtbl = symtbl
    self.arg_symtbl   = {}
    self.local_symtbl = {}
    self.local_constant_symtbl = {}
    self.stringtbl    = []

  def convert(self):
    for key in self.symtbl:
      ast = self.symtbl[key]
      if isinstance(ast, ASTDeclFunc):
        # local ���� Stack �ʿ�.
        continue
      elif isinstance(ast, ASTDefVar):
        continue
      elif isinstance(ast, ASTDefVal):
        continue

  # search the symbol and return type of it.
  def searchSymbolTable(self, name):
    if name in self.arg_symtbl:
      return self.arg_symtbl[name]
    elif name in self.local_symtbl:
      return self.local_symtbl[name]
    elif name in self.local_constant_symtbl:
      return self.local_constant_symtbl[name]

    return None

  def processExpr(self):
    now = self.now
    if isinstance(now, ASTOperator):
      left  = self.transform(now.left)
      right = self.transform(now.right)
      # to construct
    if isinstance(now, ASTWord):
      if now.type == 'integerLiteral':
        convstr = convertIntToHex(now.value)
        typestr = ""
        if len(convstr) <= 2:
          typestr = "integer2"
        elif len(convstr) <= 4:
          typestr = "integer4"
        elif len(convstr) <= 8:
          typestr = "integer8"
        elif len(convstr) <= 16:
          typestr = "integer16"
        else:
          typestr = "number"

        return {"type": typestr, "value": convstr}
      elif now.type == 'floatLiteral':
        convstr = convertFloatToHex(now.value)
        return {"type": "float8", "value": convstr}
      elif now.type == 'stringLiteral':
        index = len(self.stringtbl)
        self.stringtbl.append(now.value)
        return {"type": "string", "index": index}
      elif now.type == 'id':
        regnum = len(self.symboltbl)
        # �����̸� register, ũ�Ⱑ �ִٸ� start address�� register
        type   = self.searchSymbol(now.value)
        if self.isBasicType(type):
          return {"type": type, "register-num": regnum}
        else:
          return {"type": type, "register-num": regnum, "extendtype": "indrect"}
      else:
        print("I don't know how the ASTWord(%s) convert" % (now.name))
      return None
    elif isinstance(now, ASTVar):
      if self.searchSymbol(now.name) == None:
        print("duplicate symbol")
      self.local_symtbl[now.name] = convertType(now.type)
      ret = self.parseExpr(now.init)
    elif isinstance(now, ASTVal):
      if self.searchSymbol(now.name) == None:
        print("duplicate symbol")
      self.local_constant_symtbl[now.name] = now.type
      ret = self.parseExpr(now.init)

parser = Parser("sample.prg")
parser.parse()
#print parser.symbol_dict.hierarchy
#for key in parser.symbol_dict.hierarchy:
#  print key

def makeSymbolName(cname, fname, args):
  #print("debug) %s, %s" % (cname, fname))

  name = [cname, str(len(fname)), fname, convertType(args)]
  #print("debug) full : %s" % ("".join(name)))
  return "".join(name)

class Register:
  MODE_NONE = 0
  MODE_REG  = 1
  MODE_IMM  = 2
  # addressing mode
  MODE_ADDR = 3 

  def __init__(self, type, regid = None, base = None, index = None, imm = None):
    self.type  = type
    self.regid = regid
    self.base  = base
    self.index = index
    self.imm   = imm

  def __str__(self):
    if self.type == Register.MODE_IMM:
      return "%08x" % (self.imm)
    elif self.type == MODE_REG:
      if self.regid == REG_RAX:
        return "rax"
      elif self.regid == REG_EAX:
        return "eax"
      elif self.regid == REG_AX:
        return "ax"
      elif self.regid == REG_AH:
        return "al"
      elif self.regid == REG_AL:
        return "ah"

def genRandomString(length):
  chars  = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_$#@~.?"
  locs   = [random.uniform(0, len(chars)) for i in range(0, length)]
  if locs[0] > chars.index('Z'):
    locs[0] = random.uniform(0, chars.index('Z'))
  return [chars[loc] for loc in locs]

class Configure:
  def __init__(self):
    pass

  def getLengthOfTemporaryVariable():
    return 16

def convertDoubleToHex(value):
  return 0

def convertFloatToHex(value):
  return 0

def convertIntToHex(value):
  if isinstance(value, str):
    return int(value)
  elif isinstance(value, int):
    return value

  return None

class IRegister:
  def __init__(self, name):
    self.name = name

  def __str__(self):
    return "%s" % (self.name)

class ILabel:
  def __init__(self, label):
    self.label = label

  def __str__(self):
    return "%s" % (self.label)

class IPointer:
  def __init__(self, pointer):
    self.value = pointer

  def __str__(self):
    return "0x%x" % (self.value)

class IImmediate:
  def __init__(self, _value):
    self.value = _value

  def __str__(self):
    return "0x%x" % (self.value)

class IFloat:
  def __init__(self, _value):
    self.value = _value

  def __str__(self):
    #return "%g" % (convertHexToFloat(self.value))
    return "0x%x" % (self.value)

class IDouble:
  def __init__(self, _value):
    self.value = _value

  def __str__(self):
    #return "%g" % (convertHexToFloat(self.value))
    return "0x%x" % (self.value)

class IMemoryAddress:
  def __init__(self, base, idx = None, imm = 0):
    self.basereg = base
    self.idxreg  = idx
    self.imm     = imm

  def __str__(self):
    code  = "%s" % (self.basereg)
    if self.idxreg != None:
      code += "+%s" % (self.idxreg)
    if self.imm    != 0:
      code += "+%d" % (self.imm)

    return "[%s]" % (code)

REG_RAX = IRegister("rax")
REG_RBX = IRegister("rbx")
REG_RCX = IRegister("rcx")
REG_RDX = IRegister("rdx")
REG_RSI = IRegister("rsi")
REG_RDI = IRegister("rdi")
REG_RBP = IRegister("rbp")
REG_RSP = IRegister("rsp")
REG_R8  = IRegister("r8")
REG_R9  = IRegister("r9")
REG_R10 = IRegister("r10")
REG_R11 = IRegister("r11")
REG_R12 = IRegister("r12")
REG_R13 = IRegister("r13")
REG_R14 = IRegister("r14")
REG_R15 = IRegister("r15")

class IR:
  def __init__(self):
    self.code    = []
    self.data    = {}
    self.stack   = []

  def emitClear(self, left):
    self.code.append("xor %s, %s" % (left, left))

  def emitMove(self, left, right):
    strcmd = "mov %s, %s" % (left, right)
    self.code.append(strcmd)

  def emitPush(self, left):
    self.code.append("push %s" % (left))

  def emitPop(self, left):
    self.code.append("pop %s" % (left))

  def emitAdd(self, rd, rn, rs):
    pass

  def emitAdd(self, left, right):
    self.code.append("add %s, %s" % (left, right))

  def emitSub(self, left, right):
    self.code.append("sub %s, %s" % (left, right))

  def emitMul(self, left, right):
    self.code.append("mul %s, %s" % (left, right))

  def emitDiv(self, left, right):
    self.code.append("div %s, %s" % (left, right))

  def emitCall(self, name, **kw):
    for (key, item) in list(kw.items()):
      pass
  
    self.emitClear(REG_RAX)
    self.code.append("call %s" % (name))

  def searchFunctionInClass(self, BaseName, OperatorName):
    fpath = mergeName(BaseName, changeIntoReal(OperatorName))
    if fpath not in self.symtbl:
      return None

    return fpath

  def searchConstructorInClass(self, BaseName, RightType):
    pattern = "".join([BaseName, "Ec"])
    for (key, value) in list(self.symtbl.items()):
      if re.match(pattern, key):
        return key
    
    return None

  def evalOperator(self, tree):
    self.eval(tree.left)
    self.eval(tree.right)
    
    l_classname, ltypestr = getTypeOf(lsubtree)
    ret = searchFunctionInClass(ltypestr, tree.name)
    if ret == None:
      print("Error) Operator Not Found! : %s" % (tree.name))
      sys.exit(-1)

    r_classname, rtypestr  = getTypeOf(rsubtree)
    if ltypestr != rtypestr:
      result = searchConstructorInClass(ltypestr, rtypestr)
      if result == None:
        print("Error) Don't know how to convert %s to %s" % (demangleName(rtypestr), demangleName(ltypestr)))
        sys.exit(-1)

      
      emitCall(result[0], arg1 = rsubtree.space)

    emitCall(ret, arg1 = lsubtree.space, arg2 = rsubtree.space)

  def evalTerminalToken(self, tree):
    realName = convertName(tree.type)
    if tree.type == 'System.lang.String':
      label = genRandomString(16)
      self.data[label] = {"type": realName, "value": tree.value}
      self.stack.append(ILabel(label))
    elif tree.type == 'System.lang.Int':
      self.stack.append(IImmediate(convertIntToHex(tree.value)))
    elif tree.type == 'System.lang.Float':
      #label = genRandomString(16)
      #realName = convertName('System.lang.Float')
      self.stack.append(IFloat(convertFloatToHex(tree.value)))
    elif tree.type == 'System.lang.Double':
      #label = genRandomString(16)
      #realName = convertName('System.lang.Double')
      #self.data[label] = {"type": realName, 
      #                    "value": convertDoubleToHex(tree.value)}
      #return (label, self.data[label])
      self.stack.append(IDouble(convertDoubleToHex(tree.value)))
    elif tree.type == 'System.lang.Boolean':
      pass

  def eval(self, tree):
    if isinstance(tree, ASTWord):
      ret = self.evalTerminalToken(tree)

    pass

class IR2:
  def __init__(self):
    self.content = []
    self.random  = Random()
    self.info    = {}

  def getType(self, node):
    #print("getType = ", node)
    if node is ASTWord:
      type = None
      if node.type is str:
        type = node.type.split('.')
      else:
        # not yet
        type = node.array

      return convertName(type)
    elif node is ASTNames:
      return convertName(self.array)
    else:
      print("Error in getType")

  def searchFuncInClass(self, cname, fname, args):
    symbol = makeSymbolName(cname, fname, args)
    ret    = symbol_dict.search(symbol)
    if ret == None: return False
    return True

  def findSymbolType(self, tree):
    # to find in arguments
    arguments = self.info['@arguments']
    if tree in arguments:
      return arguments[tree]
    return self.getType(tree)

  def genRandomVariable(self, rettype):
    basestr = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"
    name = "__" + "".join([basestr[self.random.randrange(0, len(basestr))] for i in range(0, 10)])
    return {'@name': name,
            '@type': rettype,
            '@representation': 'identifier'}

  def evalFunc(self, tree):
    if not isinstance(tree, ASTDeclFunc):
      info = {'@argument_symbols': {}}

      args = tree.info['@arguments']
      for var_name in args:
        info['@argument_symbols'][var_name] = args[var_name]

      print("argument = ", info['@argument_symbols'])
      sys.exit(-1)
    else:
      raise NotImplemented

  def eval(self, tree):
    innerSymbolTbl = {}
    while True:
      #print(tree)
      if isinstance(tree, ASTDeclFunc):
        self.evalFunc(tree)
      elif isinstance(tree, ASTWord):
        if tree.type == 'id':
          # find at symbol table of function
          ret = None
          type = self.findSymbolType(tree.value)
          return {"@name": tree.value, 
                  "@type": convertName(type), 
                  "@representation": 'identifier'}
        else:
          return {"@name": tree.value, 
                  "@type": convertName(tree.type.split('.')),
                  "@representation": 'value'}
      elif isinstance(tree, ASTExprs):
        for subtree in tree.exprs:
          self.eval(subtree)
      elif isinstance(tree, ASTExpr):
        self.eval(tree.expr)
      elif isinstance(tree, ASTSimpleExprs):
        for expr in tree.exprs:
          self.eval(expr)
      elif isinstance(tree, ASTOperator):
        ltype = self.eval(tree.left)
        rtype = self.eval(tree.right)

        func  = self.searchFuncInClass(cname = ltype['@type'], fname = tree.name, args = [rtype['@type']])
        if func == None:
          # if fname is None, fname will be the class name.
          casting_func = self.searchFuncInClass(cname = ltype['@type'], fname = None, args = [rtype['@type']])
          if casting_func == None:
            print("Compiler doesn't know how to convert %s into %s" % (recoverName(ltype), recoverName(rtype)))
            sys.exit(-1)

          tmpval = self.genRandomVariable(casting_func['@return'])
          IR.emitCall(casting_func['@name'], args = [rtype['@name']], retval = tmpval['@name'])
          rtype  = tmpval
          
          func   = self.searchFuncInClass(cname = ltype['@type'], fname = tree.name, args = [rtype['@type']])
        
        tmpval = self.genRandomVariable(func['@return'])
        IR.emitCall(func['@name'], args = [ltype['@name'], rtype['@name']], retval = tmpval['@name'])

        return tmpval
      else:
        if '@type' not in tree:
          print(tree)
          break

        if tree['@type'] == 'function':
          info = {'@arguments': {}}

          for name in tree['@arguments']:
            info['@arguments'][name] = convertType(tree['@arguments'][name])

          info['@return'] = convertType(tree['@rettype'])

          #print("arguments = ", info['@arguments'])
          #print("return    = ", info['@return'])

          self.info = info

          self.eval(tree['@body'])
        else:
          break

ir = IR()
ir.eval(symbol_dict.hierarchy['add'])
