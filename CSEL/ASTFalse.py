#!/usr/bin/env pythone
from .AST import *

class ASTFalse(AST):
  def printXML(self):
    print("<false/>")


