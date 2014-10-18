#!/usr/bin/env python
# -*- coding: utf-8 -*-
from mangle import *
from ASTType import *

# native인지 구별할 필요가 있어야 한다.
# native의 의미는 C++에서 제작된 것으로 Bear 언어로 별도로 된 body가 없다는 뜻.  
# TODO: Class, Struct, Function등에 대해서 native에 대한 정의를 담을 수 있는 변수 또는 어떠한 장치 필요 
class SymbolTable:
  def __init__(self):
    self.symbolTable = {}
    self.symbolDict = {'@type':'namespace'}

  def register(self, info):
    if not info.has_key('@type'):
      raise KeyError

    type = info['@type']
    if type == 'namespace':
      self.registerNamespace(info)
    elif type == 'class':
      self.registerClass(info)
    elif type == 'def':
      self.registerDef(info)
    elif type == 'alias':
      if not info.has_key('@fullname'):
        raise KeyError

      self.symbolDict[info['@name']] = {'@type': 'alias', '@name': info['@fullname']}
    else:
      print "type :", type
      raise NotImplementedError

  def registerNamespace(self, info):
    if not info.has_key('@name'):
      raise KeyError

    path = info['@name'].split('.')
    now  = self.symbolDict
    for name in path:
      if not now.has_key(name):
        now[name] = {'@type': 'namespace'}

      now = now[name]

  def registerClass(self, info):
    if not info.has_key('@name'):
      raise KeyError

    path = info['@name'].split('.')
    now  = self.symbolDict
    for name in path[:-1]:
      if not now.has_key(name):
        now[name] = {'@type': 'class'}
      
      now = now[name]
    
    cname = path[-1]
    if now.has_key(cname):
      print "Error) Duplicated Class Name"
      raise Exception('Error', 'Duplicated Class Name')

    content = {'@type': 'class'}
    if not info.has_key('@body'):
      now[cname] = content
      return

    symbols = info['@body']
    for name in symbols:
      if symbols[name]['@type'] == 'var':
        content[name] = {'@type': 'var', '@vtype': symbols[name]['@vtype']}
      elif symbols[name]['@type'] == 'val':
        content[name] = {'@type': 'val', '@vtype': symbols[name]['@vtype']}
      elif symbols[name]['@type'] == 'def':
        data = symbols[name]

        args = None
        if data.has_key('@args'):
          args = data['@args']

        body = None
        if data.has_key('@body'):
          body = data['@body']

        native = convertToNativeSymbol(name, args, None)
        content[native] = {'@type': 'def', '@vtype': data['@vtype'], '@body': body}

        fn = encodeSymbolName(".".join([info['@name'], name]), args)
        self.symbolTable[fn] = content[native]

    now[cname] = content

  def registerDef(self, info):
    if not info.has_key('@name'):
      raise KeyError

    path = info['@name'].split('.')
    now  = self.symbolDict
    if len(path) > 1:
      for name in path[:-1]:
        if not now.has_key(name):
          now[name] = {}

        now = now[name]

    content = {'@type': 'def', '@vtype': info['@vtype']}

    args = None
    if info.has_key('@args'):
      args = info['@args']

    body = None
    if info.has_key('@body'):
      body = info['@body']

    content['@body'] = body
    content['@args'] = args

    fname = path[-1]

    native = convertToNativeSymbol(fname, args, None)
    fn = encodeSymbolName(path, args)
    
    self.symbolTable[fn] = content
    now[native] = content

  def findType(self, path):
    now = self.symbolDict

    pathlst = path.split('.')
    nmatch = 0
    for name in pathlst:
      if now['@type'] == 'namespace':
        if not now.has_key(name):
          break

        now = now[name]
        nmatch += 1
      elif now['@type'] == 'class':
        # class의 method들은 무조건 단일 이름의 함수들이다.
        for key in now.keys():
          if key.startswith(name + 'E'):
            now = now[key]
            nmatch += 1
            break
      elif now['@type'] == 'def':
        break
      else:
        break

    if nmatch == len(pathlst):
      if now['@type'] == 'alias':
        return self.findType(now['@name'])

      return now['@type']

    native = encodeSymbolName(path, None, None)
    for key in self.symbolTable.keys():
      if key.startswith(native):
        data = self.symbolTable[key]
        if not data.has_key('@type'):
          print "Error) key :", key
          raise KeyError

        return data['@type']

  def find(self, info):
    if not info.has_key('@name') or not info.has_key('@type'):
      raise KeyError

    type = info['@type']
    path = info['@name']
    pathlst = path.split('.')

    if type == 'def':
      args = None
      if info.has_key('@args'):
        args = info['@args']

      native = encodeSymbolName(path, args, None)
      if self.symbolTable.has_key(native):
        return True
    elif type == 'namespace' or type == 'class':
      pathlst = path.split('.')

      now = self.symbolDict
      nmatch = 0
      for pos, name in enumerate(pathlst):
        if not now.has_key(name):
          return False

        now = now[name]
        nmatch += 1

      if nmatch == len(pathlst):
        return True
    else:
      print "Error) type :", type
      raise NotImplementedError

    return False

  def __getitem__(self, path):
    if not self.symbolTable.has_key(path):
      return None

    return self.symbolTable[path]
