#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os, sys, string
from .mangle import *

# The information about a symbol in symbol table has information (and body if the type of that is a function.    
class SymbolInfo:
    TYPE_NONE = 0
    TYPE_DEF = 1 # function
    TYPE_VAR = 2 # variable
    TYPE_CONSTANT = 3 # constant variable
    TYPE_NAMESPACE = 4
    TYPE_CLASS = 5
    TYPE_STRUCT = 6
    TYPE_ENUM = 7
    
    def __init__(self):
        self.type = SymbolInfo.TYPE_NONE
        self.native = False

    def getType(self):
        return self.type

    def isNativeAttribute(self):
        return self.native

class DefSymbolInfo(SymbolInfo):
    def __init__(self, isNative = False, info = None):
        self.type = SymbolInfo.TYPE_DEF
        self.native = isNative
        self.info = info

class VarSymbolInfo(SymbolInfo):
    def __init__(self, isNative = False, varType = "System.lang.Int", initCode = None):
        self.type = SymbolInfo.TYPE_VAR
        self.native = isNative
        self.varType = varType
        self.initCode = initCode

class ConstantSymbolInfo(SymbolInfo):
    def __init__(self, isNative = False, varType = "System.lang.Int", initCode = None):
        self.type = SymbolInfo.TYPE_VAR
        self.native = isNative
        self.varType = varType
        self.initCode = initCode
        
class NamespaceSymbolInfo(SymbolInfo):
    def __init__(self, isNative = False):
        self.type = SymbolInfo.TYPE_NAMESPACE
        self.native = isNative

class ClassSymbolInfo(SymbolInfo):
    def __init__(self, isNative = False, parent = None):
        self.type = SymbolInfo.TYPE_CLASS
        self.native = isNative
        self.parent = parent

class StructSymbolInfo(SymbolInfo):
    def __init__(self, isNative = False):
        self.type = SymbolInfo.TYPE_CLASS
        self.native = isNative

class EnumSymbolInfo(SymbolInfo):
    def __init__(self, isNative = False):
        self.type = SymbolInfo.TYPE_ENUM
        self.native = isNative

class SymbolTable:
    ERROR_NONE = 0
    ERROR_ALREADY_REGISTERED = 1
    ERROR_NOT_REGISTERED = 2
    
    def __init__(self):
        self.dict = {}
        self.local = []

        self.registerPredefinedSymbols()

    # 아래 두 함수의 return은 dict로만...
    def getGlobalSymbolTable(self):
        return self.dict

    def getWorkingSymbolTable(self):
        if len(self.local) == 0:
            return self.dict

        return self.local[-1]

    def convertToMachineName(self, pathStr, argsStr):
        name = convertSimpleTypeName(pathStr)
        return name + "E" + argsStr
    
    def registerPredefinedSymbols(self):
        namespaceObject = "System.lang.Object"
        namespaceByte = "System.lang.Byte"
        namespaceChar = "System.lang.Char"
        namespaceShort = "System.lang.Short"
        namespaceInt = "System.lang.Int"
        namespaceLong = "System.lang.Long"
        namespaceFloat = "System.lang.Float"
        namespaceDouble = "System.lang.Double"
        namespaceString = "System.lang.String"

        # ****** 기계어로 번역은 (당연한 거지만) function만...
        self.registerSymbol(convertNamespace(namespaceObject), [], None, ClassSymbolInfo(isNative = True))
        # to get type's name
        self.registerSymbol(convertNamespace(namespaceObject + ".getName"), [], namespaceString, DefSymbolInfo(isNative = True))
        # to convert type information to string
        self.registerSymbol(convertNamespace(namespaceObject + ".toString"), [], namespaceString, DefSymbolInfo(isNative = True))

        commonAncient = [namespaceObject]
        
        #self.registerSymbol(namespaceByte, [], ClassSymbolInfo(isNative = True, parent = commonAncient))
        #self.registerSymbol(namespaceShort, [], ClassSymbolInfo(isNative = True, parent = commonAncient))
        # 입력 범위를 줄이기 위해서...
        self.registerSymbol(convertNamespace(namespaceInt), None, None, ClassSymbolInfo(isNative = True, parent = commonAncient))
        self.registerSymbol(convertNamespace(namespaceInt + ".+"), [namespaceInt], namespaceInt, DefSymbolInfo(isNative = True))
        self.registerSymbol(convertNamespace(namespaceInt + ".="), [namespaceInt], namespaceInt, DefSymbolInfo(isNative = True))
        #self.registerSymbol("System.lang.Float", None, ClassSymbolInfo(isNative = True, parent = commonAncient))
        #self.registerSymbol("System.lang.Double", None, ClassSymbolInfo(isNative = True, parent = commonAncient))
        #self.registerSymbol("System.lang.String", None, ClassSymbolInfo(isNative = True, parent = commonAncient))

        self.registerAliasSymbol("object", namespaceObject)
        self.registerAliasSymbol("byte", namespaceByte)
        self.registerAliasSymbol("short", namespaceShort)
        self.registerAliasSymbol("int", namespaceInt)
        self.registerAliasSymbol("float", namespaceFloat)
        self.registerAliasSymbol("double", namespaceDouble)
        self.registerAliasSymbol("string", namespaceString)

    def registerSymbol(self, pathStr, args, ends, info):
        if args == None:
            args = []
            
        # 3개를 다 받아서 abi format에 맞게 이름 변경
        encodedName = encodeSymbol(pathStr, args, ends)

        d = self.getWorkingSymbolTable()
        if encodedName in d:
            return SymbolTable.ERROR_ALREADY_REGISTERED

        d[encodedName] = {"encoded": encodedName, "alias": False, "info": info}
        return SymbolTable.ERROR_NONE
    
    def registerAliasSymbol(self, fpath, originalPath):
        d = self.getWorkingSymbolTable()
        d[fpath] = {"alias": True, "original": originalPath}
        return SymbolTable.ERROR_NONE

    # search는 local symbol table부터 차례대로 검사한다.
    def searchTable(self, tbl, name):
        if tbl == None: return None

        if name not in tbl:
            return None

        v = tbl[name]
        if v['alias']:
            return v['original']

        return v

    def search(self, name):
        for tbl in self.local:
            r = self.searchTable(tbl, name)
            if r != None:
                return r

        # None이 return으로 잡혀도 그냥 return 한다.
        return self.searchTable(self.dict, name)

    def searchSymbol(self, name):
        return self.search(name)

    # local symbol table만...
    def push(self):
        # 마지막에 hash하나 삽입하면 끝...
        self.local.append({})

    def pop(self):
        # 마지막꺼 삭제하면 끝...
        self.local.pop()
    