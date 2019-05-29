#!/usr/bin/env python
from .AST import *

class ASTIndexing(AST):
  def __init__(self, name, history):
    self.name  = name
    self.hist  = history
    
  def printXML(self):
    print("<indexing>\n<name>")
    self.name.printXML()
    print("</name>\n<hist>")
    for item in self.hist:
      item.printXML()
    print("</hist>\n</indexing>")


