#!/usr/bin/env python
# -*- coding: utf-8 -*-
from mangle import *
from ASTType import *

class SymbolType(object):
    def __init__(self, name):
        self.name = name
        
class NamespaceSymbol(SymbolType):
    def __init__(self):
        super(NamespaceSymbol, self).__init__("namespace")
        
class ClassSymbol(SymbolType):
    def __init__(self):
        super(ClassSymbol, self).__init__("class")
        
class FunctionSymbol(SymbolType):
    def __init__(self, args, retType, body):
        super(FunctionSymbol, self).__init__("function")
        self.args = args
        self.retType = retType
        self.body = body
        
class VariableSymbol(SymbolType):
    def __init__(self, type):
        super(VariableSymbol, self).__init__("variable")
        self.type = type

class ValueSymbol(SymbolType):
    def __init__(self, type):
        super(ValueSymbol, self).__init__("value")
        self.type = type
        
class SymbolTable:
    def __init__(self):
        self.symbolTable = {}   # 무조건 Native형태로...
        self.aliasSymbolTable = {}
        
    # path는 "System.lang...."라는 식으로 들어와야 한다.
    def registerNamespace(self, path):
        symbol = encodeSymbolName(path)
        
        if self.symbolTable.has_key(symbol):
            return None
        
        self.symbolTable[symbol] = NamespaceSymbol()
        return self.symbolTable[symbol]
    
    def registerClass(self, path):
        symbol = encodeSymbolName(path)
        
        if self.symbolTable.has_key(symbol):
            return None
        
        self.symbolTable[symbol] = ClassSymbol()
        return self.symbolTable[symbol]
        
    def registerFunction(self, path, args = None, retType = None, body = None):
        symbol = encodeSymbolName(path, args)
        
        if self.symbolTable.has_key(symbol):
            return None
        
        # body가 null이면 native function으로 취급한다.
        self.symbolTable[symbol] = FunctionSymbol(args, retType, body)
        return self.symbolTable[symbol]
        
    def registerAliasSymbol(self, shortName, longName):
        self.aliasSymbolTable[shortName] = longName
        return self.aliasSymbolTable[shortName]

    def registerVariable(self, name, type):
        if self.symbolTable.has_key(name):
            return None
        
        self.symbolTable[name] = VariableSymbol(type)
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