#!/usr/bin/env python
from AST import *

class ASTTemplateArg(AST):
  def __init__(self, name, type):
    self.name = name
    self.type = type

  def printXML(self):
    print "<template-arg>"
    print "</template-arg>"
