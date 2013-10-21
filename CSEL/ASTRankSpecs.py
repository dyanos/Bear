#!/usr/bin/env python
from AST import *

class ASTRankSpecs(AST):
  def __init__(self, history):
    self.history = history

  def printXML(self):
    print "<rank-spec-list>"
    for item in self.history:
      print "<rank>"
      item.printXML()
      print "</rank>"

    print "</rank-spec-list>"


