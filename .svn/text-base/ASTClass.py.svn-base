#!/usr/bin/env python
# -*- coding: utf-8 -*-
from AST import *

# All the class and namespace must have unique symbol table related to our class or namespace.

# 만일 variable의 이름이 System.out.debug라고 할때, 
# 해당 namespace(System.out)이 꼭 먼저 선언되어 있어야 한다.
# 그래야 사용할 수 있다.
# 만약 선언되어 있지 않다면 Symbol을 사용할 수 없다.
class ASTClass(AST):
  def __init__(self, info):
    self.info = info

  def printXML(self):
    print "<class>"
    if self.info.has_key('short'):
      print "<short-name>%s</short-name>" % (self.info['short'])
    if self.info.has_key('long'):
      print "<long-name>%s</long-name>" % (self.info['long'])
    self.name.printXML()
    print "</class>"


