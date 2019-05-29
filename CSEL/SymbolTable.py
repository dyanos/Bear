#!/usr/bin/env python
# -*- coding: utf-8 -*-
from .mangle import *
from .ASTType import *

# native인지 구별할 필요가 있어야 한다.
# native의 의미는 C++에서 제작된 것으로 Bear 언어로 별도로 된 body가 없다는 뜻.  
# TODO: Class, Struct, Function등에 대해서 native에 대한 정의를 담을 수 있는 변수 또는 어떠한 장치 필요 
class SymbolTable:
  def __init__(self):
    self.symbolTable = {}
    self.symbolDict = {'@type':'namespace'}

  def register(self, info):
    if '@type' not in info:
      raise KeyError

    type = info['@type']
    if type == 'namespace':
      self.registerNamespace(info)
    elif type == 'class':
      self.registerClass(info)
    elif type == 'def':
      self.registerDef(info)
    elif type == 'alias':
      if '@fullname' not in info:
        raise KeyError

      self.symbolDict[info['@name']] = {'@type': 'alias', '@name': info['@fullname']}
    elif type == 'native def':
      self.registerNativeDef(info)
    else:
      print("type :", type)
      raise NotImplementedError

  def registerNamespace(self, info):
    if '@name' not in info:
      raise KeyError

    path = info['@name'].split('.')
    now  = self.symbolDict
    for name in path:
      if name not in now:
        now[name] = {'@type': 'namespace'}

      now = now[name]

  def registerClass(self, info):
    if '@name' not in info:
      raise KeyError

    path = info['@name'].split('.')
    now  = self.symbolDict
    for name in path[:-1]:
      if name not in now:
        now[name] = {'@type': 'class'}
      
      now = now[name]
    
    cname = path[-1]
    if cname in now:
      print("Error) Duplicated Class Name")
      raise Exception('Error', 'Duplicated Class Name')

    content = {'@type': 'class'}
    if '@body' not in info:
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
        if '@args' in data:
          args = data['@args']

        body = None
        if '@body' in data:
          body = data['@body']

        native = convertToNativeSymbol(name, args, None)
        content[native] = {'@type': 'def', '@vtype': data['@vtype'], '@body': body}

        fn = encodeSymbolName(".".join([info['@name'], name]), args)
        self.symbolTable[fn] = content[native]

    now[cname] = content

  def registerDef(self, info):
    if '@name' not in info:
      raise KeyError

    path = info['@name'].split('.')
    now  = self.symbolDict
    if len(path) > 1:
      for name in path[:-1]:
        if name not in now:
          now[name] = {}

        now = now[name]

    content = {'@type': 'def', '@vtype': info['@vtype']}

    args = None
    if '@args' in info:
      args = info['@args']

    body = None
    if '@body' in info:
      body = info['@body']

    symbols = None
    if '@symbols' in info:
      symbols = info['@symbols']

    content['@body'] = body
    content['@args'] = args
    content['@symbols'] = symbols

    fname = path[-1]

    native = convertToNativeSymbol(fname, args, None)
    fn = encodeSymbolName(path, args)

    self.symbolTable[fn] = content
    now[native] = content

  def registerNativeDef(self, info):
    if '@name' not in info:
      raise KeyError

    path = info['@name'].split('.')
    now  = self.symbolDict
    if len(path) > 1:
      for name in path[:-1]:
        if name not in now:
          now[name] = {}

        now = now[name]

    content = {'@type': 'def', '@vtype': info['@vtype']}

    args = None
    if '@args' in info:
      args = info['@args']

    body = None
    if '@body' in info:
      body = info['@body']

    symbols = None
    if '@symbols' in info:
      symbols = info['@symbols']

    content['@body'] = body
    content['@args'] = args
    content['@symbols'] = symbols
    content['@method'] = info['@method']

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
        if name not in now:
          break

        now = now[name]
        nmatch += 1
      elif now['@type'] == 'class':
        # class의 method들은 무조건 단일 이름의 함수들이다.
        for key in list(now.keys()):
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
    for key in list(self.symbolTable.keys()):
      if key.startswith(native):
        data = self.symbolTable[key]
        if '@type' not in data:
          print("Error) key :", key)
          raise KeyError

        return data['@type']

  def find(self, info):
    if '@name' not in info or '@type' not in info:
      raise KeyError

    type = info['@type']
    path = info['@name']
    pathlst = path.split('.')

    if type == 'def':
      args = None
      if '@args' in info:
        args = info['@args']

      native = encodeSymbolName(path, args, None)
      #print "*1", native
      if native in self.symbolTable:
        return self.symbolTable[native]
    elif type == 'namespace' or type == 'class':
      pathlst = path.split('.')

      now = self.symbolDict
      nmatch = 0
      for pos, name in enumerate(pathlst):
        if name not in now:
          return None

        now = now[name]
        nmatch += 1

      if nmatch == len(pathlst):
        return now
    else:
      print("Error) type :", type)
      raise NotImplementedError

    return None

  def findByEncodedSymbol(self, encoded):
    if encoded in self.symbolTable:
      return self.symbolTable[encoded]

    return None

  def __getitem__(self, path):
    if path not in self.symbolTable:
      return None

    return self.symbolTable[path]
