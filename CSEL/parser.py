#!/usr/bin/env pythone
# -*- coding: utf-8 -*-
from typing import *
import traceback

import CSEL.TypeTable
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
from .ASTID import *
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
from .TypeTable import *
from .IR import *
from .mangle import *

import copy
import random
import re

sourceSets = []

# symbol의 type등에 대한 부분은 string match로...
# class나 struct일 경우는 hierachy탐색이 추가
# template은 macro에 가까우므로, 별도의 table을 두고, realization할때 가상의 class name을 부여하여 사용 예) <templatename>_<realization type string>
class PROPERTY:
  PUBLIE = 1
  PRIVATE = 2
  PROTECTED = 3


def checkNamespaceGroup(name: str) -> bool:
  if re.match(r'^((_|[a-zA-Z])[a-zA-Z0-9_]*\.)*\*$', name):
    return True
  
  return False


def mangling(name: str, args: List[AST], rettype: ASTType = None, extern: bool = False):
  # name들은 무조건 C++기준으로, 단 extern이 있으면 C로 가정한다.
  if extern is True:
    return "_" + name
  
  return encodeSymbolName(name, args)


def doInternalMangling(name: str, args: List[AST]) -> str:
  return encodeSymbolName(name, args)


class ClassSuccessionInfo:
  PUBLIC = 1
  PROTECTED = 2
  PRIVATE = 3
  
  def __init__(self, path: str, type: ASTType):
    self.path = path
    self.type = type


class SyntaxError(Exception):
  def __init__(self):
    pass


class Library:
  def __init__(self, libraryPaths: List[str]):
    self.libraryPaths = libraryPaths
    self.getLibraryPaths()
  
  def getLibraryPaths(self):
    import os
    import glob
    
    libraries: List[str] = []
    for p in self.libraryPaths:
      temp = glob.glob(os.paths.join(p, "*"))
      libraries.extends(temp)
    
    self.library_paths = libraries
  
  def loadSymbolFrom(self, path: str) -> SymbolTable:
    # 모든 symbol들은 System.lang.Object형태로 변경된 후 다루어진다.
    
    # 1. 상위이름으로 매칭되는 파일명 찾기 : 예를 들어, System.lang.Object를 찾는다면, System.lang.Object.dll을 찾으면 됨
    # 2. 찾은게 있다면, 해당 library파일을 읽어서 거기에 있는 symbol들을 몽땅다 읽기
    # 3. demangling하기
    # 4. 그걸 적당한 class로 감싸서 돌려주기
    raise NotImplementedError
    return None


# <- 키워드에 대한 정의 (이건 library에서 하면될듯)
# 위 operator는 async한 assign이다.
# = 은 sync한 assign을 의미한다. 
# thread환경이 아니라면 '<-'은 '='과 동일하게 동작하지만
# thread환경일 경우는 '<-'은 synchronized한 동작을 한다(thread-safe)
# 하지만 '='은 no-thread-safe하게 동작한다. (2013.03.12)
class Parser:
  def __init__(self, fn: str, isdebug: bool = False):
    self.isdebug = isdebug  # 0은 디버깅하지 않겠다는 의미
    
    self.basename: str = fn[:fn.rfind('.')]
    
    self.token: Token = Token(fn)
    self.token.nextToken()
    
    # Root Symbol Table 등록
    self.symbolTable: SymbolTable = SymbolTable()
    # 함수 시작되면, 사용
    self.localSymbolTable = []
    
    # function이나 class앞의 template이나 attribute같은 것들의 정보를 가지고 있는...
    self.directive = []
    
    # 아무것도 없으면 Root임
    self.namespaceStack: List[str] = []
    self.loadedSymbolList = []
    
    self.mustcompile: List[AST] = []
  
  def initSymbolTable(self) -> SymbolTable:
    symTbl = SymbolTable()
    return symTbl
  
  def nextToken(self) -> NoReturn:
    self.token.nextToken()
  
  def match(self, word: str) -> bool:
    return self.token.match(word)
  
  def same(self, word: str) -> bool:
    return self.token.same(word)
  
  def matchType(self, word: str) -> str:
    return self.token.matchType(word)
  
  def sameType(self, word: str) -> bool:
    return self.token.sameType(word)
  
  def isEnd(self) -> bool:
    return self.token.reachEnd()
  
  def getTokValue(self) -> str:
    return self.token.tok.value
  
  def getTokType(self) -> Type:
    if self.isdebug:
      print(f"getTokType = {self.token.tok.type}")

    if self.token.tok.type == 'stringLiteral':
      return self.symbolTable.convert(ASTType('System.lang.String'))
    elif self.token.tok.type == 'integerLiteral':
      return self.symbolTable.convert(ASTType('System.lang.Int'))
    elif self.token.tok.type == 'floatLiteral':
      return self.symbolTable.convert(ASTType('System.lang.Float'))
    elif self.token.tok.type == 'true':
      return self.symbolTable.convert(ASTType('System.lang.Boolean'))
    elif self.token.tok.type == 'false':
      return self.symbolTable.convert(ASTType('System.lang.Boolean'))
    else:
      if self.isdebug:
        print(self.token.tok.type)

      return None

  def searchSymbol(self, name: str):
    # 우선 local에서... 마지막 scope에서부터 찾는다.
    for scope in reversed(self.localSymbolTable):
      if name in scope:
        return scope[name]

    return self.symbolTable.find(name)
  
  def getName(self) -> str:
    if self.match('_'):
      return ASTUnit()
    
    return self.token.matchType('id')
  
  def getNames(self) -> str:
    names = []
    while not self.isEnd():
      names.append(self.getName())
      if not self.match('.'):
        break
    
    return ".".join(names)
  
  def parse(self) -> NoReturn:
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
  
  def parseImport(self) -> NoReturn:
    path = self.getImportNames()
    alias = None
    if self.match('as'):
      alias = self.getName()
    
    # TODO: 실제 해당 namespace 또는 class가 있는지 체크한다.
    library = Library([""])
    symbols = library.loadSymbolFrom(path)
    matched = symbols.findByLastName(path)
    for symbol in matched:
      self.symbolTable.register(symbol)
  
  def getImportNames(self) -> str:
    names = []
    while not self.isEnd():
      names.append(self.getName())
      if not self.match('.'):
        break
    
    return ".".join(names)
  
  def parseNamespace(self) -> NoReturn:
    if not self.match('namespace'):
      return
    
    path = self.getNames()
    
    self.namespaceStack.append(path)
    self.parseNamespaceBody()
    name = ".".join(self.namespaceStack)
    self.symbolTable.registerNamespace(name)  # TODO: 수정필요
    self.namespaceStack.pop()  # symbol search할때도 사용할예정
  
  def getWorkingPath(self) -> str:
    return ".".join(self.namespaceStack)
  
  def parseNamespaceBody(self) -> NoReturn:
    if not self.match('{'):
      return
    
    self.parse()
    
    self.match('}')
  
  def parseClass(self) -> NoReturn:
    if not self.match('class'):
      return
    
    names = self.getNames()
    
    # 검색 symbol list에 등록만 해놓는다.
    # 정의가 안되어 있다가 나중에 사용되면 실제 symbol table에 body가 없으므로,
    # body가 없다고 에러를 내면 된다.
    # self.loadedSymbolList와 self.namespaceStack은 단지 symbol을 만들때와 symbol참조를 위해서만 쓰인다.
    # TODO: System.lang.Object는 기본 상속, public인지, private인지, trait인지등에 대한 정보 추가 필요
    parents = [ClassSuccessionInfo("System.lang.Object", ClassSuccessionInfo.PUBLIC)]
    if self.match(':'):  # 상속이 있다면...
      # TODO: 상속과 관련된 코드 필요
      pass
    
    if self.match(';'):
      self.namespaceStack.append(names)
      self.symbolTable.registerClass(".".join(self.namespaceStack), parents)  # TODO: 상속등의 class정보도 주어져야...
      self.namespaceStack.pop()
      return
    
    self.namespaceStack.append(names)
    self.parseClassBody()
    self.symbolTable.registerClass(".".join(self.namespaceStack), parents)  # TODO: Body는 어딘가에 등록이 되어야 할 듯?
    self.namespaceStack.pop()
  
  def parseClassBody(self) -> NoReturn:
    if not self.match('{'):
      return
    
    property = PROPERTY.PUBLIC
    body = {}
    while not self.match('}'):
      if self.match('public'):
        property = PROPERTY.PUBLIE
      elif self.match('prviate'):
        property = PROPERTY.PRIVATE
      elif self.match('protected'):
        property = PROPERTY.PROTECTED

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
        
        if property == PROPERTY.PUBLIC or property == PROPERTY.PROTECTED:
          self.namespaceStack.append(name)
          self.symbolTable.registerValue(name, type, body)
          self.namespaceStack.pop()
        else:
          if name in self.localSymbolTable[-1]:
            raise Exception(f"already {name}")
          else:
            self.localSymbolTable[-1][name] = {'type': type, 'body': body, 'property': PROPERTY.PRIVATE}
            
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
        self.symbolTable.registerVariable(name, type, body)
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
          rettype = self.parseType()
        else:
          rettype = ASTUnit()
        
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
        self.symbolTable.registerFunc(name, args, self.symbolTable.convert(rettype), body)
        self.namespaceStack.pop()
  
  def parseInitExpr(self) -> NoReturn:
    # 여긴 상수나 간단한 계산하는 루틴정도?
    # 아님 배열
    
    raise NotImplementedError
  
  def parseAttribute(self) -> NoReturn:
    if not self.match('@'):
      return
    
    pass
  
  def parseTemplate(self) -> ASTTemplate:
    if not self.match('template'):
      return None
    
    params = self.parseTemplateArguments()
    if params is None:
      print("Error) Needs some template parameters")
      return None
    
    for param in params:
      self.symbolTable.registerTemplateVariable(param.name, param.type)
    
    if self.same('class'):
      target = self.parseClass()
    elif self.same('def'):
      target = self.parseDef()
      
      self.symbolTable.register({
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
  
  def parseTemplateArguments(self) -> List[ASTTemplateArg]:
    if not self.match('<'):
      return None
    
    # 선언할때는 function argument처럼
    args = [self.parseTemplateArgument()]
    while self.match(','):
      args.append(self.parseTemplateArgument())
    
    if not self.match('>'):
      return None
    
    return args
  
  def parseTemplateArgument(self) -> ASTTemplateArg:
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
  def makeFullPath(self, fn: str) -> str:
    return ".".join(self.namespaceStack + [fn])
  
  def parseDefBody(self) -> NoReturn:
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
  
  def parseFuncName(self) -> NoReturn:
    tmp = self.token.matchType('id')
    # template!!
    if self.same('['):
      typeName = self.parseTemplateName()
  
  def parseDef(self) -> NoReturn:
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
      
      if not self.symbolTable.findByLastName(arg.type.name):
        print("Error) Unknown Type")
        raise SyntaxError
      
      self.localSymbolTable[arg.name] = arg.type
    
    nativeFuncname = doInternalMangling(funcname, args)
    fn = ".".join(self.namespaceStack + [nativeFuncname])
    # global symbol table에서 체크 : 인자 다양성 부분에 대한 고려가 필요
    if self.symbolTable.findByLastName(fn):
      name = ".".join(self.namespaceStack + [funcname])
      print(f"Error) Already defined : {name}")
      raise SyntaxError
    
    # To parse return type
    rettype = self.parseReturnType()
    
    # To parse body of function
    body = self.parseDefBody()
    if body is None:
      print("Error) Body Empty : in %s" % (fn))
      raise Exception("Error", "Error")
    
    if rettype != UnitType():
      if isinstance(body, ASTExprs) or isinstance(body, ASTSimpleExprs):
        # return을 명시적으로 적지 않았다면, 마지막 expression의 결과를 return값으로 한다.
        lastExpr = body.exprs[-1]
        if not isinstance(lastExpr, ASTReturn):
          body.exprs[-1] = ASTReturn(lastExpr)
      else:  # isinstance(body, ASTExpr):
        body = ASTExpr(ASTReturn(body))
    
    # print("&&=", type(rettype))
    # print("**=", body)
    
    # 바로전에 template이 선언되었다면 여기도 영향을 받아야만 한다.
    # 일단 지금은 영향을 받지 않는다고 가정한다.
    self.symbolTable.registerFunc(fn, args, rettype, body, copy.deepcopy(self.localSymbolTable))
    
    self.localSymbolTable = {}
    
    # print "1", nativeSymbol, self.symbolTable[nativeSymbol]
    # self.mustcompile.append((self.symbolTable[nativeSymbol], nativeSymbol))
    
    if self.isdebug:
      print("ending parseDef")
  
  def parseDefArgsList(self) -> List[ASTDefArg]:
    if not self.match('('):
      return None
    
    args = []
    while not self.isEnd():
      arg = self.parseDefArg()
      if arg is None: break
      args.append(arg)
      if not self.match(','): break
    
    if not self.match(')'):
      print("Error) Needed ')'")
      return None
    
    return args
  
  def parseReturnType(self) -> ASTType:
    # if return type is none,
    if not self.match(':'):
      return ASTType(name="System.lang.Int", templ=None, ranks=None)
    
    return self.parseType()
  
  def parseDefArg(self) -> ASTDefArg:
    name = self.getName()
    if name is None:
      return None
    
    typeStr = self.symbolTable.convert(ASTType(name="System.lang.Int", templ=None, ranks=None))
    if self.match(':'):
      typeStr = self.parseType()
    
    defval = None
    if self.match('='):
      defval = self.parseBasicSimpleExpr()
    
    # if typeStr is None: makeError
    return ASTDefArg(name=name, type=typeStr, defval=defval)
  
  def parseTemplatePart(self) -> Type:
    if self.match('<'):
      name = self.parseType()
      if name is None:
        print("Expected class name")
        sys.exit(-1)
      
      template = self.parseTemplatePart()
      
      self.match('>')
      
      return template
    
    return None
  
  def matchTemplateInfo(self, typeInfo, templateInfo) -> bool:
    # raise Exception('matchTemplateInfo', 'Not Implemented')
    return True
  
  def parseType(self) -> Type:
    if self.isdebug:
      print("starting parseType")
    
    idStr = self.getNames()
    template = self.parseTemplatePart()
    
    if self.isdebug:
      print(idStr)
    
    # 해당 type이 존재하는지 검사합니다.
    tp = self.symbolTable.findByLastName(idStr)
    if tp is None:
      print("Unknown Type : %s" % (idStr))
      sys.exit(-1)
    
    if tp == 'alias':
      idStr = self.symbolTable.findByLastName(idStr)
      # print "(", idStr
    
    # tmpl = self.parseTemplatePart()
    # if not self.matchTemplateInfo(result, tmpl):
    #  # 일단 현재는 pass
    #  print("Error) Not matched template information")
    #  pass
    
    # print("type's full name = %s" % (idStr))
    
    # tmpl  = self.parseTemplatePart()
    # ename, body = symbolTable.search(names.array)
    # if ename is None:
    #  print("doesn't exist symbol : %s" % (".".join(names.array)))
    #  sys.exit(-1) # 일단 죽이고... 나중에 에러처리 생각
    # else:
    #  names.array = ename
    
    rank = self.parseRankList()
    
    if self.isdebug:
      print("ending parseType")
    
    return self.symbolTable.convert(ASTType(name=idStr, templ=template, ranks=rank))
  
  def parseRankList(self) -> ASTRankList:
    lst = []
    while self.match('['):
      rank = ASTRank(self.parseSimpleExpr())
      lst.append(rank)
      if not self.match(']'):
        print("Error) Need ']'")
    
    return ASTRankList(lst)
  
  def parseExprs(self) -> ASTExprs:
    lst = []
    while not self.isEnd():
      ret = self.parseExpr()
      if ret is None:
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
  
  def parseExpr(self) -> AST:
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
  
  def parseIfStmt(self) -> ASTIf:
    if not self.match('if'):
      return None
    
    cond = self.parseExpr()
    self.match(':')
    body = self.parseExpr()
    return ASTIf(cond, body)
  
  def parseForStmt(self) -> ASTFor:
    if not self.match('for'):
      return None
    
    cond = self.parseBasicSimpleExpr()
    if cond is None:
      print("Error) Needed to identifier")
      raise SyntaxError
    if not self.match('<='):
      print("Error) Needed to <=")
      raise SyntaxError
    generator = self.parseSimpleExpr()
    if generator is None:
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
  
  def convertToASTType(self, obj: AST) -> Type:
    if isinstance(obj, ASTType):
      return self.symbolTable.convert(obj)
    elif isinstance(obj, ASTListGenerateType1):
      return self.convertToASTType(obj.start)
    elif isinstance(obj, ASTWord) and obj.type is not None:
      if isinstance(obj.type, ASTType):
        return self.symbolTable.convert(obj.type)
      # 이건 비정상적인 경우, 이렇게 찾아들어오면 안된다.
      elif isinstance(obj.type, dict):
        return obj.type['vtype']
      elif isinstance(obj.type, Type):
        return obj.type
      else:
        print("))", obj.type)
        raise NotImplementedError
    elif isinstance(obj, ASTWord) and isinstance(obj.type, ASTType):
      return self.symbolTable.convert(obj.type)
    elif isinstance(obj, ASTListGenerateType1):
      return self.symbolTable.convert(ASTType('System.lang.Array'))
    elif isinstance(obj, ASTCalleeArgType1):
      return obj.type
    elif isinstance(obj, ASTID):
      return obj.type
    else:
      print("**", type(obj))
      raise NotImplementedError
    
    return None
  
  def guessType(self, expr: AST) -> Type:
    if isinstance(expr, ASTWord):
      return expr.type
    elif isinstance(expr, ASTBinOperator):
      return expr.vtype
    elif isinstance(expr, ASTID):
      return expr.type

    if self.isdebug:
      print("=", expr)

    return None
  
  def checkSameType(self, last: ASTType, rast: ASTType) -> bool:
    # 일단 상속관계를 보지 않는다. 단지 같은지만 비교한다.
    if last.type == rast.type:
      return True
    
    return False
  
  def parseVar(self) -> List[AST]:
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
          if ltype:  # 변수의 type을 명시적으로 선언했으면, 둘이 같은지 검사
            if not self.checkSameType(ltype, rtype):
              print(f"Error) Not equal between {ltype} and {rtype}")
              raise SyntaxError
          else:
            ltype = rtype
        
        tree = ASTBinOperator('=', ASTID(name, ltype), right, ltype)
        hist.append(tree)
      
      if ltype is None:
        print("No Variable Type")
        raise Exception('Error', 'No Variable Type')
      
      self.localSymbolTable[name] = {"type": "val", "vtype": ltype, "init": tree}
      if not self.match(','):
        break
    
    self.match(';')
    
    return hist
  
  def parseVal(self) -> List[AST]:
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
          if ltype:  # 변수의 type을 명시적으로 선언했으면, 둘이 같은지 검사
            if not self.checkSameType(ltype, rtype):
              print(f"Error) Not equal between {ltype} and {rtype}")
              raise SyntaxError
          else:
            ltype = right.type
        
        tree = ASTBinOperator('=', ASTID(name, ltype), right, ltype)
        hist.append(tree)
      
      if ltype is None:
        print("No Variable Type")
        raise Exception('Error', 'No Variable Type')
      
      self.localSymbolTable[name] = {"type": "val", "vtype": ltype, "init": tree}
      if not self.match(','):
        break
    
    self.match(';')
    
    return hist
  
  def parseBlockExprs(self) -> AST:
    self.match('{')
    backup = copy.deepcopy(self.localSymbolTable)
    ast = self.parseExprs()
    self.localSymbolTable = backup
    if not self.match('}'):
      print("Error) Need '}'")
      raise SyntaxError
    
    return ast
  
  def parseSimpleExpr1(self) -> AST:
    ret = self.parseSimpleExprs()
    # not yet!
    # if self.match('?'):
    #  body = self.parseMatchingCases()
    #  ret  = ASTPatternMatch(cond = ret, body = body)
    return ret
  
  def parseSimpleExprs(self) -> AST:
    history = []
    while not self.isEnd():
      tree = self.parseSimpleExpr()
      if tree is None: break
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
  
  def getSymbolNames(self, tree: AST) -> str:
    path = None
    if isinstance(tree, ASTNames):
      path = ".".join(tree.array)
    elif isinstance(tree.name, ASTNames):
      path = ".".join(tree.name.array)
    elif isinstance(tree.name, ASTID):
      path = tree.name.name
    else:
      path = tree.name

    return path

  def guessBestSymbol(self, left: AST, mid: AST, right: AST):
    # binary operator에 대해서 symbol table에서 위 3가지 심볼에 대해서 가장 잘 매칭되는 함수 형태를 찾는다.
    left_type = self.guessType(left).getTypename()
    right_type = self.guessType(right).getTypename()
    # 1. global binary operator(mid) function을 찾는다.
    if isinstance(mid, ASTWord):
      mid_name = "operator{}".format(mid.value)
    else:
      raise NotImplementedError

    retType = self.symbolTable.glob(mid_name, [left_type, right_type])

    if retType is not None:
      return retType

    # 2. 'right'에서 operator(mid)에 대한 정의가 있는지 찾는다.

    # 3. 'left'에서 operator(mid)에 대한 정의가 있는지 찾는다.
    fname = "{}.operator{}".format(left_type, mid_name)
    retType = self.symbolTable.glob(fname, [right_type])
    if retType is not None:
      return retType

    # 4. 없으면 오류
    return None

  def parseSimpleExpr(self) -> AST:
    def getType(node: AST) -> Type:
      return node.type
    
    def compareType(left: AST, right: AST) -> bool:
      if getType(left) == getType(right):
        return True
      else:
        # 상속관계일 경우에 대한 체크가 필요
        return False
    
    if self.isdebug:
      print("entering parseSimpleExpr()")
    
    tree = self.parseBasicSimpleExpr()
    if tree is None: return None
    while not self.isEnd():
      if self.isdebug:
        print(self.getTokValue())
      
      if self.match('.'):
        right = self.parseBasicSimpleExpr()
        if isinstance(tree, ASTID):
          if isinstance(right, ASTID):
            tree = ASTNames([tree.name, right.name])
          elif isinstance(right, ASTFuncCall):
            tree = ASTFuncCall(ASTNames([tree.name, right.name.value]), right.body)
          elif isinstance(right, ASTIndexing):
            tree = ASTIndexing(ASTNames([tree.name, right.name.value]), right.history)
        elif isinstance(tree, ASTWord):
          raise NotImplementedError
        elif isinstance(tree, ASTNames):
          if isinstance(right, ASTID):
            tree = ASTNames(tree.array + [right.name])
          elif isinstance(right, ASTFuncCall):
            tree = ASTFuncCall(ASTNames(tree.array + [right.name.name]), right.args)
          elif isinstance(right, ASTIndexing):
            tree = ASTIndexing(ASTNames(tree.array + [right.name.name]), right.history)
        else:
          tok = self.token.tok
          tokVal = tok.value
          
          # Global Operator 함수로 첫번째 찾는다. (C++의 operator + (left, right)라는 식..)
          fn = f"{self.convertToASTType(tree).name}.{tokVal}"
          if tokVal in self.symbolTable.cvttbl:
            fn = f"{self.convertToASTType(tree).name}.{self.symbolTable.cvttbl[tokVal]}"
          
          symbol = self.symbolTable.findByLastName(fn)
          if symbol is None:
            # 없다면, left.type의 operator로 찾는다. (C++의 someclass::operator + (right)...)
            print(f"Error) Function or operator not exists : {tokVal}")
            raise NotImplementedError
          
          if self.isdebug:
            print("4", symbol)

          if tokVal not in self.symbolTable.cvttbl:
            tree = ASTFuncCall(fn, tree, right)
          else:
            tree = ASTBinOperator(tokVal, tree, right, vtype=self.calcBinOperatorRetType(tokVal, tree, right))
      
      # array
      elif self.sameType('id'):
        # if isinstance(tree, ASTSet):
        #  #if len(tree.lst) != 1:
        #  #  print "error!!" # make error!!
        #  if self.checktype(tree.lst[0]):
        #    tree = ASTCasting(tree.lst[0], ASTWord(tok.type, tok.value))
        tokVal = self.getTokValue()
        tokType = self.getTokType()
        mid = ASTWord(tokVal, tokType)
        
        self.nextToken()

        right = self.parseBasicSimpleExpr()

        best_guess = self.guessBestSymbol(tree, mid, right)

        if isinstance(best_guess, FuncType):
          tree = ASTFuncCall(tokVal, [tree, right])
        elif isinstance(best_guess, NativeFuncType):
          tree = ASTBinOperator(mid, tree, right, vtype=best_guess.rettype)
        else:
          # for example, 'a++' or 'a+'
          tree = ASTUnary(tree, mid, tree.vtype)
      else:
        break
    
    if isinstance(tree, ASTFuncCall):
      candidates = set([])
      
      path = None
      if isinstance(tree, ASTNames):
        path = ".".join(tree.array)
      elif isinstance(tree.name, ASTNames):
        path = ".".join(tree.name.array)
      elif isinstance(tree.name, ASTID):
        path = tree.name.name
      else:
        path = tree.name
      
      fn = FuncType(path, [FuncArgInfo("", self.getType(x)) for x in tree.args], None)

      if self.isdebug:
        print(fn, path, type(path))
      
      ret = self.symbolTable.findByLastName(path)
      if ret is None:
        print(f"Error) Not Symbol : {fn}")
        raise SyntaxError
    
    if self.isdebug:
      print("ending parseSimpleExpr()")
    
    return tree
  
  def getType(self, node: AST) -> Type:
    if isinstance(node, Type):
      return node
    elif isinstance(node, ASTWord):
      return node.type
    elif isinstance(node, ASTID):
      return node.type
    elif isinstance(node, ASTBinOperator):
      return node.vtype
    else:
      print(node)
      raise NotImplementedError
  
  def calcBinOperatorRetType(self, mid: ASTWord, left: AST, right: AST) -> Type:
    if mid.type == '=':
      return left.vtype
    
    # 여기서는 우선 순위가 중요함
    # C++의 friend함수와 같은 것을 여기에 허용할 것인가?
    # 1. 우선 friend함수를 찾아본다.
    # 2. left를 기준으로 찾아본다.
    # 3. right를 기준으로 찾아본다.
    t = FuncType(mid.value, [FuncArgInfo("", left.type),
                             FuncArgInfo("", right.type)], None)
    fn = mid.value
    if mid.value in self.symbolTable.cvttbl:
      fn = self.symbolTable.cvttbl[mid.value]
    
    if self.isdebug:
      print(fn)

    symbols = self.symbolTable.findByLastName(fn)
    if symbols is None or len(symbols) == 0:
      print("Error) symbol is not found")
      raise SyntaxError
    elif len(symbols) == 1:
      symbol = symbols[list(symbols.keys())[0]]
      if isinstance(symbol, FuncType):
        return symbol.rettype
      else:
        print("Error) Failed to find a function")
        return None
    else:
      # 여러개의 symbol이 발견, 이 중에서 어떤 것을 선택할 것인가??
      # left.vtype을 기준으로
      bestOne: FuncType = None
      for key in symbols:
        if key.startswith(left.vtype.name) \
          and isinstance(symbols[key], FuncType) \
          and len(symbols[key].args) > len(bestOne.args):
          bestOne = symbols[key]
      
      if bestOne is None:
        print("Error) Not found best one!")
        print(symbols)
        raise NotImplementedError
      
      return bestOne.rettype
    
    return None
  
  def parseBasicSimpleExpr(self) -> AST:
    tok = self.token.tok
    if tok is None: return None
    # print "calling parseBasicSimpleExpr"
    # print "value =", tok.value, tok.type
    if self.matchType('stringLiteral'):
      return ASTWord(tok.value, self.symbolTable.convert(ASTType('System.lang.String')))
    elif self.matchType('integerLiteral'):
      return ASTWord(tok.value, self.symbolTable.convert(ASTType('System.lang.Int')))
    elif self.matchType('floatLiteral'):
      return ASTWord(tok.value, self.symbolTable.convert(ASTType('System.lang.Float')))
    elif self.match('true'):
      return ASTWord('true', self.symbolTable.convert(ASTType('System.lang.Boolean')))
    elif self.match('false'):
      return ASTWord('false', self.symbolTable.convert(ASTType('System.lang.Boolean')))
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
    # if self.findByLastNameAt(tbl = self.local_symtbl, target = ret.name):
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
      names = [tok.value]
      while self.match('.'):
        tok = self.token.tok
        if self.matchType('id'):
          names.append(tok.value)
        else:
          print(tok.value)
          raise NotImplementedError
          
      path = ".".join(names)

      if self.same('['):
        history = []
        while self.match('['):
          history.append(self.parseSimpleExpr())
          self.match(']')
        return ASTIndexing(ASTID(path, tok.type), history)
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
        return ASTFuncCall(ASTID(path, tok.type), args)
      elif self.match('...'):
        right = self.parseSimpleExpr()
        return ASTListGenerateType1(ASTWord(path, tok.type), right)  # 여기서 빠진 것은 Arrya<T이어야 한다는 사실(Type이 빠졌다는 소리)
      else:
        vtype = None
        if path in self.localSymbolTable:
          vtype: CSEL.TypeTable.Type = self.localSymbolTable[path]
          if 'type' in vtype:
            vtype: CSEL.TypeTable.Type = vtype['vtype']
        elif path in self.symbolTable:
          vtype: CSEL.TypeTable.Type = self.symbolTable[path]
          if isinstance(vtype, AliasType):
            vtype: CSEL.TypeTable.Type = vtype.original_type
        #else:
        #  print(f"Error) Not found symbol {path}")
        #  raise SyntaxError
        
        return ASTID(path, vtype)
    elif self.match('_'):
      return ASTWord(tok.value, self.symbolTable.convert(ASTType("Unit")))
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
  
  def parseDefArgListForFuncCall(self) -> List[AST]:
    args = []
    
    while True:
      arg = self.parseSimpleExpr()
      if isinstance(arg, ASTWord):
        args.append(arg)
      elif isinstance(arg, ASTID):
        symtbl = self.localSymbolTable[-1]
        if arg.name not in symtbl:
          print("Error) Not found :", arg.name)
          raise SyntaxError

        args.append(arg)
      elif isinstance(arg, ASTBinOperator):
        # type checking때문에 type guessing을 해야하나??
        args.append(arg)
      else:
        print(arg)
        raise NotImplementedError
      
      if not self.match(','):
        break
    
    return args
