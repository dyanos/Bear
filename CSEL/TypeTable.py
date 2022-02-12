from typing import *

from CSEL.ASTNativeAdd import ASTNativeAdd
from .ASTType import ASTType
from .ASTNativeDef import *


class Property:
  PUBLIC = 0 # default
  PROTECTED = 1
  PRIVATE = 2
  NATIVE = 4


class Type:
  def __init__(self, typename: str):
    self.typename = typename
  
  def getTypename(self) -> str:
    return self.typename
  
  def __eq__(self, right: Type):
    right_type = right
    if isinstance(right, AliasType):
      right_type = right.original_type
    
    if right_type.typename == self.typename:
      return True
    
    return False

  def __ne__(self, right: Type):
    right_type = right
    if isinstance(right, AliasType):
      right_type = right.original_type
  
    #print(right_type.typename, self.typename)
    if isinstance(right_type, str) and right_type == self.typename:
      return False
    elif isinstance(right_type, Type) and right_type.getTypename() == self.typename:
      return False
    else:
      return True
  
class AliasType(Type):
  def __init__(self, name: str, oname: Type):
    super(AliasType, self).__init__(typename="alias")
    self.name = name
    self.original_type = oname
  
  def __eq__(self, right: Type) -> bool:
    if isinstance(right, AliasType):
      if self.original_type == right.original_type:
        return True
    else:
      if self.original_type == right:
        return True
    
    return False


class UnitType(Type):
  def __init__(self):
    super(UnitType, self).__init__(typename="System.lang.Unit")
    self.name = ''


class ObjectType(Type):
  def __init__(self):
    super(ObjectType, self).__init__(typename="System.lang.Object")
    self.name = ''


class CharType(Type):
  def __init__(self):
    super(CharType, self).__init__(typename="System.lang.Char")
    self.name = ''


class ByteType(Type):
  def __init__(self):
    super(ByteType, self).__init__(typename="System.lang.Byte")
    self.name = ''


class ShortType(Type):
  def __init__(self):
    super(ShortType, self).__init__(typename="System.lang.Short")
    self.name = ''


class WordType(Type):
  def __init__(self):
    super(WordType, self).__init__(typename="System.lang.Word")
    self.name = ''


class IntegerType(Type):
  def __init__(self):
    super(IntegerType, self).__init__(typename="System.lang.Int")
    self.name = ''


class Integer32Type(Type):
  def __init__(self):
    super(Integer32Type, self).__init__(typename="System.lang.Int32")
    self.name = ''


class Integer64Type(Type):
  def __init__(self):
    super(Integer64Type, self).__init__(typename="System.lang.Int64")
    self.name = ''


class Integer128Type(Type):
  def __init__(self):
    super(Integer128Type, self).__init__(typename="System.lang.Int128")
    self.name = ''


class Integer256Type(Type):
  def __init__(self):
    super(Integer256Type, self).__init__(typename="System.lang.Int256")
    self.name = ''


class FloatType(Type):
  def __init__(self):
    super(FloatType, self).__init__(typename="System.lang.Float")
    self.name = ''


class DoubleType(Type):
  def __init__(self):
    super(DoubleType, self).__init__(typename="System.lang.Double")
    self.name = ''


class LongType(Type):
  def __init__(self):
    super(LongType, self).__init__(typename="System.lang.Long")
    self.name = ''


class StringType(Type):
  def __init__(self):
    super(StringType, self).__init__(typename="System.lang.String")
    self.name = ''


class BooleanType(Type):
  def __init__(self):
    super(BooleanType, self).__init__(typename="System.lang.Boolean")
    self.name = ''


class ArrayType(Type):
  def __init__(self, default_type: Type = None, rank: List[int] = None):
    super(ArrayType, self).__init__(typename="array")
    self.name = ''
    self.default_type = default_type
    self.rank = rank
  
  def __eq__(self, right: Type) -> bool:
    right_type = right
    if isinstance(right_type, AliasType):
      right_type = right_type.original_type
    
    if self.typename != right_type.typename:
      return False
    
    if self.default_type != right.default_type:
      return False
    
    if self.rank != right.rank:
      return False
    
    return True


class PointerType(Type):
  def __init__(self):
    super(PointerType, self).__init__(typename="pointer")
    self.name = ''


class TemplateType(Type):
  def __init__(self, type: Type, arg: Type):
    super(TemplateType, self).__init__(typename="template")
    self.type = type
    self.arg = arg
  
  def __eq__(self, right: Type) -> bool:
    right_type = right
    if isinstance(right_type, AliasType):
      right_type = right_type.original_type
    
    if self.typename != right_type.typename:
      return False
    
    if self.type != right_type.type:
      return False
    
    if self.arg != right_type.arg:
      return False
    
    return True


class FuncArgInfo:
  def __init__(self, name: str, type: Type, default_val: Any = None):
    self.name = name
    self.type = type
    self.default_val = default_val


class FuncType(Type):
  def __init__(self, name: str, args: List[FuncArgInfo], rettype: Type = UnitType(), body: AST = None, symtbl: Any = None):
    super(FuncType, self).__init__(typename="function")
    self.name = name
    self.args = args  # list[Type]
    self.rettype = rettype
    self.body = body
    self.symtbl = symtbl
    
    
class NativeFuncType(Type):
  def __init__(self, name: str, args: List[FuncArgInfo], rettype: Type = UnitType()):
    super(NativeFuncType, self).__init__(typename="function")
    self.name = name
    self.args = args  # list[Type]
    self.rettype = rettype


class ClassType(Type):
  def __init__(self, name: str, parents: List[Type]):
    super(ClassType, self).__init__(typename="class")
    self.name = name
    self.parents = parents
  
  def __eq__(self, right: Type) -> bool:
    right_type = right
    if isinstance(right_type, AliasType):
      right_type = right_type.original_type
    
    if self.typename != right_type.typename:
      return False
    
    if self.name != right_type.name:
      for parent in self.parents:
        if parent == right_type:
          return True
      
      return False
    
    return True


class NamespaceType(Type):
  def __init__(self, name: str, namespaceInfo: Any):
    super(NamespaceType, self).__init__(typename="namespace")
    self.name = name
    self.info = namespaceInfo
  
  def __eq__(self, right: Type) -> bool:
    right_type = right
    if isinstance(right_type, AliasType):
      right_type = right_type.original_type
    
    if self.typename != right_type.typename:
      return False
    
    if self.name != right_type.name:
      return False
    
    return True


class ValueType(Type):
  def __init__(self, name: str, type: Type, attr: Property, default_val: Any = None):
    super(ValueType, self).__init__(typename="value")
    self.name = name
    self.type = type
    self.attr = attr
    self.default_val = default_val
  
  def __eq__(self, right: Type) -> bool:
    if isinstance(right, ValueType) or isinstance(right, VariableType):
      if self.type != right.type:
        return False
    else:
      if self.type != right:
        return False
    
    return True

  def __ne__(self, right: Type) -> bool:
    if isinstance(right, ValueType) or isinstance(right, VariableType):
      if self.type != right.type:
        return True
    else:
      if self.type != right:
        return True
  
    return False

class VariableType(Type):
  def __init__(self, name: str, type: Type, attr: Property, default_val: Any = None):
    super(VariableType, self).__init__(typename="variable")
    self.name = name
    self.type = type
    self.attr = attr
    self.default_val = default_val

  def __eq__(self, right: Type) -> bool:
    if isinstance(right, ValueType) or isinstance(right, VariableType):
      if self.type != right.type:
        return False
    else:
      if self.type != right:
        return False
  
    return True

  def __ne__(self, right: Type) -> bool:
    if isinstance(right, ValueType) or isinstance(right, VariableType):
      if self.type != right.type:
        return True
    else:
      if self.type != right:
        return True
  
    return False

class EllipsisType(Type):
  def __init__(self):
    super(EllipsisType, self).__init__(typename="ellipsis")
    self.name = ''
