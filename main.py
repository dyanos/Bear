#!/usr/bin/env python
from CSEL.parser import *
from CSEL.analysis import *
from CSEL.Operand import *
from CSEL.Intel import *

parser = Parser("code1.prg")
parser.parse()

CodeSection = {}
DataSection = {}

print("Parsing End")
asmf = open(parser.basename+"64.asm", "wt")
for symbol in parser.mustcompile:
  print(symbol)
  _, name = symbol
  machine = Translate(parser.globalSymbolTable, symbol)

  if machine.codes == None:
    continue

  ds = machine.getDataSection()
  for key in list(ds.keys()):
    DataSection[key] = ds[key]

  CodeSection[name] = machine.codes

print("printing code(sample)")

asmf.write("section .text\n")
for key in list(CodeSection.keys()):
  asmf.write("%s:\n" % (key))
  for code in CodeSection[key]:
    asmf.write("%s\n" % (code))
  asmf.write("\n")

asmf.write("section .data\n")
for key in list(DataSection.keys()):
  asmf.write("%s: db %s\n" % (key, DataSection[key]))

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

print(doRegisterAllocation(test, []))
