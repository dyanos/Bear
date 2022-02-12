#!/usr/bin/env python
# -*- coding: utf-8 -*-
from typing import *

from typing import Dict

from .mangle import *
from .ASTType import *
from .TypeTable import *


def processError():
  pass


class SymbolTable:
  cvt = { "System.lang.Int": "int", 
          "System.lang.Object": "object",
          "System.lang.Char": "char",
          "System.lang.Byte": "byte",
          "System.lang.Short": "short",
          "System.lang.Word": "word",
          "System.lang.Int32": "int32",
          "System.lang.Int64": "int64",
          "System.lang.Int128": "int128",
          "System.lang.Int256": "int256",
          "System.lang.Long": "long",
          "System.lang.Float": "float",
          "System.lang.Double": "double",
          "System.lang.Array": "array",
          "System.lang.String": "string",
          "System.lang.Boolean": "boolean",
          "System.lang.Unit": "unit"}

  def __init__(self):
    self.isdebug = False

    self.table: Dict[str, Type] = {}
    
    # To register default symbols
    self.table["System.lang.Object"] = ObjectType()
    self.table["System.lang.Char"] = CharType()
    self.table["System.lang.Byte"] = ByteType()
    self.table["System.lang.Short"] = ShortType()
    self.table["System.lang.Word"] = WordType()
    self.table["System.lang.Int"] = IntegerType()
    self.table["System.lang.Int64"] = Integer64Type()
    self.table["System.lang.Int128"] = Integer128Type()
    self.table["System.lang.Int256"] = Integer256Type()
    self.table["System.lang.Long"] = LongType()
    self.table["System.lang.Float"] = FloatType()
    self.table["System.lang.Double"] = DoubleType()
    self.table["System.lang.Array"] = ArrayType()
    self.table["System.lang.String"] = StringType()
    self.table["System.lang.Boolean"] = BooleanType()
    self.table["System.lang.Unit"] = UnitType()
    self.table["operator+"] = NativeFuncType("operator+",
                                       [FuncArgInfo("left", self.table["System.lang.Int"]),
                                        FuncArgInfo("right", self.table["System.lang.Int"])],
                                       self.table["System.lang.Int"])
    self.table["System.lang.Int.operator+"] = NativeFuncType("System.lang.Int.operator+",
                                                       [FuncArgInfo("right", self.table["System.lang.Int"])],
                                                       self.table["System.lang.Int"])
    #self.table["System.lang.Int.operator+"] = FuncType("+", [FuncArgInfo("right", self.table["System.lang.Int"])], self.table["System.lang.Int"])
    self.table["operator-"] = NativeFuncType("operator-", 
                                       [FuncArgInfo("left", self.table["System.lang.Int"]),
                                        FuncArgInfo("right", self.table["System.lang.Int"])], 
                                       self.table["System.lang.Int"])
    self.table["System.lang.Int.operator-"] = NativeFuncType("System.lang.Int.operator-",
                                                       [FuncArgInfo("right", self.table["System.lang.Int"])],
                                                       self.table["System.lang.Int"])
    self.table["operator*"] = NativeFuncType("operator*",
                                       [FuncArgInfo("left", self.table["System.lang.Int"]),
                                        FuncArgInfo("right", self.table["System.lang.Int"])],
                                       self.table["System.lang.Int"])
    self.table["System.lang.Int.operator*"] = NativeFuncType("System.lang.Int.operator*",
                                                       [FuncArgInfo("right", self.table["System.lang.Int"])],
                                                       self.table["System.lang.Int"])
    self.table["operator/"] = NativeFuncType("operator/",
                                       [FuncArgInfo("left", self.table["System.lang.Int"]),
                                        FuncArgInfo("right", self.table["System.lang.Int"])],
                                       self.table["System.lang.Int"])
    self.table["System.lang.Int.operator/"] = NativeFuncType("System.lang.Int.operator/",
                                                       [FuncArgInfo("right", self.table["System.lang.Int"])],
                                                       self.table["System.lang.Int"])
    self.table["System.lang.Int.operator="] = NativeFuncType("System.lang.Int.operator=",
                                                       [FuncArgInfo("right", self.table["System.lang.Int"])],
                                                       self.table["System.lang.Int"])

    #self.table["System.lang.Int.operator-"] = FuncType("-", [FuncArgInfo("right", self.table["System.lang.Int"])], self.table["System.lang.Int"])
    self.table["System.out.println"] = FuncType("System.out.println", [
      FuncArgInfo("fmt", ValueType("fmt", StringType(), "")),
      FuncArgInfo("...", EllipsisType())])
    
    self.table["char"] = AliasType("char", self.table["System.lang.Char"])
    self.table["byte"] = AliasType("byte", self.table["System.lang.Byte"])
    self.table["short"] = AliasType("short", self.table["System.lang.Short"])
    self.table["word"] = AliasType("word", self.table["System.lang.Word"])
    self.table["int"] = AliasType("int", self.table["System.lang.Int"])
    self.table["int32"] = AliasType("int32", self.table["System.lang.Int"])
    self.table["int64"] = AliasType("int64", self.table["System.lang.Int64"])
    self.table["int128"] = AliasType("int128", self.table["System.lang.Int128"])
    self.table["int256"] = AliasType("int256", self.table["System.lang.Int256"])
    self.table["long"] = AliasType("long", self.table["System.lang.Long"])
    self.table["float"] = AliasType("float", self.table["System.lang.Float"])
    self.table["double"] = AliasType("double", self.table["System.lang.Double"])
    self.table["string"] = AliasType("string", self.table["System.lang.String"])
    self.table["bool"] = AliasType("bool", self.table["System.lang.Boolean"])
    self.table["array"] = AliasType("array", self.table["System.lang.Array"])
    self.table["_"] = AliasType("_", self.table["System.lang.Unit"])
    
    self.cvttbl = {"+": "operator+",
                   "-": "operator-",
                   "*": "operator*",
                   "/": "operator/"}

  def registerNamespace(self, path: str):
    if path in self.table:
      pass

    self.table[path] = NamespaceType(path, None)

  def registerClass(self, path: str, successions: List[Type]) -> NoReturn:
    # path는 full path로 
    self.table[path] = ClassType(path, successions)

  # 초기화는 코드로 들어가야 함!!
  def registerValue(self, path: str, type: Type, attr: Property) -> NoReturn:
    self.table[path] = ValueType(path, type)

  def registerVariable(self, path: str, type: Type, attr: Property) -> NoReturn:
    self.table[path] = VariableType(path, type, attr)

  def registerFunc(self, path: str, args: List[Type], rettype: Type, body: AST, symtbl: Any) -> NoReturn:
    self.table[path] = FuncType(path, args, rettype, body, symtbl)

  def find(self, node: Type) -> Dict[str, Type]:
    if isinstance(node.name, str):
      return self.findByLastName(node.name)
    elif isinstance(node.name, ASTID):
      return self.findByLastName(node.name.name)
    else:
      return self.findByLastName(node.name)
  
  def findByLastName(self, idStr: str) -> Dict[str, Type]:
    keys = sorted([key for key in self.table if key.endswith(idStr)], key=lambda x: len(x))
    return {key: self.table[key] for key in keys}

  def glob(self, path: str, args: List[Type]) -> Type:
    # path는 일단 두 개의 것을 나눈다.
    # 1. full path : System.lang.Int.toString()
    # 2. short path : println()
    if self.isdebug:
      print(f"path={path}")

    result = self.findByLastName(path)
    if len(result) == 0:
      return None
    else:
      r = []
      for key in result:
        _type = result[key]
        if isinstance(_type, FuncType) or isinstance(_type, NativeFuncType):
          is_completed: bool = True
          idx, loc, nargs = 0, 0, len(_type.args)
          while idx < nargs:
            if self.isdebug:
              print(_type.args[idx], args[loc])

            if EllipsisType() == _type.args[idx].type:
              is_completed = True
              break

            if self.isdebug:  
              print(_type.args[idx].type.type, args[loc])

            if _type.args[idx].type != args[loc]:
              is_completed = False
              break
              
            idx += 1
            loc += 1

          if is_completed:
            r.append(_type)
        else:
          print(_type)
          raise NotImplementedError

      if len(r) == 1:
        return r[0]
      elif len(r) >= 1:
        return sorted(r, key=lambda x: -len(x.args))[0]
      else:
        return None

      print(f"duplicated functions: {r}")
      return None

  def startswiths(self, start_str: str) -> List[str]:
    return [key for key in self.table if key.startswith(start_str)]

  def endswiths(self, end_str: str) -> List[str]:
    return [key for key in self.table if key.endswith(end_str)]

  def __getitem__(self, key: str) -> Type:
    if key in self.table:
      return self.table[key]

    return None

  def __contains__(self, key: str) -> bool:
    return key in self.table
    
  def convert(self, _type: ASTType) -> Type:
    def convertType(name: str) -> Type:
      if name == 'System.lang.Int' or name == 'System.lang.Int32' or name == 'int':
        return IntegerType()
      elif name == 'System.lang.Int64' or name == 'int64':
        return Integer64Type()
      elif name == 'System.lang.Int128' or name == 'int128':
        return Integer128Type()
      elif name == 'System.lang.Int256' or name == 'int256':
        return Integer256Type()
      elif name == 'System.lang.Char' or name == 'char':
        return CharType()
      elif name == 'System.lang.Byte' or name == 'byte':
        return ByteType()
      elif name == 'System.lang.Short' or name == 'short':
        return ShortType()
      elif name == 'System.lang.Word' or name == 'word':
        return WordType()
      elif name == 'System.lang.Long' or name == 'long':
        return LongType()
      elif name == 'System.lang.Float' or name == 'float':
        return FloatType()
      elif name == 'System.lang.Double' or name == 'double':
        return DoubleType()
      elif name == 'System.lang.String' or name == 'string':
        return StringType()
      elif name == "System.lang.Boolean" or name == "bool":
        return BooleanType()
      elif name == "System.lang.Unit" or name == "_":
        return UnitType()
      else:
        symbols = self.findByLastName(name)
        keys = list(symbols.keys())
        if len(keys) == 1:
          return symbols[keys[0]]
        else:
          print(f"Error) multiple definition!! {name}")
          print(symbols)
          raise NotImplementedError

    # 일단 template은 무시
    if isinstance(_type, ASTCalleeArgType1):
      if isinstance(_type.type, Type):
        return _type.type
      else:
        raise NotImplementedError
    else:
      ret = convertType(_type.name)

    if _type.templ is not None:
      for templ in _type.templ:
        ret = TemplateType(ret, self.convert(templ))
    if _type.ranks is not None and len(_type.ranks.ranks) != 0:
      for rank in _type.ranks.ranks:
        ret = ArrayType(ret, rank)

    return ret

