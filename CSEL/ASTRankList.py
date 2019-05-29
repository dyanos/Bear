# -*- coding: utf-8 -*-
#!/usr/bin/env python
from .AST import *

class ASTRankList(AST):
  def __init__(self, ranks = None):
    self.ranks = ranks

  def printXML(self):
    print("Not Yet")
