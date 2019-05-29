#!/usr/bin/env python
from .AST import *

class ASTTemplate(AST):
  def __init__(self, args, body, type_info):
    self.args = args
    self.body = body
    self.type_info = type_info
    
  def printXML(self):
    print("<template>")
    print("</template>")
