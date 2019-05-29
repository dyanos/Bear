# -*- coding: utf-8 -*-
#!/usr/bin/env python
from .AST import *

class ASTRank(AST):
  def __init__(self, expr = None):
    self.expr = expr

  def printXML(self):
    print("Not Yet")
