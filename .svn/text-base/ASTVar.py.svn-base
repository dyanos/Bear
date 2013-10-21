#!/usr/bin/env python
from AST import *

class ASTVar(AST):
  def __init__(self, name, type, code):
    self.name = name
    self.type = type
    self.code = code

  def printXML(self):
    print "<var>\n<name>"
    self.name.printXML()
    print "</name>\n<type>"
    self.type.printXML()
    print "</type>\n<code>"
    self.code.printXML()
    print "</code>\n</var>"


