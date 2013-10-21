#!/usr/bin/env python
from AST import *

class ASTFuncCall(AST):
  def __init__(self, name, body):
    self.name = name
    self.body = body

  def printXML(self):
    print "<call-function>\n<func-name>"
    self.name.printXML()
    print "</func-name>"
    if self.body != None:
      self.body.printXML()
    print "</call-function>"


