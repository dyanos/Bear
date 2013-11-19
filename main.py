#!/usr/bin/env python
from CSEL.parser import *
from CSEL.analysis import *
from CSEL.Operand import *
from CSEL.Intel import *
parser = Parser("sample.prg")
parser.parse()

print "Parsing End"
for symbol in parser.mustcompile:
  print symbol
  machine = Translate(parser.stackSymbolList, symbol)

#test = [OpMove(IInteger(4), IUserReg('z')), 
#        OpMove(IInteger(0), IUserReg('w')), 
#        OpMove(IInteger(1), IUserReg('z')), 
#        OpMove(IUserReg('w'), IUserReg('x')),
#        OpAdd(IUserReg('z'), IUserReg('x')), 
#        OpMove(IUserReg('w'), IUserReg('y')), 
#        OpAdd(IUserReg('x'), IUserReg('y')), 
#        OpMove(IUserReg('y'), IUserReg('w')), 
#        OpAdd(IUserReg('x'), IUserReg('w'))]

test = [OpMove(IInteger(1), IUserReg('z')),
        OpMove(IUserReg('w'), IUserReg('x')),
        OpAdd(IUserReg('z'), IUserReg('x')), 
        OpMove(IUserReg('w'), IUserReg('y')), 
        OpAdd(IUserReg('x'), IUserReg('y')), 
        OpMove(IUserReg('y'), IUserReg('w')), 
        OpAdd(IUserReg('x'), IUserReg('w'))]

print mapcolour(test)