#!/usr/bin/env python
from .AST import *

class ASTCase(AST):
  def __init__(self, cond, body):
    self.cond = cond
    self.body = body

  def printXML(self):
    print("<case>")
    print("<condition>")
    self.cond.printXML()
    print("</condition>\n<body>")
    self.body.printXML()
    print("</body>\n</case>")
