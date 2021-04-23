#!?usr/bin/env python
from typing import NoReturn
from .AST import *
from .TypeTable import *


class ASTCalleeArgType1(AST):
  def __init__(self, value: AST, type: Type):
    self.value = value
    self.type = type

  def printXML(self) -> NoReturn:
    print("<callee-type1>")
    self.value.printXML()
    if self.type == IntegerType():
      print("<integer/>")
    elif self.type == StringType():
      print("<string/>")
    elif self.type == FloatType():
      print("<float/>")
    elif self.type == DoubleType():
      print("<double/>")
    else:
      print(self.type)
      raise NotImplementedError
      
    print("</callee-type1>")

  def __eq__(self, right: AST) -> bool:
    if self.type == right.type:
      return True

    return False

  def __ne__(self, right: AST) -> bool:
    if self.type == right.type:
      return False

    return True
