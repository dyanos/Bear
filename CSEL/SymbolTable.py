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
  def __init__(self):
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
    self.table["System.lang.Int.operator+"] = FuncType("System.lang.Int.operator+", [FuncArgInfo("left", self.table["System.lang.Int"]),
                                                            FuncArgInfo("right", self.table["System.lang.Int"])], self.table["System.lang.Int"])
    #self.table["System.lang.Int.operator+"] = FuncType("+", [FuncArgInfo("right", self.table["System.lang.Int"])], self.table["System.lang.Int"])
    self.table["System.lang.Int.operator-"] = FuncType("System.lang.Int.operator-", [FuncArgInfo("left", self.table["System.lang.Int"]),
                                                            FuncArgInfo("right", self.table["System.lang.Int"])], self.table["System.lang.Int"])
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
    self.table["_"] = AliasType("_", self.table["System.lang.Unit"])
    
    self.cvttbl = {"+": "operator +",
                   "-": "operator -",
                   "*": "operator *",
                   "/": "operator /"}

  def registerNamespace(self, path: str):
    if path in self.table:
      pass

    self.table[path] = NamespaceType(path, None)

  def registerClass(self, path: str, successions: List[Type]) -> NoReturn:
    # path는 full path로 
    self.table[path] = ClassType(path, successions)

  # 초기화는 코드로 들어가야 함!!
  def registerValue(self, path: str, type: Type) -> NoReturn:
    self.table[path] = ValueType(path, type)

  def registerVariable(self, path: str, type: Type) -> NoReturn:
    self.table[path] = VariableType(path, type)

  def registerFunc(self, path: str, args: List[Type], rettype: Type, body: AST, symtbl: Any) -> NoReturn:
    self.table[path] = FuncType(path, args, rettype, body, symtbl)

  def find(self, node: Type) -> Dict[str, Type]:
    elems = self.findByLastName(node.name)
    pass
  
  def findByLastName(self, idStr: str) -> Dict[str, Type]:
    return {key: self.table[key] for key in self.table if key.endswith(idStr)}

  def glob(self, path: str, args: List[Type]) -> Type:
    # path는 일단 두 개의 것을 나눈다.
    # 1. full path : System.lang.Int.toString()
    # 2. short path : println()
    print(f"path={path}")
    result = self.findByLastName(path)
    if len(result) == 0:
      return None
    elif len(result) == 1:
      key = list(result.keys())[0]
      return result[key]
    else:
      r = []
      for _type in result:
        if isinstance(_type, FuncType):
          loc, nloc = 0, len(_type.args)
          for arg in args:
            # EllipsisType이 나타난 시점부터는 argument matching에 대한 검사는 수행하지 않는다.
            if _type.args[loc].type == EllipsisType():
              loc = nloc
              break
              
            # arg.name이 없으면 그냥 처음부터 비교하면 됨
            if arg.name is None:
              if arg.type == _type.args[loc].type:
                loc += 1
              else:
                break
            elif arg.name:
              if arg.name == _type.args[loc].name and arg.type == _type.args[loc].type:
                loc += 1
              else:
                break
          
          if loc != nloc:
            if _type.args[loc].type == EllipsisType():
              loc = nloc
            else:
              # 나머지는 default값이 들어있어야 함
              while loc < nloc:
                if _type.args[loc].default_val is None:
                  break
                
                loc += 1

          if loc == nloc:
            r.append(_type)
        else:
          print(".....")
          raise NotImplementedError

      if len(r) == 1:
        return r[0]

      print("duplicated functions")
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

