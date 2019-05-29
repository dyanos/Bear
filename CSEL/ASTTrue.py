#!/usr/bin/env python
from .AST import *

class ASTTrue(AST):
  def printXML(self):
    print("<true/>")


