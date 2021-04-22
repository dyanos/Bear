#!/usr/bin/env python
from .AST import *

class ASTUnary(AST):
  def __init__(self, ident, op, vtype):
    self.id = ident
    self.op = op
    self.vtype = vtype

  def printXML(self):
    print("<unary>")
    self.id.printXML()
    self.op.printXML()
    print("</unary>")
