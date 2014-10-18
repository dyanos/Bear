#!/usr/bin/env python
from AST import *
from ASTType import *

class ASTWord(AST):
  def __init__(self, type, value):
    self.type = self.type = type
    self.value = value

  def printXML(self):
    if self.type == 'Pc':
      print "<string>%s</string>" % (self.value)
    elif self.type == 'i':
      print "<integer>%s</integer>" % (self.value)
    elif self.type == 'f':
      print "<float>%s</float>" % (self.value)
    elif self.type == 'id':
      print "<identifier>%s</identifier>" % (self.value)
    else:
      print "%s" % (self.value)

  def __str__(self):
    return self.value 

  def __eq__(self, right):
    if right == None:
      return False
      
    if isinstance(right, str):
      if self.value == right:
        return True
    else:
      print "Not implemented = right's type :", type(right), " ... ", right
      raise Exception('ASTWord', 'ASTWord')

    return False
