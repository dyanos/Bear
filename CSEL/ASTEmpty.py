#!/usr/bin/env pythone
from .AST import *

class ASTEmpty(AST):
  def printXML(self):
    print("<empty/>")


