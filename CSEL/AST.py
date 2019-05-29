#!/usr/bin/env python
import traceback

class AST:
  def printXML(self):
    print("Empty")

  def isType(self, typeStr):
    # if this class doesn't have the 'type' member variable,
    if self.type == None:
      return False

    if self.type == typeStr:
      return True

    return False

  def getType(self):
    if self.type == None:
      return None

    return self.type
