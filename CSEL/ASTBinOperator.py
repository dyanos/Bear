#!/usr/bin/env python
from typing import Any, NoReturn
from .AST import *
from .TypeTable import Type


class ASTBinOperator(AST):
  def __init__(self, name: Any, left: AST, right: AST, vtype: Type=None):
    self.name  = name
    self.left  = left
    self.right = right
    self.vtype = vtype

  def printXML(self) -> NoReturn:
    print("<binary-operator name=\"%s\">\n<left>" % (self.name))
    self.left.printXML()
    print("</left>\n<right>")
    self.right.printXML()
    print("</right>\n</binary-operator>")


