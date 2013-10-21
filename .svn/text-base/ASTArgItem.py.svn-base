#!/usr/bin/python 
from AST import *

class ASTArgItem(AST):
  def __init__(self, name, type):
    self.name = name
    self.type = type

  def printXML(self):
    print "<arg-item>\n"
    if self.name != None:
      print "<name>"
      self.name.printXML()
      print "</name>\n<type>"
      self.type.printXML()
      print "</type>"
    print "</arg-item>"


