#!/usr/bin/env python
from AST import *

class ASTExpr(AST):
  def __init__(self, expr):
    self.expr = expr

  def printXML(self):
    self.expr.printXML()


