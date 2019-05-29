#!/usr/bin/env python
from .AST import *

class ASTArgList(AST):
  def __init__(self, history):
    self.history = history

  def printXML(self):
    print("<argument-list>")
    for item in self.history:
      item.printXML()
    print("</argument-list>")


