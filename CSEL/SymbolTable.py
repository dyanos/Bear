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
        print "starting findFunction : ", path, fn, args

        names = path.split('.')
        n_names = len(nslst)

        now = self.symbolDict
        for p, ns in names:
            if not now.has_key(ns):
                return None

            if isinstance(now[ns], FunctionSymbol):
                funcSym = now[ns]

                iscomplete = 0  # 0 is completed, 1 is that variables has default value, -1 is not equal
                for n, arg in enumerate(funcSym.args):
                  if arg.type != args[n].type: 
                    iscomplete = -1
                    break

                if iscomplete != 0:
                  continue

                # 인자가 같은지 검사
                # default value를 고려해야한다. 

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
