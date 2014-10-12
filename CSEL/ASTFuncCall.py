#!/usr/bin/env python
from AST import *

class ASTFuncCall(AST):
  def __init__(self, name, args):
    self.name = name
    self.args = args 

  def printXML(self):
    print "<call-function>\n<func-name>"
    self.name.printXML()
    print "</func-name>"
    if self.args != None:
      print "<func-arg>"
      self.args.printXML()
      print "</func-arg>"
    print "</call-function>"


