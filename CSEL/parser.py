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
from ASTNativeAdd import *
from ASTNativeMove import *

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

def mangling(name, args, rettype = None, extern = False):
    # name들은 무조건 C++기준으로, 단 extern이 있으면 C로 가정한다.
    if extern == True:
        return "_" + name
    
    return encodeSymbolName(name, args)

class SyntaxError(Exception):
    def __init__(self):
        pass

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
    self.globalSymbolTable = self.initSymbolTable()
    self.localSymbolTable = []

    # function이나 class앞의 template이나 attribute같은 것들의 정보를 가지고 있는...
    self.directive = []
    
    # 아무것도 없으면 Root임
    self.namespaceStack = []
    self.loadedSymbolList = []

    self.mustcompile = []

  def initSymbolTable(self):
    symtbl = SymbolTable()
    
    symtbl.register({'@type':'namespace','@name':"System"})
    symtbl.register({'@type':'namespace','@name':"System.lang"})
    symtbl.register({'@type':'namespace','@name':"System.out"})

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
    symtbl.register({'@type':'class','@name':namespaceObject})

    symtbl.register({'@type':'class','@name':namespaceByte})
    symtbl.register({'@type':'class','@name':namespaceChar})
    symtbl.register({'@type':'class','@name':namespaceShort})
    symtbl.register({'@type':'class','@name':namespaceInt})
    symtbl.register({
      '@type':'native def',
      '@name':namespaceInt + '.=',
      '@args':[ASTType(namespaceInt)],
      '@vtype':ASTType(namespaceInt),
      '@method':lambda se,dst: ASTNativeMove(se, dst)})
    symtbl.register({
      '@type':'native def',
      '@name':'+',
      '@args':[ASTType(namespaceInt), ASTType(namespaceInt)],
      '@vtype':ASTType(namespaceInt),
      '@method':lambda src1,src2: ASTNativeAdd(src1, src2)})
    symtbl.register({
      '@type':'native def',
      '@name':'+=',
      '@args':[ASTType(namespaceInt), ASTType(namespaceInt)],
      '@vtype':ASTType(namespaceInt),
      '@method':lambda se,dst: ASTNativeMove(se, ASTNativeAdd(src, dst))})
    symtbl.register({'@type':'class','@name':namespaceLong})
    symtbl.register({'@type':'class','@name':namespaceFloat})
    symtbl.register({'@type':'class','@name':namespaceDouble})
    symtbl.register({'@type':'class','@name':namespaceString})
    symtbl.register({'@type':'class','@name':namespaceBoolean})
    symtbl.register({'@type':'class','@name':namespaceArray})
    symtbl.register({
        '@type':'def',
        '@name':"System.lang.Array.length", 
        '@args':None, 
        '@vtype':ASTType(name="System.lang.Integer", templ = None, ranks = None)})
    symtbl.register({
        '@type':'def',
        '@name':"System.lang.Array.toRange", 
        '@args':None, 
        '@vtype':ASTType(name="System.lang.Array", templ = None, ranks = None)})
    symtbl.register({
        '@type':'def',
        '@name':"System.lang.Array.getNext",
        '@args':None, 
        '@vtype':ASTType(name="System.lang.Integer", templ = None, ranks = None)})
    symtbl.register({
        '@type':'def',
        '@name':"System.lang.Array.end",
        '@args':None, 
        '@vtype':ASTType(name="System.lang.Boolean", templ = None, ranks = None)})
    symtbl.register({'@type':'alias', '@name':"object", '@fullname':namespaceObject})
    symtbl.register({'@type':'alias', '@name':"byte", '@fullname':namespaceByte})
    symtbl.register({'@type':'alias', '@name':"short", '@fullname':namespaceShort})
    symtbl.register({'@type':'alias', '@name':"int", '@fullname':namespaceInt})
    symtbl.register({'@type':'alias', '@name':"float", '@fullname':namespaceFloat})
    symtbl.register({'@type':'alias', '@name':"double", '@fullname':namespaceDouble})
    symtbl.register({'@type':'alias', '@name':"string", '@fullname':namespaceString})
    symtbl.register({'@type':'alias', '@name':'bool', '@fullname':namespaceBoolean})
    symtbl.register({'@type':'alias', '@name':"string", '@fullname':namespaceString})

    symtbl.register({
        '@type':'def',
        '@name':'System.out.println',
        '@args':[ASTType(name=namespaceString, templ = None, ranks = None)],
        '@vtype':ASTType(name="void", templ = None, ranks = None)})

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

  def parse(self):
    if self.isdebug == 1:
      print "entering parse"

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

    if self.isdebug == 1:
      print "ending parse"
   
  def parseNamespace(self):
    if not self.match('namespace'):
      return 

    path = self.getNames()

    self.namespaceStack.append(path)
    self.loadedSymbolList.append(set([]))
    self.parseNamespaceBody()
    self.loadedSymbolList.pop()
    self.namespaceStack.pop() # symbol search할때도 사용할예정

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
    classname = ".".join(self.namespaceStack + [names])

    # 검색 symbol list에 등록만 해놓는다. 
    # 정의가 안되어 있다가 나중에 사용되면 실제 symbol table에 body가 없으므로,
    # body가 없다고 에러를 내면 된다.
    # self.loadedSymbolList와 self.namespaceStack은 단지 symbol을 만들때와 symbol참조를 위해서만 쓰인다.
    self.loadedSymbolList[-1] |= set([classname])
    if self.match(';'):
      return 

    self.namespaceStack.push(name)
    body = self.parseClassBody()
    self.namespaceStack.pop()

    symtbl = self.getRecentSymbolTable()
    # class의 body는 variable만 있어야 한다. 
    # class의 method들은 symbol로 등록될 것 이다.
    symtbl.registerSymbol({"@type": "class", "@name": classname, "@attribute": None, "@body": body})

  def parseClassBody(self):
    if not self.match('{'):
      return

    body = {}
    while not self.match('}'):
      if self.match('val'): # 상수선언
        name = self.getName()
        if body.has_key(name):
          print "Error) duplicated name :", name
          raise NameError

        content = {"@type": "val", "@vtype": ASTType("System.lang.Integer")}
      
        if self.match(':'):
          content['@vtype'] = self.parseType()
      
        if self.match('='):
          content['@init'] = self.parseInitExpr()

        body[name] = content
      elif self.match('var'):   # 변수선언
        name = self.getName()
        if body.has_key(name):
          print "Error) duplicated name :", name
          raise NameError

        content = {"@type": "var", "@vtype": ASTType("System.lang.Integer")}
      
        if self.match(':'):
          content['@vtype'] = self.parseType()
      
        if self.match('='):
          content['@init'] = self.parseInitExpr()

        body[name] = content
      elif self.match('def'):   # 함수
        name = self.getName()

        # 인자까지 봐야지 중복인지를 체크할 수 있음
        content = {"@type": "def"}
        if self.match('('):
          args = self.parseDefArgsList()
          if not self.match(')'):
            print "Error) Needed ')'"
            raise SyntaxError
          content['@args'] = args

        if self.match(':'): # return type
          type = self.parseType()
          content['@vtype'] = type
        else:
          content['@vtype'] = None # return이 없음을 의미 (c의 void)

        if self.match('='):
          defbody = self.parseExpr()
          content['@body'] = defbody
        elif self.match('{'):
          defbody = self.parseExprs()
          if not self.match('}'):
            print "Error) Needed '}'"
            raise SyntaxError
          content['@body'] = defbody
        else:
          print "Error) Needed Body"
          raise SyntaxError

        # 함수이름을 native symbol로 변경
        realn = convertToNativeSymbol(name, content['@args'], content['@vtype'])
        # TODO : Auto Casting은 일단 지원하지 않는다.
        if body.has_key(realn):
          print "Error) Multiple declaration :", fname
          raise SyntaxError

        body[realn] = content

    return body

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
      print "Error) Needs some template parameters"
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
    return ".".join(self.namespaceStack + [fn])

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
    only = self.getNames()
    fn = ".".join(self.namespaceStack + [only])

    #print "Function name : %s" % (fn)

    # 함수용 local symbol table을 만듭니다.
    self.localSymbolTable = [{}]
    
    # argument가 나오는지 검사합니다.
    args = self.parseDefArgsList()

    # check
    localSymTbl = self.localSymbolTable[-1]
    for arg in args:
      if localSymTbl.has_key(arg.name):
        print "Error) Duplicated Name"
        raise SyntaxError

      if not self.globalSymbolTable.findType(arg.type.name):
        print "Error) Unknown Type"
        raise SyntaxError

      localSymTbl[arg.name] = arg.type

    nativeSymbol = mangling(fn, args)
    if self.globalSymbolTable.find({'@type': 'def', '@name': fn, '@args': args}):
      print "Error) Duplicated Name"
      raise Exception("Error", "Error")
    #localSymTbl.printDoc()

    # To parse return type
    rettype = self.parseReturnType()

    # To parse body of function
    body = self.parseDefBody()
    if body == None:
      print "Error) Body Empty : in %s" % (nativeSymbol)
      raise Exception("Error", "Error")
      
    if rettype != 'void':
      if isinstance(body, ASTExpr):
        body = ASTReturn(body)
      else:
        # return을 명시적으로 적지 않았다면, 마지막 expression의 결과를 return값으로 한다.
        lastExpr = body.exprs[-1]
        if not isinstance(lastExpr, ASTReturn):
          body.exprs[-1] = ASTReturn(lastExpr)

    # 바로전에 template이 선언되었다면 여기도 영향을 받아야만 한다.
    # 일단 지금은 영향을 받지 않는다고 가정한다.
    self.globalSymbolTable.register({
      "@type": "def",
      "@name": fn,
      "@args": args,
      "@vtype": rettype,
      "@body": body,
      "@symbols": self.localSymbolTable})

    self.localSymbolTable = [{}]

    print nativeSymbol, self.globalSymbolTable[nativeSymbol]
    self.mustcompile.append((self.globalSymbolTable[nativeSymbol], nativeSymbol))

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
      print "Error) Needed ')'"
      return None

    return args

  def parseReturnType(self):
    # if return type is none,
    if not self.match(':'):
      return ASTType(name = "System.lang.Integer", templ = None, ranks = None)

    return self.parseType()

  def parseDefArg(self):
    name = self.getName()
    if name == None: 
      return None

    typeStr = ASTType(name = "System.lang.Integer", templ = None, ranks = None)
    if self.match(':'): 
      typeStr = self.parseType()

    defval = None
    if self.match('='):
      defval = self.parseBasicSimpleExpr()

    # if typeStr == None: makeError
    return ASTDefArg(name = name, type = typeStr, defval = defval)

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
    type = self.globalSymbolTable.findType(idStr)
    if type == None:
      print "Unknown Type : %s" % (idStr)
      sys.exit(-1)

    if type == 'alias':
      idStr = self.globalSymbolTable.find(idStr)
      print "(", idStr

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

    return ASTType(name = idStr, templ = None, ranks = rank)

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
      if ret == None: 
        continue
      if isinstance(ret, ASTExprs):
        lst += ret.exprs
      elif isinstance(ret, list):
        lst += ret
      else:
        # ??
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

  def convertToASTType(self, obj):
    if isinstance(obj, ASTType):
      return obj
    elif isinstance(obj, ASTWord) and obj.vtype != None:
      return obj.vtype
    elif isinstance(obj, ASTWord) and isinstance(obj.type, ASTType):
      return obj.type
    elif isinstance(obj, ASTListGenerateType1):
      return ASTType('System.lang.Array')
    else:
      print "**", obj
      raise NotImplementedError

  def parseVar(self):
    if not self.match('var'):
      return None

    sym = self.localSymbolTable[-1]
    
    hist = []
    while True:
      name = self.getName()
      if sym.has_key(name):
        print "has duplicated name"
        raise Exception('Error', 'Duplicated Name')
        return None

      type = None
      if self.match(':'):
        type = self.parseType()
      else:
        type = ASTType(name = 'System.lang.Integer', templ = None, ranks = None)

      #print "name =", name

      # 변수 초기화
      tree = None
      if self.match('='):
        query = {"@name": '=', '@type': 'def'}
        query['@args'] = [type, self.convertToASTType(self.parseSimpleExpr())]
        symbol = self.globalSymbolTable.find(query)
        print symbol

        tree = ASTOperator(ASTWord('id', '='), ASTWord('id', name, type), self.parseSimpleExpr())
        hist.append(tree)

      sym[name] = {"@type": "var", "@vtype": type}
      if not self.match(','):
        break

    self.match(';')

    return hist

  def parseVal(self):
    if not self.match('val'):
      return None

    sym = self.localSymbolTable[-1]
    
    hist = []
    while True:
      name = self.getName()
      if sym.has_key(name):
        print "has duplicated name"
        raise Exception('Error', 'Duplicated Name')
        return None

      type = None
      if self.match(':'):
        type = self.parseType()
      else:
        type = ASTType(name = 'System.lang.Integer', templ = None, ranks = None)

      #print "name =", name

      # 변수 초기화
      tree = None
      if self.match('='):
        query = {"@name": '=', '@type': 'def'}
        query['@args'] = [type, self.convertToASTType(self.parseSimpleExpr())]
        symbol = self.globalSymbolTable.find(query)
        print symbol

        tree = ASTOperator(ASTWord('id', '='), ASTWord('id', name, type), self.parseSimpleExpr())
        hist.append(tree)

      sym[name] = {"@type": "var", "@vtype": type}
      if not self.match(','):
        break

    self.match(';')

    return hist


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
  
          # Global Operator 함수로 첫번째 찾는다. (C++의 operator + (left, right)라는 식..)
          content = {'@type': 'def', '@name': tok.value}
          content['@args'] = [self.convertToASTType(tree), self.convertToASTType(right)]
          symbol = self.globalSymbolTable.find(content)
          if symbol == None:
            # 없다면, left.type의 operator로 찾는다. (C++의 someclass::operator + (right)...)
            content = {'@type': 'def', '@name': self.convertToASTType(tree) + "." + tok.value}
            content['@args'] = [self.convertToASTType(right)]
            symbol = self.globalSymbolTable.find(content)

          print symbol, content
          if symbol != None:
            if symbol['@type'] == 'native def':
              raise NotImplementedError
            else:
              tree = ASTFuncCall(content['@name'], tree, right)
          elif symbol == None:
            tree = ASTOperator(ASTWord(tok.type, tok.value), tree, right)
            
      # array
      elif self.sameType('id'):
        #if isinstance(tree, ASTSet):
        #  #if len(tree.lst) != 1:
        #  #  print "error!!" # make error!!
        #  if self.checktype(tree.lst[0]):
        #    tree = ASTCasting(tree.lst[0], ASTWord(tok.type, tok.value))
        tokVal = self.getTokValue()
        tokType = self.getTokType()

        mid = ASTWord(tokType, tokVal)

        self.token.nextToken()

        right = self.parseBasicSimpleExpr()
        print "here : ", mid, tree, right
        if right != None:
          content = {'@type': 'def', '@name': tokVal}
          content['@args'] = [self.convertToASTType(tree), self.convertToASTType(right)]
          symbol = self.globalSymbolTable.find(content)
          if symbol == None:
            # 없다면, left.type의 operator로 찾는다. (C++의 someclass::operator + (right)...)
            content = {'@type': 'def', '@name': self.convertToASTType(tree) + "." + tokVal}
            content['@args'] = [self.convertToASTType(right)]
            symbol = self.globalSymbolTable.find(content)

          if symbol != None:
            if symbol['@type'] == 'native def':
              raise NotImplementedError
            else:
              tree = ASTFuncCall(content['@name'], [tree, right])
          else:
            tree = ASTOperator(mid, tree, right)
        else:
          # for example, 'a++' or 'a+'
          tree = ASTUnary(tree, mid)
      else:
        break

    if isinstance(tree, ASTFuncCall):
      candidates = set([])      

      path = None
      if isinstance(tree, ASTNames):
        path = ".".join(tree.name.array)
      else:
        path = tree.name

      ret = self.globalSymbolTable.find({'@type':'def', '@name':path, '@args':tree.args})
      if ret == None:
        print "Error) Not Symbol :", path
        raise SyntaxError
     
    if self.isdebug == 1:
      print "ending parseSimpleExpr()"

    return tree

  def parseBasicSimpleExpr(self):
    tok = self.token.tok
    if tok == None: return None
    #print "calling parseBasicSimpleExpr"
    #print "value =", tok.value, tok.type
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
        return ASTListGenerateType1(ASTWord(tok.type, tok.value), right) # 여기서 빠진 것은 Arrya<T이어야 한다는 사실(Type이 빠졌다는 소리)
      else:
        vtype = None
        for symbolTable in reversed(self.localSymbolTable):
          if symbolTable.has_key(tok.value):
            vtype = symbolTable[tok.value]
            break

        if vtype == None:
          vtype = self.globalSymbolTable.findType([tok.value])

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
    #else:
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
          if not symtbl.has_key(arg.value):
            print "Error) Not found :", arg.value
            raise SyntaxError
          
          args.append(ASTCalleeArgType1(value = arg, type = symtbl[arg.value]))
        else:
          args.append(ASTCalleeArgType1(value = arg, type = arg.type))
      else:
        print arg
        raise NotImplementedError

      if not self.match(','):
        break

    return args
