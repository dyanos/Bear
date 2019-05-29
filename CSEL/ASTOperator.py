#!/usr/bin/env python
from .AST import *

class ASTOperator(AST):
  def __init__(self, name, left, right):
    self.name  = name
    self.left  = left
    self.right = right

  def printXML(self):
    print("<binary-operator name=\"%s\">\n<left>" % (self.name))
    self.left.printXML()
    print("</left>\n<right>")
    self.right.printXML()
    print("</right>\n</binary-operator>")


