#!/usr/bin/env pythone
from AST import *

class ASTIf(AST):
  def __init__(self, cond, body):
    self.cond = cond
    self.body = body

  def printXML(self):
    print "<if>\n<cond>"
    self.cond.printXML()
    print "</cond>\n<body>"
    self.body.printXML()
    print "</body>\n</if>"


