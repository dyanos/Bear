#!/usr/bin/env python
from typing import *
from .AST import *


class ASTNames(AST):
  def __init__(self, array: List[str]):
    self.array = array

  def printXML(self) -> NoReturn:
    print("<names>%s</names>" % (".".join(self.array)))

  def convertToPath(self) -> str:
    return ".".join(self.array)

  def getLevel(self) -> int:
    return len(self.array)

  def getNameList(self) -> List[str]:
    return self.array
