#!/usr/bin/python 
from AST import *

class ASTDefArg(AST):
  def __init__(self, name, type, defval = None):
    self.name = name
    self.type = type
    self.defval = defval 

  def printXML(self):
    print "<def-func-arg>\n"
    if self.name != None:
      print "<name>"
      self.name.printXML()
      print "</name>\n<type>"
      self.type.printXML()
      print "</type>"
    print "</def-func-arg>"


