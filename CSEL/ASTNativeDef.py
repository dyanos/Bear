from .AST import *

class ASTNativeDef(AST):
  def __init__(self, name):
    self.name = name

  def printXML(self):
    print(f"native function : {self.name}")