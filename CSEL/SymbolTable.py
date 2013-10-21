#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os, sys, string
from mangle import *

class NamespaceSymbol:
  def __init__(self, name):
    self.name = name
    self.child = {}

class ClassSymbol:
  def __init__(self, fname, name):
    self.fname = fname
    self.name = name
    # 이건 아직 미결정
    self.methods = {}
    self.properties = {}

class StructSymbol:
  def __init__(self, fname, name):
    self.fname = fname
    self.name = name
    # 이건 아직 미결정
    self.methods = {}
    self.properties = {}

class FunctionSymbol:
  def __init__(self, fname, name, args, rettype, body):
    self.fname = fname
    self.name = name
    self.args = args
    self.rettype = rettype
    self.body = body

class AliasSymbol:
  def __init__(self, fname, sname):
    self.shortName = sname
    self.name = fname

class VariableSymbol:
  def __init__(self, typeStr):
    self.type = typeStr

class TemplateFunctionSymbol:
  def __init__(self, templateargs, fname, name, args, rettype, body):
    self.templateargs = templateargs
    self.fname = fname
    self.name = name
    self.args = args
    self.rettype = rettype
    self.body = body

class TemplateArgumentSymbol:
  def __init__(self, name):
    self.name = name

class SymbolTable:
  def __init__(self):
    self.symbolTable = {}
    self.reverseSymbolTable = {}

    self.registerSymbol(pathStr = "System", typeStr = "namespace")
    self.registerSymbol(pathStr = "System.lang", typeStr = "namespace")

    namespaceObject = "System.lang.Object"
    namespaceByte = "System.lang.Byte"
    namespaceChar = "System.lang.Char"
    namespaceShort = "System.lang.Short"
    namespaceInt = "System.lang.Integer"
    namespaceLong = "System.lang.Long"
    namespaceFloat = "System.lang.Float"
    namespaceDouble = "System.lang.Double"
    namespaceString = "System.lang.String"

    # System.lang.Object
    self.registerSymbol(pathStr = namespaceObject, typeStr = "class")

    self.registerSymbol(pathStr = namespaceByte, typeStr = "class")
    self.registerSymbol(pathStr = namespaceChar, typeStr = "class")
    self.registerSymbol(pathStr = namespaceShort, typeStr = "class")
    self.registerSymbol(pathStr = namespaceInt, typeStr = "class")
    self.registerSymbol(pathStr = namespaceLong, typeStr = "class")
    self.registerSymbol(pathStr = namespaceFloat, typeStr = "class")
    self.registerSymbol(pathStr = namespaceDouble, typeStr = "class")
    self.registerSymbol(pathStr = namespaceString, typeStr = "class")

    self.registerAliasSymbol("object", namespaceObject)
    self.registerAliasSymbol("byte", namespaceByte)
    self.registerAliasSymbol("short", namespaceShort)
    self.registerAliasSymbol("int", namespaceInt)
    self.registerAliasSymbol("float", namespaceFloat)
    self.registerAliasSymbol("double", namespaceDouble)
    self.registerAliasSymbol("string", namespaceString)

  def getLastName(self, pathStrList):
    if len(pathStrList) == 1:
      return pathStrList[0]

    return pathStrList[-1]

  # pathStr은 항상 full namespace로 들어와야한다.
  def registerSymbol(self, pathStr, typeStr):
    last = self.getLastName(pathStr.split('.'))

    sym = None
    if typeStr == "namespace":
      sym = NamespaceSymbol(pathStr)
    elif typeStr == "class":
      sym = ClassSymbol(pathStr, last)
    #elif typeStr == "function":
    #  return FunctionSymbol(nameStr)
    #elif typeStr == "property" or typeStr == "variable":
    #  return VariableSymbol(nameStr)
    #elif typeStr == "enumerate":
    #  return EnumerateSymbol(nameStr)
    elif typeStr == "struct":
      return StructSymbol(pathStr, last)
    #elif typeStr == "template":
    #  return TemplateSymbol(nameStr)
    #elif typeStr == "object":
    #  return ObjectSymbol(nameStr)
    #elif typeStr == "trait":
    #  return TraitSymbol(nameStr)

    ret = self.registerSomething(pathStr, sym)
    if ret == None:
      return False

    return True

  def registerVariable(self, name, type):
    if self.has_key(name):
      return False

    self.symbolTable[name] = VariableSymbol(type)
    return True

  def registerFunction(self, fname, args, rettype, body):
    if self.has_key(fname):
      return False

    # TODO : fname 채워넣어야함
    last = self.getLastName(fname.split('.'))
    self.registerSomething(fname, FunctionSymbol(fname = fname, name = last, args = args, rettype = rettype, body = body))

  def registerTemplateArgument(self, name, type):
    if self.has_key(name):
      return False

    self.symbolTable[name] = TemplateArgumentSymbol(name)
    return True

  def registerTemplateFunction(self, templateargs, fname, args, rettype, body):
    if self.has_key(fname):
      return False

    # TODO : fname 채워넣어야함
    last = self.getLastName(fname.split('.'))
    self.registerSomething(fname, TemplateFunctionSymbol(templateargs = templateargs, fname = fname, name = last, args = args, rettype = rettype, body = body))

  def registerAliasSymbol(self, shortName, pathStr):
    sym = self.reverseSymbolTable
    if not sym.has_key(shortName):
      sym[shortName] = AliasSymbol(pathStr, shortName)
      return True

    return True

  # symbol table에 등록하는 방법
  # 만약 System.lang.Integer를 등록하고 싶으면,
  # 등록 순서는
  # 1. System
  # 2. lang
  # 3. Integer
  # 로 되어야 한다.
  def registerSomething(self, pathStr, body):
    if self.reverseSymbolTable.has_key(pathStr):
      alias = self.reverseSymbolTable[pathStr]
      if isinstance(alias, AliasSymbol):
        pathStr = alias.name

    seps = pathStr.split('.')

    last = self.getLastName(seps)
    fronts = seps[:-1]

    sym = self.symbolTable
    for name in fronts:
      if sym.has_key(name):
        sym = sym[name].child
      else:
        return None

    if not sym.has_key(last):
      if body == None:
        return None

      sym[last] = body

    return sym[last]

  def findLoc(self, pathStr):
    return self.registerSomething(pathStr, None)

  def has_key(self, name):
    sym = self.findLoc(name)
    if sym == None: 
      return False

    return True

  def __getitem__(self, pathStr):
    return self.findLoc(pathStr)

  def printStr(self, doc):
    if isinstance(doc, NamespaceSymbol):
      for keyStr in doc.child:
        print "%s" % (keyStr)
        self.printStr(doc.child[keyStr])
    elif isinstance(doc, ClassSymbol):
      for keyStr in doc.methods:
        print "%s" % (keyStr)
      for keyStr in doc.properties:
        print "%s" % (keyStr)

  def printDoc(self):
    print "Symbol)"
    
    for keyStr in self.symbolTable:
      print "keyStr : %s" % (keyStr)
      self.printStr(self.symbolTable[keyStr])

  def getRealName(self, name):
    if self.reverseSymbolTable.has_key(name):
      alias = self.reverseSymbolTable[name]
      if isinstance(alias, AliasSymbol):
        return alias.name

    return name

  def genSymbolStringWithTemplate(self, base, templ):
    raise Exception("genSymbolStringWithTemplate", "Not implemented")
