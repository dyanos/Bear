import CSEL.TypeTable
import cppmangle.ast
from .TypeTable import *
from cppmangle.ast import *
from cppmangle.msvc import msvc_mangle


def _convertToMSVCType(t: CSEL.TypeTable.Type) -> cppmangle.ast.Type:
  if t == UnitType():
    return SimpleType(0, t_void)
  elif t == IntegerType():
    return SimpleType(0, t_sint)
  elif t == FloatType():
    return SimpleType(0, t_float)
  elif t == DoubleType():
    return SimpleType(0, t_double)
  elif t == CharType():
    return SimpleType(0, t_char)
  elif t == ByteType():
    return SimpleType(0, t_uchar)
  elif t == ShortType():
    return SimpleType(0, t_sshort)
  elif t == WordType():
    return SimpleType(0, t_ushort)
  elif t == EllipsisType():
    return SimpleType(0, t_ellipsis)
  elif t == StringType():
    return PtrType(0, SimpleType(0, t_char), False, as_msvc_x64_absolute)
  elif isinstance(t, ValueType):
    ret = _convertToMSVCType(t.type)
    if isinstance(ret, PtrType):
      ret.target.cv = cv_const
    else:
      ret.cv = cv_const
    
    return ret
  elif isinstance(t, VariableType):
    return _convertToMSVCType(t.type)
  else:
    print(t)
    raise NotImplementedError


def mangling_msvc(funcObj: CSEL.TypeTable.FuncType):
  print(funcObj)
  names = funcObj.name
  if isinstance(names, str):
    names = names.split(".")
  
  # funcObj = Function(["System", "out", "println"],
  #                   FunctionType(cconv_cdecl, SimpleType(0, t_void),
  #                                [PtrType(cv_const, SimpleType(0, t_char), False, as_msvc_x64_absolute),
  #                                 SimpleType(0, t_ellipsis)], None),
  #                   fn_free,
  #                   None,
  #                   as_default)
  
  cconv_type = cconv_cdecl
  rettype = _convertToMSVCType(funcObj.rettype)
  ftype = Function(names,
                   FunctionType(cconv_type,
                                rettype,
                                [_convertToMSVCType(arg.type) for arg in funcObj.args],
                                None),
                   fn_free,
                   None,
                   as_default)
  
  return msvc_mangle(ftype)
