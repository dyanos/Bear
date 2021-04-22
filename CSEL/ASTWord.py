#!/usr/bin/env python
from typing import Any, NoReturn
from .AST import *
from .ASTType import *
from .TypeTable import Type

class ASTWord(AST):
  def __init__(self, type: str, value: Any, vtype: Type = None):
    self.type = type
    self.value = value
    self.vtype = vtype

  def printXML(self) -> NoReturn:
    if self.type == 'Pc':
      print("<string>%s</string>" % (self.value))
    elif self.type == 'i':
      print("<integer>%s</integer>" % (self.value))
    elif self.type == 'f':
      print("<float>%s</float>" % (self.value))
    elif self.type == 'id':
      print("<identifier>%s</identifier>" % (self.value))
    else:
      print("%s" % (self.value))

  def __str__(self) -> str:
    return self.value 

  def __eq__(self, right: AST) -> bool:
    if right is None:
      return False
      
    if isinstance(right, str):
      if self.value == right:
        return True
    else:
      print("Not implemented = right's type :", type(right), " ... ", right)
      raise Exception('ASTWord', 'ASTWord')

    return False
