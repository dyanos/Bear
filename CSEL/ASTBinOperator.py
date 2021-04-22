#!/usr/bin/env python
from .AST import *

class ASTBinOperator(AST):
  def __init__(self, name, left, right, vtype=None):
    self.name  = name
    self.left  = left
    self.right = right
    self.vtype = vtype

  def printXML(self):
    print("<binary-operator name=\"%s\">\n<left>" % (self.name))
    self.left.printXML()
    print("</left>\n<right>")
    self.right.printXML()
    print("</right>\n</binary-operator>")


