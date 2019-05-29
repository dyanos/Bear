#!/usr/bin/env python
from .AST import *

class ASTCases(AST):
  def __init__(self, lst):
    self.lst = lst

  def printXML(self):
    print("<cases>")
    for item in self.lst:
      item.printXML()
    print("</cases>")
