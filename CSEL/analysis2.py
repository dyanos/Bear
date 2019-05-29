#!/usr/bin/env python
import os,sys,string

# local 변수임....
DEBUG_NONE = 0
DEBUG_INFO = 1

class Something:
  def debug(self, level, msg):
    pass

  # 주어진 Object가 Natural Object가 아닌지 맞는지를 검사하는 함수
  def isObject(self, obj):
    self.debug(DEBUG_INFO, "Calling 'isObject' function")

    if obj.type == "System.lang.Integer"  \
      or obj.type == "System.lang.Float"  \
      or obj.type == "System.lang.Double":
      return false

    return true

  # 주어진 object가 int형등의 natural object인지 검사
  def isNaturalObject(self, obj):
    self.debug(DEBUG_INFO, "Calling 'isNaturalObject' function")
    return not self.isObject(obj)
  