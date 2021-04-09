#!/usr/bin/env python
from .AST import *

class ASTUnit(AST):
  def __init__(self):
    pass

  def printXML(self):
    print("<unit/>")