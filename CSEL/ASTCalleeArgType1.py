#!?usr/bin/env python
from AST import *

class ASTCalleeArgType1(AST):
  def __init__(self, value):
    self.value = value

  def printXML(self):
    print "<callee-type1>"
    self.value.printXML()
    print "</callee-type1>"

  def __eq__(self, right):
    if self.value.type == right.value.type:
      return True

    return False

  def __ne__(self, right):
    if self.value.type == right.value.type:
      return False

    return True
