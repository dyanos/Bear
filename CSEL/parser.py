#!/usr/bin/env pythone
# -*- coding: utf-8 -*-
import traceback

from Token import *

from AST import *
from ASTAlias import *
from ASTArgItem import *
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
from SymbolTable import *
from IR import *
from mangle import *

import copy
import random

sourceSets = []

class Parser:
  def __init__(self, fn):
    self.isdebug = True

    self.directive = []

    self.token = Token(fn)
    self.token.nextToken()

    # Root Symbol Table 등록
    self.stackSymbolList = [SymbolTable()]
    # 아무것도 없으면 Root임
    self.depthNamespaceString = []

    self.mustcompile = []

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
      if elem.has_key(symbol):
        return elem[symbol]

    return False

  # list에 따로 들어있는 각각의 namespace, class, function, template, struct, property등을 하나로 합칩니다.
  def flattenSymbolList(self):
    root = self.getRootSymbolTable()
    # 일단 구현할께 function밖에 없으니 ...

  def parse(self):
    parsingList = []
    while not self.isEnd():
      tree = None
      
      if self.same('namespace'):
        raise Exception("parse", "namespace")
      elif self.same('class'):
        raise Exception("parse", "class")
      elif self.same('template'):
        result = self.parseTemplate()
      elif self.same('def'):
        info = self.parseDef()
        parsingList.append(tree)
        #print tree
        #print info['body']
        #info['body'].printXML()
        self.getRootSymbolTable().registerFunction(info['name'], info['args'], info['rettype'], info['body'])
        self.mustcompile.append(self.getRootSymbolTable()[info['name']])
      elif self.same('native'):
        # 예는 push로..
        self.directive.append(value)
        pass
      else:
        break

    self.flattenSymbolList()

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
    return ASTTEmplateArg(name, type)

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
  def combineNamespace(self, fn):
    if len(self.depthNamespaceString) == 0:
      return fn

    return ".".join(self.depthNamespaceString + [fn])

  def parseDef(self):
    if not self.match('def'):
      return None

    # 이름을 얻습니다.
    fn = self.combineNamespace(self.getNames())
    #print "Function name : %s" % (fn)

    # 함수용 symbol table을 만듭니다.
    self.stackSymbolList.append(SymbolTable())
    localSymTbl = self.getRecentSymbolTable()

    # argument가 나오는지 검사합니다.
    args = self.parseFuncArgumentList()
    for elem in args:
      typeTree = elem.type
      #print "symbol = %s" % (typeTree.name)
      if self.searchSymbol(typeTree.name):
        localSymTbl.registerVariable(elem.name, typeTree.name)
      else:
        print "Not found symbol"
        sys.exit(-1)

    #localSymTbl.printDoc()

    rettype = self.parseReturnType()

    if self.match('='):
      body = self.parseExpr()
      if rettype != 'void':
        body = ASTReturn(body)
    elif self.match('{'):
      body = self.parseExprs()
      self.match('}')
    else:
      body = None

    for directive in self.directive:
      if directive == 'native':
        pass

    self.directive = []

    ret = {'name': fn, 'rettype': rettype}
    if args == None:
      ret['body'] = body
    else:
      ret['args'] = args
      ret['body'] = body

    return ret

  def parseFuncArgumentList(self):
    if not self.match('('):
      return None

    args = []
    while not self.isEnd():
      arg = self.parseArgument()
      if arg == None: break
      args.append(arg)
      if not self.match(','): break

    self.match(')')

    return args

  def parseReturnType(self):
    # if return type is none,
    if not self.match(':'):
      return "System.lang.Integer"

    return self.parseType()

  def parseArgument(self):
    name = self.getName()
    if name == None: return None
    if not self.match(':'): 
      return ASTArgItem(name = name, type = "System.lang.Integer")
    typeStr = self.parseType()
    # if typeStr == None: makeError
    return ASTArgItem(name = name, type = typeStr)

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
    idStr = self.getNames()

    # 해당 type이 존재하는지 검사합니다.
    result = self.searchSymbol(idStr)
    if result == None:
      print "unknown type : %s" % (idStr)
      return None

    #print "result : ", result
    if isinstance(result, AliasSymbol):
      idStr = result.name
      result = self.searchSymbol(idStr)
    else:
      idStr = result.fname # 무조건 full name을 얻는다.

    tmpl = self.parseTemplatePart()
    if not self.matchTemplateInfo(result, tmpl):
      # 일단 현재는 pass
      print "Error) Not matched template information"
      pass

    #print "type's full name = %s" % (idStr)

    #tmpl  = self.parseTemplatePart()
    #ename, body = symbolTable.search(names.array)
    #if ename == None:
    #  print "doesn't exist symbol : %s" % (".".join(names.array))
    #  sys.exit(-1) # 일단 죽이고... 나중에 에러처리 생각
    #else:
    #  names.array = ename

    #rank  = self.parseRankList()
    whole = idStr
    return ASTType(name = whole, templ = None, ranks = None)

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
    tree = self.parseBasicSimpleExpr()
    if tree == None: return None
    while not self.isEnd():
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
            tree = ASTFuncCall(ASTNames(tree.array + [right.name.value]), right.body)
          elif isinstance(right, ASTIndexing):
            tree = ASTIndexing(ASTNames(tree.array + [right.name.value]), right.history)
        else:
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

      return ret
    elif self.matchType('id'): 
      if self.same('['):
        history = []
        while self.match('['):
          history.append(self.parseSimpleExpr())
          self.match(']')
        return ASTIndexing(ASTWord(tok.type, tok.value), history)
      elif self.match('('):
        args = self.parseArgumentList()
        self.match(')')
        return ASTFuncCall(ASTWord(tok.type, tok.value), args)
      elif self.match('...'):
        right = self.parseSimpleExpr()
        return ASTListGenerateType1(ASTWord(tok.type, tok.value), right)
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