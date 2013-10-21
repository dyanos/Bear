#!/usr/bin/env python
from AST import *

class ASTAlias(AST):
  def __init__(self, name, alias):
    self.name  = name
    self.alias = alias
    
  def printXML(self):
    print "<alias>\n<name>"
    self.name.printXML()
    print "</name>\n<alias>"
    self.alias.printXML()
    print "</alias>\n</alias>"


