#!/usr/bin/env python

class Operand:
  def __init__(self):
    pass

class IStorage(object):
  def __init__(self, name):
    self.storageTypeStr = name

class IReg(IStorage):
  def __init__(self, name, nbits = 64):
    super(IReg, self).__init__("reg")
    self.name = name

  def __str__(self):
    return self.name

  def __hash__(self):
    return hash(self.name)

  def __eq__(self, right):
    if not isinstance(right, IReg):
      return False

    if self.name != right.name:
      return False

    return True

class IUserReg(IStorage):
  def __init__(self, name, nbits = 64):
    super(IUserReg, self).__init__("userreg")
    self.name = name

  def __str__(self):
    return self.name

  def __hash__(self):
    return hash(self.name)

  def __eq__(self, right):
    if not isinstance(right, IUserReg):
      return False

    if self.name != right.name:
      return False

    return True
      
class IImm(IStorage):
  def __init__(self, value = 0):
    super(IImm, self).__init__("imm")
    self.value = value

  def __str__(self):
    return "%d" % (self.value)

  def __eq__(self, right):
    return False

  def __hash__(self):
    raise Excpetion('IImm', 'Not Implemented')

class IMem(IStorage):
  def __init__(self, base = None, ind = None, imm = None):
    super(IMem, self).__init__("mem")
    self.base = base
    self.indx = ind
    self.imm  = imm

  def __str__(self):
    return "%s * %d + %d" % (self.base, self.indx, self.imm)

  def __eq__(self, right):
    if not isinstance(right, IMem):
      return False

    if self.base != right.base or self.indx != right.indx or self.imm != right.imm:
      return False

    return True      

  def __hash__(self):
    raise Excpetion('IImm', 'Not Implemented')

class IString(IStorage):
  def __init__(self, value):
      super(IString, self).__init__("string")
      self.value = value

  def __str__(self):
      return self.value

  def __hash__(self):
    raise Excpetion('IImm', 'Not Implemented')

  def __eq__(self):
    raise Excpetion('IImm', 'Not Implemented')

class IInteger(IStorage):
  def __init__(self, value):
      super(IInteger, self).__init__("integer")
      if isinstance(value, str):
          self.value = int(value)
      else:
          self.value = value

  def __str__(self):
      return "%d" % (self.value)

  def __eq__(self, right):
    return False

  def __hash__(self):
    raise Excpetion('IImm', 'Not Implemented')

class IFloat(IStorage):
  def __init__(self, value):
      super(IFloat, self).__init__("float")
      self.value = value

  def __str__(self):
      return "%lf" % (self.value)

  def __eq__(self, right):
    return False

  def __hash__(self):
    raise Excpetion('IImm', 'Not Implemented')

class IDouble(IStorage):
  def __init__(self, value):
      super(IDouble, self).__init__("double")
      self.value = value

  def __str__(self):
      return "%lf" % (self.value)

  def __eq__(self, right):
    return False

  def __hash__(self):
    raise Excpetion('IImm', 'Not Implemented')

def isTemporaryRegister(reg):
  if isinstance(reg, IUserReg):
      return True

  return False
