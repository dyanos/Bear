#!/usr/bin/env python
from AST import *

class ASTReturn(AST):
  def __init__(self, expr):
    self.expr = expr

  def printXML(self):
    print "<return>"
    self.expr.printXML()
    print "</return>"
