#!/usr/bin/env python
# -*- coding: utf-8 -*-
from mangle import *
from ASTType import *

class SymbolType(object):
  def __init__(self, name):
    self.name = name

  def find(self, path = None, fn = None, args = None):
    raise NotImplementedError
        
class NamespaceSymbol(SymbolType):
  def __init__(self):
    super(NamespaceSymbol, self).__init__("namespace")

class ClassSymbol(SymbolType):
  def __init__(self):
    super(ClassSymbol, self).__init__("class")
        
class FunctionSymbol(SymbolType):
  def __init__(self, args, retType, body, native=False):
    super(FunctionSymbol, self).__init__("function")
    self.args = args
    self.retType = retType
    self.body = body
    self.native = native
    
  def find(self, path = None, fn = None, args = None):
    return []
    
class VariableSymbol(SymbolType):
  def __init__(self, type):
    super(VariableSymbol, self).__init__("variable")
    self.type = type

  def find(self, path = None, fn = None, args = None):
    return []
 
class ValueSymbol(SymbolType):
  def __init__(self, type):
    super(ValueSymbol, self).__init__("value")
    self.type = type

  def find(self, path = None, fn = None, args = None):
    return []
 
# native인지 구별할 필요가 있어야 한다.
# native의 의미는 C++에서 제작된 것으로 Bear 언어로 별도로 된 body가 없다는 뜻.    
# TODO: Class, Struct, Function등에 대해서 native에 대한 정의를 담을 수 있는 변수 또는 어떠한 장치 필요 
class SymbolTable:
    def __init__(self):
        self.symbolTable = {}   # 무조건 Native형태로...
        self.symbolDict = {}
        self.aliasSymbolTable = {}
       
    def set(self, path, content):
        d   = path.split('.')
        nd  = len(d)

        now = self.symbolDict
        for p,n in enumerate(d):
          if p+1 == nd:
            if not now.has_key(n):
              now[n] = content
              return True
            else:
              return False
          elif not now.has_key(n):
            now[n] = {}
          now = now[n]

        return False

    def findFunction(self, path, fn, args): 
        def checkFuncSym(info):
          if info.args == None:
            # 함수의 선언시 void로 했는데, callee는 인자가 있다.
            # 이런 경우는 아예 매치가 안된 것임
            if args != None and len(args) != 0:
              return None
            elif (args != None and len(args) == 0) or args == None:
              return info # 둘다 인자가 없고, 여기에 들어오는 경우는 함수가 일치할때 뿐이므로, return을 한다.
            else:
              raise Exception('Error', 'checkFuncSym') # 이곳으로 들어오는 경우가 있으려나??
          
          # 만일 callee의 인자가 없다면, callee의 선언에 default value가 첫인자부터 설정되어 있는지 체크한다. 
          if args == None or (args != None and len(args) == 0):
            # 최초의 인자가 default value를 가지고 있지 않다면, non-matched이다.
            arg = info.args[0]
            if arg.defval == None:
              return None 
            
            # 기본적으로 최초의 default value이후의 나머지 인자들은 모두 default value여야 한다. 그러므로, 이 호출은 정당해진다. 
            return info

          # c++의 default value를 따름(TODO python만큼은 나중에 지원)
          for n, arg in enumerate(info.args):
            print arg, args[n].value.type
            if arg == args[n].value.type:
              continue

            # TODO type이 서로 다르면, 한쪽에서 다른 쪽으로 변환이 가능한지에 대한 체크가 필요하다. 
            return None

          # 인자가 같은지 검사
          # default value를 고려해야한다. 
          #candidates.append(funcSym)
          return info
          
        print "starting findFunction : ", path, fn, args

        names = path.split('.')
        n_names = len(names)

        candidates = []

        now = self.symbolDict
        for ns in names:
          if not now.has_key(ns):
            return None

          now = now[ns]

        if not now.has_key(fn):
          return None

        target = now[fn]
        if isinstance(target, list): # overloaded
          for element in target:
            info = checkFuncSym(element)
            if info != None:
              candidates.append(info)
        elif isinstance(target, dict):
          raise Exception('Error', 'dict')
        elif isinstance(target, FunctionSymbol):
          info = checkFuncSym(target)
          if info != None: 
            candidates.append(info)
        else:
          print target
          raise Exception('Error', 'other instances')
        
        return candidates

    # path는 "System.lang...."라는 식으로 들어와야 한다.
    def registerNamespace(self, path):
        symbol = encodeSymbolName(path)
        
        if self.symbolTable.has_key(symbol):
            return None
        
        self.symbolTable[symbol] = {"@type": "namespace"}
        self.set(path, self.symbolTable[symbol])
        return self.symbolTable[symbol]
    
    def registerClass(self, path):
        symbol = encodeSymbolName(path)
        
        if self.symbolTable.has_key(symbol):
            return None
        
        self.symbolTable[symbol] = {"@type": "class"}
        self.set(path, self.symbolTable[symbol])
        return self.symbolTable[symbol]
    
    def registerFunction(self, path, args = None, retType = None, body = None):
        symbol = encodeSymbolName(path, args)
        
        if self.symbolTable.has_key(symbol):
            return None
        
        # body가 null이면 native function으로 취급한다.
        self.symbolTable[symbol] = FunctionSymbol(args, retType, body)
        self.set(path, self.symbolTable[symbol])
        return self.symbolTable[symbol]

    def registerNativeFunction(self, path, args = None, retType = None):
        symbol = encodeSymbolName(path, args)
        
        if self.symbolTable.has_key(symbol):
            return None
        
        # body가 null이면 native function으로 취급한다.
        self.symbolTable[symbol] = FunctionSymbol(args, retType, None, native=True)
        self.set(path, self.symbolTable[symbol])
        return self.symbolTable[symbol]
       
    def registerAliasSymbol(self, shortName, longName):
        self.aliasSymbolTable[shortName] = longName
        self.symbolTable[shortName] = {"@type": "alias", "@long": longName}
        self.set(longName, self.aliasSymbolTable[shortName])
        return self.aliasSymbolTable[shortName]

    def registerVariable(self, name, type):
        if self.symbolTable.has_key(name):
            return None
        
        self.symbolTable[name] = VariableSymbol(type)
        self.set(name, self.symbolTable[name])
        return self.symbolTable[name]
    
    def getRealname(self, path):
        _path = path
        if self.aliasSymbolTable.has_key(_path):
            _path = self.aliasSymbolTable[_path]
        
        if self.symbolTable.has_key(_path):
            return _path
        elif self.symbolTable.has_key(encodeSymbolName(_path)):
            return _path
        
        return None

    def searchNative(self, path):
        if self.symbolTable.has_key(path):
            return path
        
        return None
        
    def __getitem__(self, k):
        if self.symbolTable.has_key(k):
            return self.symbolTable[k]
        
        return None
    
    def __setitem__(self, k, v):
        self.symbolTable[k] = v
        
    def has_key(self, k):
        return self.symbolTable.has_key(k)
