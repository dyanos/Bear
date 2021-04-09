#!/usr/bin/env python
# -*- coding: utf-8 -*-
from .mangle import *
from .ASTType import *

def processError():
  pass

class SymbolTable:
  def __init__(self):
    self.table = {}
    # To register default symbols
    self.table["System.lang.Object"] = {"@type": "class"}
    self.table["System.lang.Char"] = {"@type": "class"}
    self.table["System.lang.Byte"] = {"@type": "class"}
    self.table["System.lang.Short"] = {"@type": "class"}
    self.table["System.lang.Word"] = {"@type": "class"}
    self.table["System.lang.Int"] = {"@type": "class"}
    self.table["System.lang.Int64"] = {"@type": "class"}
    self.table["System.lang.Int128"] = {"@type": "class"}
    self.table["System.lang.Int256"] = {"@type": "class"}
    self.table["System.lang.Float"] = {"@type": "class"}
    self.table["System.lang.Double"] = {"@type": "class"}
    self.table["System.lang.Array"] = {"@type": "class"}
    self.table["char"] = {"@type": "class", "@alias": True, "@full": "System.lang.Char"}
    self.table["byte"] = {"@type": "class", "@alias": True, "@full": "System.lang.Byte"}
    self.table["short"] = {"@type": "class", "@alias": True, "@full": "System.lang.Short"}
    self.table["word"] = {"@type": "class", "@alias": True, "@full": "System.lang.Word"}
    self.table["int"] = {"@type": "class", "@alias": True, "@full": "System.lang.Int"}
    self.table["int32"] = {"@type": "class", "@alias": True, "@full": "System.lang.Int"}
    self.table["int64"] = {"@type": "class", "@alias": True, "@full": "System.lang.Int64"}
    self.table["int128"] = {"@type": "class", "@alias": True, "@full": "System.lang.Int128"}
    self.table["int256"] = {"@type": "class", "@alias": True, "@full": "System.lang.Int256"}
    self.table["float"] = {"@type": "class", "@alias": True, "@full": "System.lang.Float"}
    self.table["double"] = {"@type": "class", "@alias": True, "@full": "System.lang.Double"}

  def register(self, symbol):
    pass

  def registerNamespace(self, path):
    if path in self.table:
      pass

    self.table[path] = {"@type": "namespace"}

  def registerClass(self, path, successions):
    self.table[path] = {"@type": "class", "successions": successions}

  def registerValue(self, path, type, body):
    self.table[path] = {"@type": "const_class_property", "type": type, "body": body}

  def registerVariable(self, path, type, body):
    self.table[path] = {"@type": "class_property", "type": type, "body": body}

  def registerFunc(self, path, args, rettype, body, symtbl):
    self.table[path] = {"@type": "class_method", "ret_type": type, "args": args, "body": body, "symtbl": symtbl}

  def find(self, idStr):
    for key in self.table:
      if key.endswith(idStr):
        return self.table[key]

    return None

  def __getitem__(self, key):
    if key in self.table:
      return self.table[key]

    return None

  def __contains__(self, key):
    return key in self.table
    
