#!/usr/bin/env python
from .AST import *

class ASTFuncCall(AST):
  def __init__(self, name, args):
    self.name = name
    self.args = args 

  def printXML(self):
    print("<call-function>\n<func-name>")
    if type(self.name) == str:
      print(self.name)
    else:
     self.name.printXML()
    print("</func-name>")
    if self.args != None:
      print("<func-args>")
      if type(self.args) == list:
        for arg in self.args:
          print("<func-arg>")
          arg.printXML()
          print("</func-arg>")
      else:
        self.args.printXML()
      print("</func-args>")
    print("</call-function>")


