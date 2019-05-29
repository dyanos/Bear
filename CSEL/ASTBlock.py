#!/usr/bin/env python
from .AST import *

class ASTBlock(AST):
  def __init__(self, body):
    self.body = body

  def printXML(self):
    print("<block>")
    self.body.printXML()
    print("</block>")
