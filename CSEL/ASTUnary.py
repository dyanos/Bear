#!/usr/bin/env python
from .AST import *

class ASTUnary(AST):
  def __init__(self, ident, op):
    self.id = ident
    self.op = op

  def printXML(self):
    print("<unary>")
    self.id.printXML()
    self.op.printXML()
    print("</unary>")
