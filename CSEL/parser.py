#!/usr/bin/env pythone
# -*- coding: utf-8 -*-
import traceback

from Token import *

from AST import *
from ASTAlias import *
from ASTDefArg import *
from ASTArgList import *
from ASTAttribute import *
from ASTTemplate import *
from ASTClass import *
from ASTDeclFunc import *
from ASTEmpty import *
from ASTExpr import *
from ASTExprs import *
from ASTFor import *
from ASTFuncCall import *
from ASTIf import *
from ASTListGenerateType1 import *
from ASTNames import *
from ASTNamespace import *
from ASTOperator import *
from ASTRankSpecs import *
from ASTSimpleExprs import *
from ASTTemplateList import *
from ASTType import *
from ASTRank import *
from ASTRankList import *
from ASTUse import *
from ASTVal import *
from ASTVar import *
from ASTWord import *
from ASTBlock import *
from ASTIndexing import *
from ASTSet import *
from ASTCase import *
from ASTCases import *
from ASTPatternMatch import *
from ASTTrue import *
from ASTFalse import *
from ASTReturn import *
from ASTWrap import *
from ASTUnary import *
from ASTTemplateArg import *
from ASTListValue import *
from ASTCalleeArgType1 import *
from ASTCalleeArgType2 import *
from SymbolTable import *
from IR import *
from mangle import *

import copy
import random
import re

sourceSets = []

def checkNamespaceGroup(name):
    if re.match(r'^((_|[a-zA-Z])[a-zA-Z0-9_]*\.)*\*$', name):
        return True
    
    return False

def mangling(name, args, extern = False):
    # name들은 무조건 C++기준으로, 단 extern이 있으면 C로 가정한다.
    if extern == True:
        return "_" + name
    
    return encodeSymbolName(name, args)

# <- 키워드에 대한 정의 (이건 library에서 하면될듯)
# 위 operator는 async한 assign이다.
# = 은 sync한 assign을 의미한다. 
# thread환경이 아니라면 '<-'은 '='과 동일하게 동작하지만
# thread환경일 경우는 '<-'은 synchronized한 동작을 한다(thread-safe)
# 하지만 '='은 no-thread-safe하게 동작한다. (2013.03.12)
class Parser:
  def __init__(self, fn, isdebug = 0):
    self.isdebug = isdebug # 0은 디버깅하지 않겠다는 의미

    self.basename = fn[:fn.rfind('.')]

    self.directive = []

    self.token = Token(fn)
    self.token.nextToken()

    # Root Symbol Table 등록
    symtbl = self.initSymbolTable()
    self.stackSymbolList = [symtbl]
    # function이나 class앞의 template이나 attribute같은 것들의 정보를 가지고 있는...
    self.directive = []
    
    # 아무것도 없으면 Root임
    self.pathList = []

    self.mustcompile = []

  def initSymbolTable(self):
    symtbl = SymbolTable()
    
    symtbl.registerNamespace(path = "System")
    symtbl.registerNamespace(path = "System.lang")
    symtbl.registerNamespace(path = "System.out")

    namespaceObject = "System.lang.Object"
    namespaceByte = "System.lang.Byte"
    namespaceChar = "System.lang.Char"
    namespaceShort = "System.lang.Short"
    namespaceInt = "System.lang.Integer"
    namespaceLong = "System.lang.Long"
    namespaceFloat = "System.lang.Float"
    namespaceDouble = "System.lang.Double"
    namespaceString = "System.lang.String"
    namespaceBoolean = "System.lang.Boolean"
    namespaceArray = "System.lang.Array"

    # System.lang.Object
    symtbl.registerClass(path = namespaceObject)

    symtbl.registerClass(path = namespaceByte)
    symtbl.registerClass(path = namespaceChar)
    symtbl.registerClass(path = namespaceShort)
    symtbl.registerClass(path = namespaceInt)
    symtbl.registerClass(path = namespaceLong)
    symtbl.registerClass(path = namespaceFloat)
    symtbl.registerClass(path = namespaceDouble)
    symtbl.registerClass(path = namespaceString)
    symtbl.registerClass(path = namespaceBoolean)
    symtbl.registerClass(path = namespaceArray)
    symtbl.registerNativeFunction(
        path = "System.lang.Array.length", 
        args = None, 
        retType = ASTType(name="System.lang.Integer", templ = None, ranks = None))
    symtbl.registerFunction(
        path = "System.lang.Array.toRange", 
        args = None, 
        retType = ASTType(name="System.lang.Array", templ = None, ranks = None))
    symtbl.registerFunction(
        path = "System.lang.Array.getNext",
        args = None, 
        retType = ASTType(name="System.lang.Integer", templ = None, ranks = None))
    symtbl.registerFunction(
        path = "System.lang.Array.end",
        args = None, 
        retType = ASTType(name="System.lang.Boolean", templ = None, ranks = None))
    symtbl.registerAliasSymbol("object", namespaceObject)
    symtbl.registerAliasSymbol("byte", namespaceByte)
    symtbl.registerAliasSymbol("short", namespaceShort)
    symtbl.registerAliasSymbol("int", namespaceInt)
    symtbl.registerAliasSymbol("float", namespaceFloat)
    symtbl.registerAliasSymbol("double", namespaceDouble)
    symtbl.registerAliasSymbol("string", namespaceString)
    symtbl.registerAliasSymbol('bool', namespaceBoolean)
    symtbl.registerAliasSymbol("String", namespaceString)

    symtbl.registerNativeFunction(
        path = 'System.out.println',
        args = None,
        retType = ASTType(name="void", templ = None, ranks = None))
 
    return symtbl

  def nextToken(self):
    self.token.nextToken()

  def match(self, word):
    return self.token.match(word)

  def same(self, word):
    return self.token.same(word)

  def matchType(self, word):
    return self.token.matchType(word)

  def sameType(self, word):
    return self.token.sameType(word)

  def isEnd(self):
    return self.token.reachEnd()

  def getTokValue(self):
    return self.token.tok.value

  def getTokType(self):
    return self.token.tok.type

  def getRootSymbolTable(self):
    return self.stackSymbolList[0]

  def getRecentSymbolTable(self):
    return self.stackSymbolList[-1]

  def searchSymbol(self, symbol):
    for elem in reversed(self.stackSymbolList):
      realname = elem.getRealname(symbol)
      if realname: return realname

    return None

  def searchNativeSymbol(self, native):
    for elem in reversed(self.stackSymbolList):
      if elem.has_key(native):
        return elem[native]

    return None
      
  # list에 따로 들어있는 각각의 namespace, class, function, template, struct, property등을 하나로 합칩니다.
  def flattenSymbolList(self):
    root = self.getRootSymbolTable()
    # 일단 구현할께 function밖에 없으니 ...

  def parse(self):
    if self.isdebug == 1:
      print "entering parse"

    root = self.getRootSymbolTable()
    
    parsingList = []
    while not self.isEnd():
      tree = None
      
      if self.same('namespace'):
        self.parseNamespace()
      elif self.same('class'):
        self.parseClass()
        raise Exception("parse", "class")
      elif self.same('template'):
        result = self.parseTemplate()
        self.directive.append(result)
      elif self.same('@'):
        result = self.parseAttribute()
        self.directive.append(result)
      elif self.same('def'):
        self.parseDef()
      elif self.same('native'):
        # 예는 push로..
        self.directive.append('native')
        pass
      else:
        break

    self.flattenSymbolList()

    if self.isdebug == 1:
      print "ending parse"
   
  def parseNamespace(self):
    if not self.match('namespace'):
      return 

    path = self.getNames()
    for name in path.split('.'):
      self.pathList.append(name)

    if self.match(';'):
      return

    self.parseNamespaceBody()

  def parseNamespaceBody(self):
    if not self.match('{'):
      return

    self.parse()

    self.match('}')

  def parseClass(self):
    if not self.match('class'):
      return 

    classname = self.makeFullPath(self.getNames())

    if self.match(';'):
      root = self.getRecentSymbolTable()
      root.registerSymbol(pathStr = classname, typeStr = "class")
      return 

    body = self.parseClassBody()

  def parseClassBody(self):
    if not self.match('{'):
      return

    # blahblah....

    self.match('}')
    
  def parseAttribute(self):
    if not self.match('@'):
      return 
  
    pass

  def parseTemplate(self):
    if not self.match('template'):
      return None

    sym = SymbolTable()
    self.stackSymbolList(sym)

    params = self.parseTemplateArguments()
    if params == None:
      print "Error) Needs some template parameters"
      return

    for param in params:
      sym.registerTemplateVariable(param.name, param.type)

    if self.same('class'):
      target = self.parseClass()
    elif self.same('def'):
      target = self.parseDef()

      root = self.getRootSymbolTable()
      root.registerTemplateFunction(params, target['name'], target['args'], target['rettype'], target['body'])
      # TODO : 그리고 먼가 파일로 만드는 코드 추가
    else:
      print "Error) Dont use template in this type"
      raise Exception("parseTemplate", "wrong type")

    self.pop()

    return ASTTemplate(params, target)

  def parseTemplateArguments(self):
    if not self.match('<'):
      return None

    # 선언할때는 function argument처럼
    args = [self.parseTemplateArgument()]
    while self.match(','):
      args.append(self.parseTemplateArgument())

    if not self.match('>'):
      return None

    return args

  def parseTemplateArgument(self):
    name = self.getName()
    type = "typename" # 일단 임시로
    if self.match(':'):
      type = self.getNames()
    return ASTTemplateArg(name, type)

  # 함수 선언 형태
  # def func(argname1: argtype1, argname2: argtype2, ...) = expr
  # def func(argname1: argtype1, argname2: argtype2, ...) { exprs }
  # def func(argname1: argtype1, argname2: argtype2, ...):rettype = expr
  # def func(argname1: argtype1, argname2: argtype2, ...):rettype { exprs }
  # 변수 선언 : (Scala처럼 구분하지 않는게 좋을듯)
  # def variableName; // 이럴 경우 정수형으로 가정
  # def variableName:variableType;
  # def variableName = <initial expr>;  // 이거랑 
  # def variableName:variableType = <initial expr>; // 이거는 함수취급
  def makeFullPath(self, fn):
    if len(self.pathList) == 0:
      return fn

    return ".".join(self.pathList + [fn])

  def parseDefBody(self):
    if self.isdebug == 1:
      print "entering parseDefBody"

    body = None
   
    if self.isdebug == 1:
      print "getTokValue : %s" % (self.getTokValue())
 
    if self.match('='):
      body = self.parseExpr()
    elif self.match('{'):
      body = self.parseExprs()
      self.match('}')

    if self.isdebug == 1:
      print "ending parseDefBody"
      
    return body
      
  def parseDef(self):
    if not self.match('def'):
      return None

    if self.isdebug == 1:
      print "entering parseDef"

    # 이름을 얻습니다.
    fn = self.makeFullPath(self.getNames())
    #print "Function name : %s" % (fn)

    # 함수용 symbol table을 만듭니다.
    parentSymTbl = self.getRecentSymbolTable()
    
    self.stackSymbolList.append(SymbolTable())
    localSymTbl = self.getRecentSymbolTable()

    # argument가 나오는지 검사합니다.
    args = self.parseDefArgsList()
    for elem in args:
      typeTree = elem.type
      #print "symbol = %s" % (typeTree.name)
      if self.searchSymbol(typeTree.name):
        localSymTbl.registerVariable(elem.name, typeTree)
      else:
        print "Not found symbol"
        sys.exit(-1)

    nativeSymbol = mangling(fn, args)
    if parentSymTbl.searchNative(nativeSymbol):
      print "Error: Duplicated Name"
      sys.exit(-1)
    #localSymTbl.printDoc()

    rettype = self.parseReturnType()
    body = self.parseDefBody()
    if body == None:
      print "function's body is empty : in %s" % (nativeSymbol)
      sys.exit(-1)
      
    if rettype != 'void':
      if isinstance(body, ASTExpr):
        body = ASTReturn(body)
      else:
        # return을 명시적으로 적지 않았다면, 마지막 expression의 결과를 return값으로 한다.
        lastExpr = body.exprs[-1]
        if not isinstance(lastExpr, ASTReturn):
          body.exprs[-1] = ASTReturn(lastExpr)

    for directive in self.directive:
      if directive == 'native':
        pass

    self.directive = []

    # 바로전에 template이 선언되었다면 여기도 영향을 받아야만 한다.
    # 일단 지금은 영향을 받지 않는다고 가정한다.
    parentSymTbl.registerFunction(path = fn, args = args, retType = rettype, body = body)

    self.mustcompile.append((parentSymTbl[nativeSymbol], nativeSymbol))

    if self.isdebug == 1:
      print "ending parseDef"

  def parseDefArgsList(self):
    if not self.match('('):
      return None

    args = []
    while not self.isEnd():
      arg = self.parseDefArg()
      if arg == None: break
      args.append(arg)
      if not self.match(','): break

    if not self.match(')'):
      print "Error) Need right parenthence"
      return None

    return args

  def parseReturnType(self):
    # if return type is none,
    if not self.match(':'):
      return ASTType(name = ASTNames("System.lang.Integer".split('.')), templ = None, ranks = None)

    return self.parseType()

  def parseDefArg(self):
    name = self.getName()
    if name == None: 
      return None

    typeStr = ASTType(name = ASTNames("System.lang.Integer".split('.')), templ = None, ranks = None)
    if self.match(':'): 
      typeStr = self.parseType()

    defval = None
    if self.match('='):
      defval = self.parseBasicSimpleExpr()

    # if typeStr == None: makeError
    return ASTDefArg(name = name, type = typeStr, defval = defval)

  def getName(self):
    if self.match('_'):
      return '_'
    
    return self.token.matchType('id')

  def getNames(self):
    names = []
    while not self.isEnd():
      names.append(self.getName())
      if not self.match('.'): break
    return ".".join(names)

  def parseTemplatePart(self):
    #raise Exception('parseTemplatePart', 'Not Implemented')
    return None

  def matchTemplateInfo(self, typeInfo, templateInfo):
    #raise Exception('matchTemplateInfo', 'Not Implemented')
    return True

  def parseType(self):
    if self.isdebug == 1:
      print "starting parseType"

    idStr = self.getNames()

    if self.isdebug == 1:
      print ".".join(idStr)

    # 해당 type이 존재하는지 검사합니다.
    whole = self.searchSymbol(idStr)
    if not whole:
      print "Unknown Type : %s" % (idStr)
      sys.exit(-1)

    #tmpl = self.parseTemplatePart()
    #if not self.matchTemplateInfo(result, tmpl):
    #  # 일단 현재는 pass
    #  print "Error) Not matched template information"
    #  pass

    #print "type's full name = %s" % (idStr)

    #tmpl  = self.parseTemplatePart()
    #ename, body = symbolTable.search(names.array)
    #if ename == None:
    #  print "doesn't exist symbol : %s" % (".".join(names.array))
    #  sys.exit(-1) # 일단 죽이고... 나중에 에러처리 생각
    #else:
    #  names.array = ename

    rank  = self.parseRankList()
 
    if self.isdebug == 1:
      print "ending parseType"

    return ASTType(name = whole, templ = None, ranks = rank)

  def parseRankList(self):
    lst = []
    while self.match('['):
      rank = ASTRank(self.parseSimpleExpr())
      lst.append(rank)
      if not self.match(']'):
        print "Error) Need ']'"
    
    return ASTRankList(lst)

  def parseExprs(self):
    lst = []
    while not self.isEnd():
      ret = self.parseExpr()
      if ret == None: break
      if isinstance(ret, ASTExprs):
        lst += ret.exprs
      else:
        lst.append(ret)

    if len(lst) == 0: return None

    return ASTExprs(lst)

  def parseExpr(self):
    ret = None

    if self.same('if'):
      ret = self.parseIfStmt()
    elif self.same('for'):
      ret = self.parseForStmt()
    elif self.same('var'):
      #print "calling var"
      ret = self.parseVar()
    elif self.same('val'):
      ret = self.parseVal()
    elif self.same('{'):
      ret = self.parseBlockExprs()
    else:
      ret = self.parseSimpleExpr1()
      self.match(';')

    return ret

  def parseIfStmt(self):
    if not self.match('if'):
      return None

    cond = self.parseExpr()
    self.match(':')
    body = self.parseExpr()
    return ASTIf(cond, body)

  def parseForStmt(self):
    if not self.match('for'):
      return None

    cond = self.parseSimpleExpr()
    self.match(':')
    body = self.parseExpr()
    return ASTFor(cond, body)

  def parseVar(self):
    if not self.match('var'):
      return None

    sym = self.getRecentSymbolTable()
    
    hist = []
    while True:
      name = self.getName()
      if sym.has_key(name):
        print "has duplicated name"
        return None

      type = None
      if self.match(':'):
        type = self.parseType()
      else:
        type = ASTType(name = 'System.lang.Integer', templ = None, ranks = None)

      #print "name =", name

      # 변수 초기화
      init = None
      if self.match('='):
        tree = ASTOperator(ASTWord('id', '='), ASTWord('id', name), self.parseSimpleExpr())
        hist.append(tree)

      sym.registerVariable(name, type)
      if not self.match(','):
        break

    self.match(';')

    return ASTExprs(hist)

  def parseVal(self):
    return None

  def parseBlockExprs(self):
    return None

  def parseSimpleExpr1(self):
    ret = self.parseSimpleExprs()
    # not yet!
    #if self.match('?'):
    #  body = self.parseMatchingCases()
    #  ret  = ASTPatternMatch(cond = ret, body = body)
    return ret

  def parseSimpleExprs(self):
    history = []
    while not self.isEnd():
      tree = self.parseSimpleExpr()
      if tree == None: break
      if self.match(','):
        hist = [tree]
        while self.match(','):
          tree = self.parseSimpleExpr()
          hist.append(tree)
        tree = ASTSet(hist)

      history.append(tree)

    if len(history) == 0: return None
    #self.match(';') # caution!!
    return ASTSimpleExprs(history)

  def parseSimpleExpr(self):
    if self.isdebug == 1:
      print "entering parseSimpleExpr()"

    tree = self.parseBasicSimpleExpr()
    if tree == None: return None
    while not self.isEnd():
      if self.isdebug == 1:
        print self.getTokValue()

      if self.match('.'):
        right = self.parseBasicSimpleExpr()
        if isinstance(tree, ASTWord):
          if isinstance(right, ASTWord):
            tree = ASTNames([tree.value, right.value])
          elif isinstance(right, ASTFuncCall):
            tree = ASTFuncCall(ASTNames([tree.value, right.name.value]), right.body)
          elif isinstance(right, ASTIndexing):
            tree = ASTIndexing(ASTNames([tree.value, right.name.value]), right.history)
        elif isinstance(tree, ASTNames):
          if isinstance(right, ASTWord):
            tree = ASTNames(tree.array + [right.value])
          elif isinstance(right, ASTFuncCall):
            tree = ASTFuncCall(ASTNames(tree.array + [right.name.value]), right.args)
          elif isinstance(right, ASTIndexing):
            tree = ASTIndexing(ASTNames(tree.array + [right.name.value]), right.history)
        else:
          tok = self.token.tok
          tree = ASTOperator(ASTWord(tok.type, tok.value), tree, right)
      # array
      elif self.sameType('id'):
        #if isinstance(tree, ASTSet):
        #  #if len(tree.lst) != 1:
        #  #  print "error!!" # make error!!
        #  if self.check_type(tree.lst[0]):
        #    tree = ASTCasting(tree.lst[0], ASTWord(tok.type, tok.value))
        tokVal = self.getTokValue()
        tokType = self.getTokType()

        mid = ASTWord(tokType, tokVal)

        self.token.nextToken()

        right = self.parseBasicSimpleExpr()
        if right != None:
          tree = ASTOperator(mid, tree, right)
        else:
          # for example, 'a++' or 'a+'
          tree = ASTUnary(tree, mid)
      else:
        break

    if isinstance(tree, ASTFuncCall):
      candidates = set([])      

      array = tree.name.array
      path = ".".join(array[:-1])
      name = array[-1]
 
      for symtbl in reversed(self.stackSymbolList):
        lst = symtbl.findFunction(path, name, tree.args)  
        if lst == None:
          continue
        candidates |= set(lst)
     
      ncandidates = len(candidates) 
      if ncandidates == 0:
        print "Error) Not exist symbol : %s" % (".".join(array))
        sys.exit(-1)
      elif ncandidates != 1:
        print "Error) Two more symbols : %s" % (".".join(array))
        sys.exit(-1)
      else:
        # exists symbol
        pass

    if self.isdebug == 1:
      print "ending parseSimpleExpr()"

    return tree

  def parseBasicSimpleExpr(self):
    tok = self.token.tok
    if tok == None: return None
    #print "calling parseBasicSimpleExpr"
    #print "value =", tok.value, tok.type
    if self.matchType('stringLiteral'): 
      return ASTWord('System.lang.String', tok.value)
    elif self.matchType('integerLiteral'):
      return ASTWord('System.lang.Integer', tok.value)
    elif self.matchType('floatLiteral'):
      return ASTWord('System.lang.Float', tok.value)
    elif self.match('true'):
      return ASTWord('System.lang.Boolean', '1')
    elif self.match('false'):
      return ASTWord('System.lang.Boolean', '0')
    elif self.match('return'):
      return ASTReturn(self.parseExpr())
    #elif self.match('def'):
    #  ret = self.parseDefInnerFunc()

      #if len(ret.name) != 1:
      #  print "don't use namespace!"
      #  sys.exit(-1)

      #realname = ret.name[0]
      #if realname == '_':
      #  realname = self.genTemporaryName()  
      #if self.findAt(tbl = self.local_symtbl, target = ret.name):
      #  print "already defined!"
      #  sys.exit(-1)

      #typename = convertType(ret.ret)
      #if not self.validateType(typename):
      #  print "not declare type"
      #  sys.exit(-1)
      
      #self.local_symtbl[realname] = {
      #  "attribute": ["lambda"], 
      #  "args": ret.args, 
      #  "type": typename, 
      #  "body": ret.body}

      #return ret
    elif self.matchType('id'): 
      if self.same('['):
        history = []
        while self.match('['):
          history.append(self.parseSimpleExpr())
          self.match(']')
        return ASTIndexing(ASTWord(tok.type, tok.value), history)
      elif self.match('('):
        # TODO 함수의 그것인지 아닌지에 대한 구분이 필요하다.
        args = self.parseDefArgListForFuncCall()

        if not self.match(')'):
          print "Error) Need ')'"

        # TODO: 호출하려는 function에 대한 정보를 얻어서 입력된 argument들의 type과 비교하여,
        # 현재 symbol table에 호출할 수 있는 function이 있는지를 찾는 코드가 있어야 한다.
        # 몇번의 try가 필요할지도...(auto casting때문에...)
        # 예를 들어, 호출하려는 함수의 인자중에 char*를 갖는데, 해당 함수의 인자에는 char*를 사용하지 않고 System.lang.String만 사용하는 경우는
        # 자동으로 char*를 String으로 auto casting해주어야 한다.
        # 그 반대의 경우는 String을 char*로 casting해주어야 한다.
        # 단, 해당 class에 해당 변환을 지원해준다는 가정이 필요하다.(즉, 해당 casting을 지원해주는지 여부를 체크해야만 한다.)
        # 알고리즘
        # 1. 현재의 argument들의 type들로 구성된 function을 찾는다.
        # 2. 만일 없다면, argument들의 갯수가 동일한 함수.... (이건 내일 생각)
        return ASTFuncCall(ASTWord(tok.type, tok.value), args)
      elif self.match('...'):
        right = self.parseSimpleExpr()
        return ASTListGenerateType1(ASTWord(tok.type, tok.value), right)
      elif self.match('='):
        right = self.parseSimpleExpr()
        return ASTCalleeArgType2(ASTWord(tok.type, tok.value), right)
      else:
        return ASTWord(tok.type, tok.value)
    elif self.match('_'):
      return ASTWord('v', tok.value)
    elif self.match('['):
      history = []
      tree = self.parseSimpleExpr()
      if self.match('...'):
        right = self.parseSimpleExpr()
        self.match(']')
        return ASTListGenerateType1(tree, right)
      elif self.match(','):
        history.append(tree)
        while self.match(','):
          item = self.parseSimpleExpr()
          history.append(item)
        self.match(']')
        return ASTListValue(history)
       
      self.match(']')
      return ASTListValue([tree])
    elif self.match('('):
      tree = self.parseSimpleExpr1()
      self.match(')')
      return ASTWrap(tree)
    #else:
    #  print tok
    #  raise Exception("parseBasicSimpleExpr", "Not implemented")

    return None

  def parseDefArgListForFuncCall(self):
    args = []

    arg = self.parseSimpleExpr()
    args.append(ASTCalleeArgType1(arg))
    while self.match(','):
      arg = self.parseSimpleExpr()
      args.append(ASTCalleeArgType1(arg))

    return args
