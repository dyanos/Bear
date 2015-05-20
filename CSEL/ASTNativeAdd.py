#!/usr/bin/env python
from AST import *

class ASTNativeAdd(AST):
  def __init__(self, src, dst):
    self.src  = src
    self.dst  = dst

  def printXML(self):
    self.src.printXML()
    self.dst.printXML()
