# -*- coding: utf-8 -*-
#!/usr/bin/env python
from AST import *

class ASTType(AST):
  def __init__(self, name, templ = None, ranks = None):
    self.name  = name
    self.templ = templ
    self.ranks = ranks

  # 일단 지금으로써는 그냥 name만 templ과 rank는 어떻게 쓸지 생각해봐야겠음  
  def __eq__(self, right):
    if isinstance(right, str):
      if self.name != right:
        return False
    elif isinstance(right, ASTType):
      if self.name != right.name:
        return False
      if self.templ != self.templ:
        return False
      if self.ranks != self.ranks:
        return False
      return True
    else:
      return False

    return True

  def __ne__(self, right):
    return not self.__eq__(right)            

  def __str__(self):
    return self.name

  def printXML(self):
    print "<type>\n<name>"
    self.name.printXML()
    print "</name>"
    if self.templ != None:
      print "<templ>"
      self.templ.printXML()
      print "</templ>"
    if self.ranks != None:
      print "<ranks>"
      self.ranks.printXML()
      print "</ranks>"
    print "</type>"


