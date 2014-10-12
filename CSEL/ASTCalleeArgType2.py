#!/usr/bin/env python
from AST import *

class ASTCalleeArgType2(AST):
  def __init__(self, name, value):
    self.name = name
    self.value = value

  def printXML(self):
    print "<callee-type2>"
    print "<name>"
    self.name.printXML()
    print "</name>"
    print "<value>"
    self.name.printXML()
    print "</value>"
    print "<callee-type2>"

  def __eq__(self, right):
    if self.value.type == right.value.right:
      return True

    return False

  def __ne__(self, right):
    if self.value.type == right.value.right:
      return False

    return True
