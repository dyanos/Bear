#!/usr/bin/env python
from .AST import *

class ASTExprs(AST):
  def __init__(self, exprs):
    self.exprs = exprs

  def printXML(self):
    for item in self.exprs:
      item.printXML()


