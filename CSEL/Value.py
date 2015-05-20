# -*- coding: utf-8 -*-
#!/usr/bin/env python

# value는 그냥 값을 가지고 있으면 되공,
# data는 data section의 위치를 가지고 있으면 되공...
class Value:
  def __init__(self, **kargs):
    for key, value in kargs.iteritems():
      setattr(self, key, value)
      
  def __str__(self):
    attrs = vars(self)
    return ', '.join("%s: %s" % item for item in attrs.items())
