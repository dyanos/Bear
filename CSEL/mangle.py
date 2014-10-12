#!/usr/bin/env pythone
# -*- coding: utf-8 -*-
import traceback
from random import Random

from AST import *
from ASTAlias import *
from ASTType import *
from ASTDefArg import *
from ASTArgList import *
from ASTAttribute import *
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

import re

# ms compiler용 mangling 함수 작성 필요 
enm = {      '_': 'v',
       'wchar_t': 'w',
          'bool': 'b',
          'char': 'c',
   'signed char': 'a',
 'unsigned char': 'h',
         'short': 's',
'unsigned short': 't',
           'int': 'i',
  'unsigned int': 'j',
          'long': 'l',
 'unsigned long': 'm',
     'long long': 'x',
       '__int64': 'x',
'unsigned long long': 'y',
      '__uint64': 'y',
      '__int128': 'n',
'unsigned __int128': 'o',
         'float': 'f',
        'double': 'd',
   'long double': 'e',
     '__float80': 'e',
    '__float128': 'g',
       'float64': 'Dd',
      'float128': 'De',
       'float32': 'Df',
       'float16': 'Dh',
      'char32_t': 'Di',
      'char16_t': 'Ds',
          'auto': 'Da',
'std::nullptr_t': 'Dn'}

longToShort = {
  "System.lang.Char": 'char',
  "System.lang.Short": 'short',
  "System.lang.Integer": 'int',
  "System.lang.Long": 'long',
  "System.lang.Float": 'float',
  'System.lang.Double': 'double'
}

operatorTransTbl = {
  "new": "nw",
  "new[]": "na",
  "delete": "dl",
  "delete[]": "da",
  "~": "co",
  "+": "pl",
  "-": "mi",
  "*": "ml",
  "/": "dv",
  "%": "rm",
  "&": "an",
  "|": "or",
  "^": "eo",
  "=": "aS",
  "+=": "pL",
  "-=": "mI",
  "*=": "mL",
  "/=": "dV",
  "%=": "rM",
  "&=": "aN",
  "|=": "oR",
  "^=": "eO",
  "<<": "ls",
  ">>": "rs",
  "<<=": "lS",
  ">>=": "rS",
  "==": "eq",
  "!=": "ne",
  "<": "lt",
  ">": "gt",
  "<=": "le",
  ">=": "ge",
  "!": "nt",
  "&&": "aa",
  "||": "oo",
  "++": "pp",
  "--": "mm",
  ",": "cm",
  "->*": "pm",
  "->": "pt",
  "()": "cl",
  "[]": "ix",
  "?": "qu",
}

eoperatorTransTbl = {
  # 얘네들은 나중에 특별취급
  "+(unary)": "ps",
  "-(unary)": "ng",
  "&(unary)": "ad",
  "*(unary)": "de",
  "sizeof(a type)": "st",
  "sizeof(an expression)": "sz",
  "alignof(a type)": "at",
  "alignof(an expression)": "az",
  "cast": "cv<type>",
  "vendor" : "v<digit><source-name>",
}

def validNamespaceName(name):
  if re.match(r'^(_|[a-zA-Z])[a-zA-Z0-9_]*$', name) and name != '_':
    return True

  return False

def convertPathToNative(name, options = None):
    # name의 유효성 검사 
    if not re.match(r'^((_|[a-zA-Z])[a-zA-Z0-9_]*\.)*(_|[a-zA-Z])[a-zA-Z0-9_]*$', name):
        return None
    
def convertNamespace_for_gcc(name, options):
  if not re.match(r'^((_|[a-zA-Z])[a-zA-Z0-9_]*\.)*((_|[a-zA-Z])[a-zA-Z0-9_]*|[~`!@#\$%\^\&\*\(\)\-_\+=\{\}\[\]\|\\:;"\'<>,\.\?\/]*)$', name):
    return None

  nameList = name.split('.')

  op = nameList[-1]
    
  # 마지막이 operator일 경우
  if operatorTransTbl.has_key(op):
    opName = operatorTransTbl[op]

    if options != None and options['unary']:
      if op == '+':
        opName = 'ps'
      elif op == '-':
        opName = 'ng'
      elif op == '&':
        opName = 'ad'
      elif op == '*':
        opName = 'de'
  elif re.match(r'^[~`!@#\$%\^\&\*\(\)\-_\+=\{\}\[\]\|\\:;"\'<>,\.\?\/]', op):
    raise Exception('Need to implement', op)

    return "".join(map(lambda x: "".join([str(len(x)), x]), nameList[:-2])) + opName 

  return "".join(map(lambda x: "".join([str(len(x)), x]), nameList))

def convertNamespace(namespace, options = None):
  return convertNamespace_for_gcc(namespace, options)

def convertName_for_gcc(name):
  if len(name) == 1:
    if name[0] == 'main':
      return '_main'
    else:
      return "__Z%d%s" % (len(name[0]), name[0])
  else:
    return "".join(["__ZN"] + map(lambda x: "".join([str(len(x)), x]), name) + ['E'])

def convertName(name):
  nameList = None
  if isinstance(name, list):
    nameList = name
  else:
    nameList = name.split('.') 
  #if option.compiler_type == 'gcc':
  return convertName_for_gcc(nameList)
  #elif option.compiler_type == 'msvc':
  # return convertName_for_msvc(tree)
  #else:
  # return convertName_for_other(tree)
 
def convertType_for_gcc(type):
  def __converting(name):
    if len(name) == 1:
      return '%d%s' % (len(name[0]), name[0])
    else:
      return "".join(map(lambda x: "".join([str(len(x)), x]), name))

  result = []
  # reference type도 쓸수있게먼가 조치를...
  # result = ["R"]
  if type.ranks != None:
    if len(type.ranks.ranks) != 0:
      result = ["P"] * len(type.ranks.ranks)

  array = None
  if isinstance(type.name, list):
    array = type.name
  else:
    array = type.name.split('.')
    
  pathStr = ".".join(array)
  if longToShort.has_key(pathStr):
    array = [longToShort[pathStr]]
  
  cnt = len(array)
  if cnt == 1:
    name = array[0]
    if not enm.has_key(name):
      result += [__converting(array)]
    else:
      result += [enm[name]]
  else:
    result += ["N" +  __converting(array)]

  if type.templ != None:
    result += ["I"]
    for item in type.templ.history:
      tmp = convertType(item)
      result += [tmp]
    result += ["E"]
  
  if cnt != 1:
    result += ["E"]

  return "".join(result)

def convertType(type):
  #if option.compiler_type == 'gcc':
  return convertType_for_gcc(type)
  #elif option.compiler_type == 'msvc':
  # return convertType_for_msvc(tree)
  #else:
  # return convertType_for_other(tree)
 
def converting(name, tmpl):
  mangling_name = []
  mangling_name += convertName(name)
  if tmpl != None:
    mangling_name.append("I")
    for item in tmpl:
      mangling_name.append(converting(item.name, item.tmpl))
    mangling_name.append("E")
  mangling_name.apeend("E")
  return "".join(mangling_name)

# 모든 이름은 root namespace부터 있어야 한다.
# 즉, Full name space이어야한다.
def encode_for_gcc(name, args):
  mangling = []
  if True:
    cnt = len(name)
    _name = convertName(name)
    mangling.append(_name)

    if args != None:
      for item in args:
        #_type = args[item]
        _type = None
        if isinstance(item, ASTType):
          _type = item
        else:
          _type = item.type
        typename = convertType(_type)
        mangling.append(typename)

    return "".join(mangling)
  elif isinstance(tree, ASTVar) or isinstance(tree, ASTVal):
    cnt = len(tree.name.array)
    if cnt == 1:
      return "_" + tree.name.array[0]
    else:
      name = convertName(tree.name.array)
      mangling.append("".join(["__ZN"]+name+["E"]))
     
    return "".join(mangling)
    
def encodeSymbolName(name, args = None, ends = None):
  if name == 'main':
    return '_main'

  #if option.compiler_type == 'gcc':
  return encode_for_gcc(name, args)
  #elif option.compiler_type == 'msvc':
  # return encode_for_msvc(tree)
  #else:
  # return encode_for_other(tree)

def reverseEncodedName(name):
  value = None
  for key in enm.keys():
    if enm[key] == name:
      value = key

  if value == None:
    value = name

  return value

def convertSimpleTypeName(name):
  #shortName = {
  #  "System.lang.Integer": "i",
  #  "System.lang.Boolean": "b",
  #  "System.lang.Float": "f",
  #  "System.lang.Double": "d"}

  # for gcc
  nameList = name.split('.')
  return convertName(nameList)

def decodeMachineName(name):
  translateTable = {
    "i": "System.lang.Integer",
    "b": "System.lang.Boolean",
    "f": "System.lang.Float",
    "d": "System.lang.Double"}

  if translateTable.has_key(name):
    return translateTable[name]

  path = []
  
  pos = 0
  while True:
    loc = pos
    while True:
      ch = name[pos]
      if not ch.isdigit():
        break
      pos += 1
  
    num = int(name[loc:pos])
    path.append(name[pos:pos+num])
    pos += num

    if pos == len(name):
      break

  return ".".join(path)

# def System.out.println(abs:First[])
# void System::out::println(First[] abs);
#name = ASTNames(["System", "out", "println"])
#args = ASTArgList([ASTDefArg(ASTNames(["abc"]), ASTType(ASTNames(["First"]), ASTTemplateList([ASTType(ASTNames(["int"]), None, None)]), [ASTEmpty()]))])
#tree = ASTDeclFunc(name = name, args = args, ret = None, body = None, type = None)
#print encode_for_gcc(tree)

def encodeSymbol(name, args, ends):
  if name == 'main':
    return '_main'

  if ends == None:
    ends = ''

  # 숫자로 시작하면, namespace symbol임
  if re.match(r'[0-9]', name[0]):
    return "".join(['__ZN', name, 'E'] + args + ['E'] + [ends])
  else:
    return "".join(['__Z', name, 'E'] + args + ['E'] + [ends])

if __name__ == '__main__':
  print convertNamespace('i')
  print decodeMachineName('6System3out7println')
