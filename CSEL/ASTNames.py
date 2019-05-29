#!/usr/bin/env python
from .AST import *

class ASTNames(AST):
  def __init__(self, array):
    self.array = array

  def printXML(self):
    print("<names>%s</names>" % (".".join(self.array)))

  def convertToPath(self):
    return ".".join(self.array)

  def getLevel(self):
    return len(self.array)

  def getNameList(self):
    return self.array
