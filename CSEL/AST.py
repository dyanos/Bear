#!/usr/bin/env python
import traceback

class AST:
  def __init__(self):
    self.type = None

  def printXML(self):
    print("Empty")

  def isType(self, typeStr: str) -> bool:
    # if this class doesn't have the 'type' member variable,
    if self.type is None:
      return False

    if self.type == typeStr:
      return True

    return False

  def getType(self) -> str:
    if self.type is None:
      return None

    return self.type
