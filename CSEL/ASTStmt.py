#!/usr/bin/env pythone
from .AST import *

class ASTStmt(AST):
  def __init__(self, stmt):
    self.stmt = stmt

  def printXML(self):
    print("<stmt>")
    self.stmt.printXML()
    print("</body>\n</if>")
