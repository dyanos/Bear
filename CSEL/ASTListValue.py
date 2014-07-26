#!/usr/bin/env python
from AST import *

class ASTListValue(AST):
  def __init__(self, history):
    self.history = history

  def printXML(self):
    print "<list>"
    for item in self.history:
      item.printXML()
    print "</list>"
