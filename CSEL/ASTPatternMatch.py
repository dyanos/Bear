#!/usr/bin/env python
from .AST import *

class ASTPatternMatch(AST):
  def __init__(self, cond, body):
    self.cond = cond
    self.body = body

  def printXML(self):
    print("<pattern-match>\n<cond>")
    print(self.cond)
    self.cond.printXML()
    print("</cond>")
    self.body.printXML()
    print("</pattern-match>")
