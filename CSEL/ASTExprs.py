#!/usr/bin/env python
from .AST import *

class ASTExprs(AST):
  def __init__(self, exprs, localSymtbl):
    self.exprs = exprs
    self.localSymtbl = localSymtbl

  def printXML(self):
    for item in self.exprs:
      item.printXML()


