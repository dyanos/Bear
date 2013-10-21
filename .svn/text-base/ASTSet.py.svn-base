#!/usr/bin/env python
from AST import *

class ASTSet(AST):
  def __init__(self, lst):
    self.lst = lst

  def printXML(self):
    print "<set>"
    for item in self.lst:
      print "<set-item>"
      item.printXML()
      print "</set-item>"
    print "</set>"
