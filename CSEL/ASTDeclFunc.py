#!/usr/bin/env python
from .AST import *

class ASTDeclFunc(AST):
  def __init__(self, info):
    self.info = info

  def printXML(self):
    print("<function>")
    print("<function-name>%s</function-name>" % (self.info['name']))
    print("</function>")


