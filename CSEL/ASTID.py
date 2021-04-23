#!/usr/bin/env python
from typing import Any, NoReturn
from .AST import *
from .ASTType import *
from .TypeTable import Type


class ASTID(AST):
  def __init__(self, name: str, _type: Type):
    super().__init__()
    self.type = _type
    self.name = name
  
  def printXML(self) -> NoReturn:
    print(f"<identifier>{self.name}</identifier>")
  
  def __str__(self) -> str:
    return self.name
  