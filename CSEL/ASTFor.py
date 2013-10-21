#!/usr/bin/env python
from AST import *

class ASTFor(AST):
  def __init__(self, cond, body):
    self.cond = cond
    self.body = body

  def printXML(self):
    print "<for>\n<cond>"
    self.cond.printXML()
    print "</cond>\n<body>"
    self.body.printXML()
    print "</body>\n</for>"


