#!/usr/bin/env python
from .AST import *
from .TypeTable import Type

class ASTReturn(AST):
  def __init__(self, expr, vtype: Type = None):
    self.expr = expr
    self.vtype = vtype

  def printXML(self):
    print("<return>")
    self.expr.printXML()
    print("</return>")
