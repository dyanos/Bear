#!?usr/bin/env python
from AST import *

class ASTCalleeArgType1(AST):
  def __init__(self, name, type):
    self.name = name
    self.type = type

  def printXML(self):
    print "<callee-type1>"
    self.name.printXML()
    self.type.printXML()
    print "</callee-type1>"

  def __eq__(self, right):
    if self.type == right.type:
      return True

    return False

  def __ne__(self, right):
    if self.type == right.type:
      return False

    return True
