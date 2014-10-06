#!/usr/bin/env python
from CSEL.parser import *
from CSEL.analysis import *
from CSEL.Operand import *
from CSEL.Intel import *

parser = Parser("sample.prg")
parser.parse()

print "Parsing End"
asmf = open(parser.basename+"64.asm", "wt")
for symbol in parser.mustcompile:
  print symbol
  _, name = symbol
  machine = Translate(parser.stackSymbolList, symbol)

  if machine.codes == None:
    continue

  print "printing code"
  print >>asmf, "%s:" % (name)
  for code in machine.codes:
    print >>asmf, code

asmf.close()
#test = [OpMove(IInteger(4), IUserReg('z')), 
#        OpMove(IInteger(0), IUserReg('w')), 
#        OpMove(IInteger(1), IUserReg('z')), 
#        OpMove(IUserReg('w'), IUserReg('x')),
#        OpAdd(IUserReg('z'), IUserReg('x')), 
#        OpMove(IUserReg('w'), IUserReg('y')), 
#        OpAdd(IUserReg('x'), IUserReg('y')), 
#        OpMove(IUserReg('y'), IUserReg('w')), 
#        OpAdd(IUserReg('x'), IUserReg('w'))]

test = [OpMove(IInteger(1), IUserReg('z')),   # z = 1
        OpMove(IUserReg('w'), IUserReg('x')), # x = w
        OpAdd(IUserReg('z'), IUserReg('x')),  # x += z
        OpMove(IUserReg('w'), IUserReg('y')), # y = w
        OpAdd(IUserReg('x'), IUserReg('y')),  # y += x
        OpMove(IUserReg('y'), IUserReg('w')), # w = y
        OpAdd(IUserReg('x'), IUserReg('w'))]  # w += x

print doRegisterAllocation(test, [])
