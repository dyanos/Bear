#!/usr/bin/env python
from typing import Any, NoReturn
from .AST import *
from .ASTType import *
from .TypeTable import *

class ASTWord(AST):
  def __init__(self, value: Any, _type: Type):
    super().__init__()
    self.type = _type
    self.value = value

  def printXML(self) -> NoReturn:
    if self.type == StringType():
      print("<string>%s</string>" % (self.value))
    elif self.type == IntegerType():
      print("<integer>%s</integer>" % (self.value))
    elif self.type == FloatType():
      print("<float>%s</float>" % (self.value))
    elif self.type == DoubleType():
      print("<double>%s</double>" % (self.value))
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
