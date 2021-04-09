#!/usr/bin/env pythone
# -*- coding: utf-8 -*-
import traceback

from .Token import *

from .AST import *
from .ASTAlias import *
from .ASTDefArg import *
from .ASTArgList import *
from .ASTAttribute import *
from .ASTTemplate import *
from .ASTClass import *
from .ASTDeclFunc import *
from .ASTEmpty import *
from .ASTExpr import *
from .ASTExprs import *
from .ASTFor import *
from .ASTFuncCall import *
from .ASTIf import *
from .ASTListGenerateType1 import *
from .ASTNames import *
from .ASTNamespace import *
from .ASTBinOperator import *
from .ASTRankSpecs import *
from .ASTSimpleExprs import *
from .ASTTemplateList import *
from .ASTType import *
from .ASTRank import *
from .ASTRankList import *
from .ASTUse import *
from .ASTUnit import *
from .ASTVal import *
from .ASTVar import *
from .ASTWord import *
from .ASTBlock import *
from .ASTIndexing import *
from .ASTSet import *
from .ASTCase import *
from .ASTCases import *
from .ASTPatternMatch import *
from .ASTTrue import *
from .ASTFalse import *
from .ASTReturn import *
from .ASTWrap import *
from .ASTUnary import *
from .ASTTemplateArg import *
from .ASTListValue import *
from .ASTCalleeArgType1 import *
from .ASTCalleeArgType2 import *
from .ASTNativeAdd import *
from .ASTNativeMove import *

from .SymbolTable import *
from .TypeTable import TypeTable
from .IR import *
from .mangle import *

import copy
import random
import re

sourceSets = []


def checkNamespaceGroup(name):
  if re.match(r'^((_|[a-zA-Z])[a-zA-Z0-9_]*\.)*\*$', name):
    return True

  return False

def mangling(name, args, rettype=None, extern=False):
  # name들은 무조건 C++기준으로, 단 extern이 있으면 C로 가정한다.
  if extern == True:
    return "_" + name

  return encodeSymbolName(name, args)

def internalMangling(name, args):
  return encodeSymbolName(name, args)

class ClassSuccessionInfo:
  PUBLIC = 1
  PROTECTED = 2
  PRIVATE = 3

  def __init__(self, path, type):
    self.path = path
    self.type = type

class SyntaxError(Exception):
  def __init__(self):
    pass

class Library:
  def __init__(self, libraryPaths):
    self.libraryPaths = libraryPaths
    self.getLibraryPaths()

  def getLibraryPaths(self):
    import os
    import glob

    libraries = []
    for p in libraryPaths:
      temp = glob.glob(os.paths.join(p, "*"))
      libraries.extends(temp)

    self.library_paths = libraries

  def loadSymbolFrom(self, path):
    # 모든 symbol들은 System.lang.Object형태로 변경된 후 다루어진다.

    # 1. 상위이름으로 매칭되는 파일명 찾기 : 예를 들어, System.lang.Object를 찾는다면, System.lang.Object.dll을 찾으면 됨
    # 2. 찾은게 있다면, 해당 library파일을 읽어서 거기에 있는 symbol들을 몽땅다 읽기
    # 3. demangling하기
    # 4. 그걸 적당한 class로 감싸서 돌려주기
    pass

# <- 키워드에 대한 정의 (이건 library에서 하면될듯)
# 위 operator는 async한 assign이다.
# = 은 sync한 assign을 의미한다. 
# thread환경이 아니라면 '<-'은 '='과 동일하게 동작하지만
# thread환경일 경우는 '<-'은 synchronized한 동작을 한다(thread-safe)
# 하지만 '='은 no-thread-safe하게 동작한다. (2013.03.12)
class Parser:
  def __init__(self, fn, isdebug=False):
    self.isdebug = isdebug  # 0은 디버깅하지 않겠다는 의미

    self.basename = fn[:fn.rfind('.')]

    self.directive = []

    self.token = Token(fn)
    self.token.nextToken()

    # Root Symbol Table 등록
    self.importSymbolTable = {}
    self.globalSymbolTable = SymbolTable()
    self.localSymbolTable = []

    self.typeTable = TypeTable()

    # function이나 class앞의 template이나 attribute같은 것들의 정보를 가지고 있는...
    self.directive = []

    # 아무것도 없으면 Root임
    self.namespaceStack = []
    self.loadedSymbolList = []

    self.mustcompile = []

  def initSymbolTable(self):
    symTbl = SymbolTable()
    typeTbl = TypeTable()

    return symTbl

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

  def getName(self):
    if self.match('_'):
      return ASTUnit()

    return self.token.matchType('id')

  def getNames(self):
    names = []
    while not self.isEnd():
      names.append(self.getName())
      if not self.match('.'): 
        break

    return ".".join(names)

  def parse(self):
    if self.isdebug:
      print("entering parse")

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
      elif self.same('import'):
        self.parseImport()
      else:
        break

    if self.isdebug:
      print("ending parse")

  def parseImport(self):
    path = self.getImportNames()
    alias = None
    if self.match('as'):
      alias = self.getName()

    # TODO: 실제 해당 namespace 또는 class가 있는지 체크한다.
    symbols = loadSymbolFrom(path)
    matched = symbols.find(path)
    for symbol in matched:
      self.globalSymbolTable.register(symbol)

  def getImportNames(self):
    names = []
    while not self.isEnd():
      names.append(self.getName())
      if not self.match('.'): 
        break

    return ".".join(names)

  def parseNamespace(self):
    if not self.match('namespace'):
      return

    path = self.getNames()

    self.namespaceStack.append(path)
    self.parseNamespaceBody()
    name = ".".join(self.namespaceStack)
    self.globalSymbolTable.registerNamespace(name) # TODO: 수정필요
    self.namespaceStack.pop()  # symbol search할때도 사용할예정

  def getWorkingPath(self):
    return ".".join(self.namespaceStack)

  def parseNamespaceBody(self):
    if not self.match('{'):
      return

    self.parse()

    self.match('}')

  def parseClass(self):
    if not self.match('class'):
      return

    names = self.getNames()

    # 검색 symbol list에 등록만 해놓는다.
    # 정의가 안되어 있다가 나중에 사용되면 실제 symbol table에 body가 없으므로,
    # body가 없다고 에러를 내면 된다.
    # self.loadedSymbolList와 self.namespaceStack은 단지 symbol을 만들때와 symbol참조를 위해서만 쓰인다.
    # TODO: System.lang.Object는 기본 상속, public인지, private인지, trait인지등에 대한 정보 추가 필요
    parents = [ClassSuccessionInfo("System.lang.Object", ClassSuccessionInfo.PUBLIC)]
    if self.match(':'): # 상속이 있다면...
      # TODO: 상속과 관련된 코드 필요
      pass

    if self.match(';'):
      self.namespaceStack.append(names)
      self.globalSymbolTable.registerClass(".".join(self.namespaceStack), parents) # TODO: 상속등의 class정보도 주어져야...
      self.namespaceStack.pop()
      return

    self.namespaceStack.append(names)
    self.parseClassBody()
    self.globalSymbolTable.registerClass(".".join(self.namespaceStack), parents) # TODO: Body는 어딘가에 등록이 되어야 할 듯?
    self.namespaceStack.pop()

  def parseClassBody(self):
    if not self.match('{'):
      return

    body = {}
    while not self.match('}'):
      if self.match('val'):  # 상수선언
        name = self.getName()
        if name in body:
          print("Error) duplicated name :", name)
          raise NameError

        type = "System.lang.Int"
        if self.match(':'):
          type = self.parseType()

        if self.match('='):
          body = self.parseInitExpr()

        self.namespaceStack.append(name)
        self.globalSymbolTable.registerValue(name, type, body)
        self.namespaceStack.pop()
      elif self.match('var'):  # 변수선언
        name = self.getName()
        if name in body:
          print("Error) duplicated name :", name)
          raise NameError

        if self.match(':'):
          type = self.parseType()

        if self.match('='):
          body = self.parseInitExpr()

        self.namespaceStack.append(name)
        self.globalSymbolTable.registerVariable(name, type, body)
        self.namespaceStack.pop()
      elif self.match('def'):  # 함수
        if 'native' in self.directive:
          is_native = True

        name = self.getName()

        # 인자까지 봐야지 중복인지를 체크할 수 있음
        if self.match('('):
          args = self.parseDefArgsList()
          if not self.match(')'):
            print("Error) Needed ')'")
            raise SyntaxError

        if self.match(':'):  # return type
          type = self.parseType()
        else:
          type = ASTUnit()

        body = None
        if self.match('='):
          body = self.parseExpr()
        elif self.match('{'):
          body = self.parseExprs()
          if not self.match('}'):
            print("Error) Needed '}'")
            raise SyntaxError

        if is_native and body:
          print("Error) native function doesn't need body")
          raise SyntaxError

        if not is_native and not body:
          print("Error) need function body")
          raise SyntaxError

        self.namespaceStack.append(name)
        self.globalSymbolTable.registerFunc(name, args, rettype, body)
        self.namespaceStack.pop()

  def parseInitExpr(self):
    # 여긴 상수나 간단한 계산하는 루틴정도?
    # 아님 배열

    raise NotImplementedError

  def parseAttribute(self):
    if not self.match('@'):
      return

    pass

  def parseTemplate(self):
    if not self.match('template'):
      return None

    params = self.parseTemplateArguments()
    if params == None:
      print("Error) Needs some template parameters")
      return

    for param in params:
      sym.registerTemplateVariable(param.name, param.type)

    if self.same('class'):
      target = self.parseClass()
    elif self.same('def'):
      target = self.parseDef()

      self.globalSymbolTable.register({
        "@type": 'template def',
        "@name": target['name'],
        "@vtype": target['rettype'],
        "@body": target['body'],
        "@template args": params})
      # TODO : 그리고 먼가 파일로 만드는 코드 추가
    else:
      print("Error) Dont use template in this type")
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
    type = "typename"  # 일단 임시로
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
    return ".".join(self.namespaceStack + [fn])

  def parseDefBody(self):
    if self.isdebug:
      print("entering parseDefBody")

    body = None

    if self.isdebug:
      print("getTokValue : %s" % (self.getTokValue()))

    if self.match('='):
      body = self.parseExpr()
    elif self.match('{'):
      body = self.parseExprs()
      self.match('}')

    if self.isdebug:
      print("ending parseDefBody")

    return body

  def parseFuncName(self):
    tmp = self.token.matchType('id')
    # template!!
    if self.same('['):
      typeName = self.parseTemplateName()
      
  def parseDef(self):
    if not self.match('def'):
      return None

    if self.isdebug:
      print("entering parseDef")

    # 이름을 얻습니다.
    funcname = self.getNames()

    # print "Function name : %s" % (fn)

    # 함수용 local symbol table을 만듭니다.
    self.localSymbolTable = {}

    # argument가 나오는지 검사합니다.
    args = self.parseDefArgsList()

    # check
    for arg in args:
      if arg.name in self.localSymbolTable:
        print("Error) Duplicated Name")
        raise SyntaxError

      if not self.globalSymbolTable.find(arg.type.name):
        print("Error) Unknown Type")
        raise SyntaxError

      self.localSymbolTable[arg.name] = arg.type

    nativeFuncname = internalMangling(funcname, args)
    fn = ".".join(self.namespaceStack + [nativeFuncname])
    # global symbol table에서 체크 : 인자 다양성 부분에 대한 고려가 필요
    if self.globalSymbolTable.find(fn):
      name = ".".join(self.namespaceStack + [funcname])
      print(f"Error) Already defined : {name}")
      raise SyntaxError

    # To parse return type
    rettype = self.parseReturnType()

    # To parse body of function
    body = self.parseDefBody()
    if body == None:
      print("Error) Body Empty : in %s" % (fn))
      raise Exception("Error", "Error")

    if rettype != 'void':
      if isinstance(body, ASTExprs) or isinstance(body, ASTSimpleExprs):
        # return을 명시적으로 적지 않았다면, 마지막 expression의 결과를 return값으로 한다.
        lastExpr = body.exprs[-1]
        if not isinstance(lastExpr, ASTReturn):
          body.exprs[-1] = ASTReturn(lastExpr)
      else:  # isinstance(body, ASTExpr):
        body = ASTExpr(ASTReturn(body))

    #print("&&=", type(rettype))
    #print("**=", body)

    # 바로전에 template이 선언되었다면 여기도 영향을 받아야만 한다.
    # 일단 지금은 영향을 받지 않는다고 가정한다.
    self.globalSymbolTable.registerFunc(fn, args, rettype, body, copy.deepcopy(self.localSymbolTable))

    self.localSymbolTable = {}

    # print "1", nativeSymbol, self.globalSymbolTable[nativeSymbol]
    # self.mustcompile.append((self.globalSymbolTable[nativeSymbol], nativeSymbol))

    if self.isdebug:
      print("ending parseDef")

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
      print("Error) Needed ')'")
      return None

    return args

  def parseReturnType(self):
    # if return type is none,
    if not self.match(':'):
      return ASTType(name="System.lang.Integer", templ=None, ranks=None)

    return self.parseType()

  def parseDefArg(self):
    name = self.getName()
    if name == None:
      return None

    typeStr = ASTType(name="System.lang.Integer", templ=None, ranks=None)
    if self.match(':'):
      typeStr = self.parseType()

    defval = None
    if self.match('='):
      defval = self.parseBasicSimpleExpr()

    # if typeStr == None: makeError
    return ASTDefArg(name=name, type=typeStr, defval=defval)

  def parseTemplatePart(self):
    if self.match('['):
      name = self.getNames()
      if name is None:
        print("Expected class name")
        sys.exit(-1)
        
      template = self.parseTemplatePart()

      self.match(']')
    return None

  def matchTemplateInfo(self, typeInfo, templateInfo):
    # raise Exception('matchTemplateInfo', 'Not Implemented')
    return True

  def parseType(self):
    if self.isdebug:
      print("starting parseType")

    idStr = self.getNames()
    template = self.parseTemplatePart()

    if self.isdebug:
      print(idStr)

    # 해당 type이 존재하는지 검사합니다.
    tp = self.globalSymbolTable.find(idStr)
    if tp == None:
      print("Unknown Type : %s" % (idStr))
      sys.exit(-1)

    if tp == 'alias':
      idStr = self.globalSymbolTable.find(idStr)
      # print "(", idStr

    # tmpl = self.parseTemplatePart()
    # if not self.matchTemplateInfo(result, tmpl):
    #  # 일단 현재는 pass
    #  print "Error) Not matched template information"
    #  pass

    # print "type's full name = %s" % (idStr)

    # tmpl  = self.parseTemplatePart()
    # ename, body = symbolTable.search(names.array)
    # if ename == None:
    #  print "doesn't exist symbol : %s" % (".".join(names.array))
    #  sys.exit(-1) # 일단 죽이고... 나중에 에러처리 생각
    # else:
    #  names.array = ename

    rank = self.parseRankList()

    if self.isdebug:
      print("ending parseType")

    return ASTType(name=idStr, templ=None, ranks=rank)

  def parseRankList(self):
    lst = []
    while self.match('['):
      rank = ASTRank(self.parseSimpleExpr())
      lst.append(rank)
      if not self.match(']'):
        print("Error) Need ']'")

    return ASTRankList(lst)

  def parseExprs(self):
    lst = []
    while not self.isEnd():
      ret = self.parseExpr()
      if ret == None:
        break
      if isinstance(ret, ASTExprs):
        lst += ret.exprs
      elif isinstance(ret, list):
        lst += ret
      else:
        # ??
        lst.append(ret)

    if len(lst) == 0: return None

    return ASTExprs(lst, copy.deepcopy(self.localSymbolTable))

  def parseExpr(self):
    ret = None

    if self.same('if'):
      ret = self.parseIfStmt()
    elif self.same('for'):
      ret = self.parseForStmt()
    elif self.same('var'):
      ret = self.parseVar()
    elif self.same('val'):
      ret = self.parseVal()
    elif self.same('{'):
      ret = self.parseBlockExprs()
    else:
      ret = self.parseSimpleExpr1()
      # print "***",ret
      self.match(';')
      # s = raw_input()

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

    cond = self.parseBasicSimpleExpr()
    if cond == None:
      print("Error) Needed to identifier")
      raise SyntaxError
    if not self.match('<='):
      print("Error) Needed to <=")
      raise SyntaxError
    generator = self.parseSimpleExpr()
    if generator == None:
      print("Error) Needed generator")
      raise SyntaxError

    body = None
    if self.match(':'):
      body = self.parseExpr()
    elif self.match('{'):
      body = self.parseExprs()
      self.match('}')
    else:
      print("Error) Needed '{' '}' or '='")
      raise NotImplementedError

    return ASTFor(cond, generator, body)

  def convertToASTType(self, obj):
    if isinstance(obj, ASTType):
      return obj
    elif isinstance(obj, ASTListGenerateType1):
      return self.convertToASTType(obj.start)
    elif isinstance(obj, ASTWord) and obj.vtype != None:
      if isinstance(obj.vtype, ASTType):
        return obj.vtype
      # 이건 비정상적인 경우, 이렇게 찾아들어오면 안된다.
      elif isinstance(obj.vtype, dict):
        return obj.vtype['@vtype']
      else:
        print("))", obj.vtype)
        raise NotImplementedError
    elif isinstance(obj, ASTWord) and isinstance(obj.type, ASTType):
      return obj.type
    elif isinstance(obj, ASTListGenerateType1):
      return ASTType('System.lang.Array')
    elif isinstance(obj, ASTCalleeArgType1):
      return self.convertToASTType(obj.type)
    else:
      print("**", obj)
      raise NotImplementedError

  def guessType(self, expr):
    if isinstance(expr, ASTWord):
      return expr.type

    return None

  def checkSameType(self, last: ASTType, rast: ASTType) -> bool:
    # 일단 상속관계를 보지 않는다. 단지 같은지만 비교한다.
    if last.type == rast.type:
      return True

    return False

  def parseVar(self):
    if not self.match('var'):
      return None

    sym = self.localSymbolTable

    hist = []
    while True:
      name = self.getName()
      if name in sym:
        print("has duplicated name")
        raise Exception('Error', 'Duplicated Name')
        return None

      type = None
      if self.match(':'):
        type = self.parseType()

      # print "name =", name

      # 변수 초기화
      tree = None
      if self.match('='):
        right = self.parseSimpleExpr()
        rtype = self.guessType(right)
        if rtype:
          if type: # 변수의 type을 명시적으로 선언했으면, 둘이 같은지 검사
            if not self.checkSameType(type, rtype):
              print(f"Error) Not equal between {type} and {rtype}")
              raise SyntaxError
          else:
            type = right.type

        tree = ASTBinOperator(ASTWord('id', '='), ASTWord('id', name, type), right)
        hist.append(tree)

      if type is None:
        print("No Variable Type")
        raise Exception('Error', 'No Variable Type')

      self.localSymbolTable[name] = {"type": "val", "vtype": type, "init": tree}
      if not self.match(','):
        break

    self.match(';')

    return hist

  def parseVal(self):
    if not self.match('val'):
      return None

    sym = self.localSymbolTable

    hist = []
    while True:
      name = self.getName()
      if name in sym:
        print("has duplicated name")
        raise Exception('Error', 'Duplicated Name')
        return None

      ltype = None
      if self.match(':'):
        ltype = self.parseType()

      # print "name =", name

      # 변수 초기화
      tree = None
      if self.match('='):
        right = self.parseSimpleExpr()
        rtype = self.guessType(right)
        if rtype:
          if ltype: # 변수의 type을 명시적으로 선언했으면, 둘이 같은지 검사
            if not self.checkSameType(ltype, rtype):
              print(f"Error) Not equal between {ltype} and {rtype}")
              raise SyntaxError
          else:
            ltype = right.type

        tree = ASTBinOperator(ASTWord('id', '='), ASTWord('id', name, ltype), right)
        hist.append(tree)

      if type is None:
        print("No Variable Type")
        raise Exception('Error', 'No Variable Type')

      self.localSymbolTable[name] = {"type": "val", "vtype": type, "init": tree}
      if not self.match(','):
        break

    self.match(';')

    return hist

  def parseBlockExprs(self):
    self.match('{')
    backup = copy.deepcopy(self.localSymbolTable)
    ast = self.parseExprs()
    self.localSymbolTable = backup
    if not self.match('}'):
      print("Error) Need '}'")
      raise SyntaxError

    return ast

  def parseSimpleExpr1(self):
    ret = self.parseSimpleExprs()
    # not yet!
    # if self.match('?'):
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

    nhist = len(history)
    
    if self.isdebug:
      print("nhist = ", nhist)

    if nhist == 0:
      return None
    elif nhist == 1:
      return history[0]

    # self.match(';') # caution!!
    return ASTSimpleExprs(history)

  def parseSimpleExpr(self):
    def getType(node):
      return node.type

    def compareType(left, right):
      if getType(left) == getType(right):
        return True
      else:
        # 상속관계일 경우에 대한 체크가 필요
        return False

    if self.isdebug:
      print("entering parseSimpleExpr()")

    tree = self.parseBasicSimpleExpr()
    if tree == None: return None
    while not self.isEnd():
      if self.isdebug:
        print(self.getTokValue())

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

          # Global Operator 함수로 첫번째 찾는다. (C++의 operator + (left, right)라는 식..)
          content = {'@type': 'def', '@name': tok.value}
          content['@args'] = [self.convertToASTType(tree), self.convertToASTType(right)]
          symbol = self.globalSymbolTable.find(content)
          if symbol == None:
            # 없다면, left.type의 operator로 찾는다. (C++의 someclass::operator + (right)...)
            content = {'@type': 'def', '@name': self.convertToASTType(tree).name + "." + tok.value}
            content['@args'] = [self.convertToASTType(right)]
            symbol = self.globalSymbolTable.find(content)

          print("4", symbol, content)
          if symbol != None:
            if symbol['@type'] == 'native def':
              raise NotImplementedError
            else:
              tree = ASTFuncCall(content['@name'], tree, right)
          elif symbol == None:
            if compareType(tree, right):
              tree = ASTBinOperator(ASTWord(tok.type, tok.value), tree, right)
            else:
              print("Error: they has difference type between two values")
              sys.exit(-1)

      # array
      elif self.sameType('id'):
        # if isinstance(tree, ASTSet):
        #  #if len(tree.lst) != 1:
        #  #  print "error!!" # make error!!
        #  if self.checktype(tree.lst[0]):
        #    tree = ASTCasting(tree.lst[0], ASTWord(tok.type, tok.value))
        tokVal = self.getTokValue()
        tokType = self.getTokType()

        mid = ASTWord(tokType, tokVal)

        self.token.nextToken()

        right = self.parseBasicSimpleExpr()
        # print "here : ", mid, tree, right
        if right != None:
          content = {'@type': 'def', '@name': tokVal}
          content['@args'] = [self.convertToASTType(tree), self.convertToASTType(right)]
          symbol = self.globalSymbolTable.find(content)
          if symbol == None:
            # 없다면, left.type의 operator로 찾는다. (C++의 someclass::operator + (right)...)
            content = {'@type': 'def', '@name': self.convertToASTType(tree).name + "." + tokVal}
            content['@args'] = [self.convertToASTType(right)]
            symbol = self.globalSymbolTable.find(content)

          if symbol != None:
            if symbol['@type'] == 'native def':
              raise NotImplementedError
            else:
              tree = ASTFuncCall(content['@name'], [tree, right])
          else:
            tree = ASTBinOperator(mid, tree, right)
        else:
          # for example, 'a++' or 'a+'
          tree = ASTUnary(tree, mid)
      else:
        break

    if isinstance(tree, ASTFuncCall):
      candidates = set([])

      path = None
      if isinstance(tree, ASTNames):
        path = ".".join(tree.array)
      elif isinstance(tree.name, ASTNames):
        path = ".".join(tree.name.array)
      else:
        path = tree.name

      ret = self.globalSymbolTable.find(
        {'@type': 'def', '@name': path, '@args': [self.convertToASTType(x) for x in tree.args]})
      if ret == None:
        print("Error) Not Symbol :", path, [self.convertToASTType(x) for x in tree.args])
        raise SyntaxError

    if self.isdebug:
      print("ending parseSimpleExpr()")

    return tree

  def parseBasicSimpleExpr(self):
    tok = self.token.tok
    if tok == None: return None
    # print "calling parseBasicSimpleExpr"
    # print "value =", tok.value, tok.type
    if self.matchType('stringLiteral'):
      return ASTWord(ASTType('System.lang.String'), tok.value)
    elif self.matchType('integerLiteral'):
      return ASTWord(ASTType('System.lang.Integer'), tok.value)
    elif self.matchType('floatLiteral'):
      return ASTWord(ASTType('System.lang.Float'), tok.value)
    elif self.match('true'):
      return ASTWord(ASTType('System.lang.Boolean'), '1')
    elif self.match('false'):
      return ASTWord(ASTType('System.lang.Boolean'), '0')
    elif self.match('return'):
      # print "entering return"
      expr = self.parseSimpleExpr()
      # print "@@", expr
      return ASTReturn(expr)
    # elif self.match('def'):
    #  ret = self.parseDefInnerFunc()

    # if len(ret.name) != 1:
    #  print "don't use namespace!"
    #  sys.exit(-1)

    # realname = ret.name[0]
    # if realname == '_':
    #  realname = self.genTemporaryName()
    # if self.findAt(tbl = self.local_symtbl, target = ret.name):
    #  print "already defined!"
    #  sys.exit(-1)

    # typename = convertType(ret.ret)
    # if not self.validateType(typename):
    #  print "not declare type"
    #  sys.exit(-1)

    # self.local_symtbl[realname] = {
    #  "attribute": ["lambda"],
    #  "args": ret.args,
    #  "type": typename,
    #  "body": ret.body}

    # return ret
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
          print("Error) Need ')'")

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
        return ASTListGenerateType1(ASTWord(tok.type, tok.value), right)  # 여기서 빠진 것은 Arrya<T이어야 한다는 사실(Type이 빠졌다는 소리)
      else:
        vtype = None
        if tok.value in self.localSymbolTable:
          vtype = self.localSymbolTable[tok.value]

        if vtype == None:
          vtype = self.globalSymbolTable.find(tok.value)

        return ASTWord(tok.type, tok.value, vtype)
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
    # else:
    #  print tok
    #  raise Exception("parseBasicSimpleExpr", "Not implemented")

    return None

  def parseDefArgListForFuncCall(self):
    args = []

    while True:
      arg = self.parseSimpleExpr()
      if isinstance(arg, ASTWord):
        if arg.type == 'id':
          symtbl = self.localSymbolTable[-1]
          if arg.value not in symtbl:
            print("Error) Not found :", arg.value)
            raise SyntaxError

          args.append(ASTCalleeArgType1(value=arg, type=symtbl[arg.value]))
        else:
          args.append(ASTCalleeArgType1(value=arg, type=arg.type))
      else:
        print(arg)
        raise NotImplementedError

      if not self.match(','):
        break

    return args
