#!/usr/bin/env pythone
from .AST import *

class ASTTemplateList(AST):
  def __init__(self, history):
    self.history = history

  def printXML(self):
    print("<template-list>")
    for item in self.history:
      print("<template-item>")
      item.printXML()
      print("</template-item>")
    print("</template-list>")


