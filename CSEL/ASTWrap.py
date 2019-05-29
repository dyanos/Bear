#!/usr/bin/env python
from .AST import *
class ASTWrap(AST):
  def __init__(self, history):
    self.history = history

  def printXML(self):
    self.history.printXML()
