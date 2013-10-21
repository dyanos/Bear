#!/usr/bin/env python
from AST import *

class ASTListGenerateType1(AST):
  def __init__(self, start, end):
    self.start = start
    self.end   = end

  def printXML(self):
    print "<list-generate-type>\n<start>"
    self.start.printXML()
    print "</start>\n<end>"
    self.end.printXML()
    print "</end>"


