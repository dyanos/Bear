# -*- coding: utf-8 -*-
#!/usr/bin/env python
import os,sys,string

import re
import ply.lex as lex
import ply.yacc as yacc

# for debugging
import traceback

literals = ",.(){}[]:#@"

reserved = {
    '' : 'EOF',
    'if' : 'IF',
    'for' : 'FOR',

    'else' : 'ELSE',
    'val' : 'VAL',
    'var' : 'VAR',
    'def' : 'DEF',
    'true' : 'TRUE',
    'false' : 'FALSE',
    'class' : 'CLASS',

    'use' : 'USE',
    'import' : 'IMPORT',
    'return' : 'RETURN',
    'match' : 'MATCH',
    '?' : 'MATCH',
    '->' : 'RIGHTARROW',
    '=>' : 'RIGHTBIGARROW',
    '<:' : 'LEFTSUCCESSION',
    ':>' : 'RIGHTSUCCESSION',
    ':' : 'COLONS',
    '_' : '_',
    }

tokens = [
    'threedot',
    'DOUBLEDOT',
    'newline',
    'op',
    'id',
    'floatingLiteral',
    'integerLiteral',
    'symbolLiteral',
    'characterLiteral',
    'stringLiteral',
    'mathLiteral',
    'semi'
    ] + list(reserved.values())

upper = r'[A-Z$_]'
lower = r'[a-z]'
letter = r'('+upper+'|'+lower+')'
digit = r'[0-9]'
opchar = r"""[^0-9a-zA-Z\s$_\[\]{}()'`";,\.:=#@]"""

octalDigit = r'[0-7]'
nonZeroDigit = r'[1-9]'
digit = r'[0-9]'
hexDigit = r'' + digit + '[a-fA-F]'
octalNumeral = r'0'+octalDigit+'+'
hexNumeral = r'0x'+hexDigit+'+'
decimalNumeral = r''+digit+'+'
exponentPart = r'[Ee][-+]?'+digit+'+'
floatType = r'[FfDd]'
idrest = r'('+letter+'|'+digit+')*(_'+opchar+')?'
varid = r''+lower+idrest
plainid = r'('+upper+idrest+'|'+varid+'|'+opchar+'+)'

simple_escape = r"""([a-zA-Z\\?'"])"""
octal_escape = r"""([0-7]{1,3})"""
hex_escape = r"""(x[0-9a-fA-F]+)"""
escape_sequence = r"""(\\("""+simple_escape+'|'+octal_escape+'|'+hex_escape+'))'
cconst_char = r"""([^'\\\n]|"""+escape_sequence+')'
char_const = "'"+cconst_char+"'"
string_char = r"""([^"\\\n]|"""+escape_sequence+')'
string_literal = '"'+string_char+'*"'

op = r''+opchar+'+'
#t_id = ur'[a-zA-Z][a-zA-Z0-9_]*|_[a-zA-Z0-9_]+|_' + opchar +'+|' + opchar + '+|\'' + string_char + '+\''
t_integerLiteral = r'('+decimalNumeral+'|'+hexNumeral+'|'+octalNumeral+')[L|l]?'
t_floatingLiteral = r"("+digit+"+\."+digit+"*("+exponentPart+")?("+floatType+")?|\."+digit+"+("+exponentPart+")?("+floatType+")?|"+digit+"+"+exponentPart+"("+floatType+")?|"+digit+"+("+exponentPart+")?"+floatType+")"
#t_characterLiteral = ur"'("+string_char+")\'"
#t_stringLiteral = ur'("'+string_char+'*"|""\"'+string_char+'*""\")'
t_semi = r'(;|\n+)'
t_threedot = r'\.\.\.'

def t_newline(t):
    r'\n'
    t.lexer.lineno = t.lexer.lineno + 1 

def t_comment(t):
    r'(/\*(.|\n)*\*/)|(//.*)'
    pass

def t_characterLiteral(t):
    r"""'([a-zA-Z0-9_]|[^\w\n])?'"""
    return t

def t_stringLiteral(t):
    r'"[^\n]*"'
    return t

def t_mathLiteral(t):
    r'`[^\n]`'
    return t

def t_symbolLiteral(t):
    r"""'[^\w\[\]\.\n;]'"""
    return t

# id��� `��� ������������ ��������� ������ ������ ������ ������ ������(2013.03.12)
# `������ ������������ ��������� `@abc123`������ ��������� ������+id��������� id��� ������������ ��������� ������
def t_id(t):
    r"""[a-zA-Z_][0-9a-zA-Z_]*|[^\w\s$\[\]{}\(\)'`";,\.]+|[^0-9a-zA-Z\(\){}[]\.,:]*"""
    if t.value == "_":
        t.type = t.value
    else:
        t.type = reserved.get(t.value, "id")
    return t

t_ignore = ' \t'

def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)
 
class Token:
  def __init__(self, fn = None):
    self.lexer = lex.lex(debug = 0)
    
    self.locking:bool = False
    self.history = []
    self.checkpt = []
    self.pos = 0
    self.refcnt = 0

    self.nAccept = 0
    self.nReject = 0

    self.tok = None
    if fn is not None or os.path.exists(fn):
      self.code = open(fn, "rt", encoding="utf-8").readlines()
      self.lexer.input("".join(self.code))

    self.tok = None

  def save(self):
    if self.locking == False:
      self.locking = True
      self.nAccept = 0
      self.nReject = 0
      self.checkpt = [(0, self.tok)]
    else:
      self.checkpt.append((self.pos, self.tok))
    
    self.incRef()

  def incRef(self):
    self.refcnt = self.refcnt + 1

  def decRef(self):
    self.refcnt = self.refcnt - 1

  def accept(self):
    self.decRef()
    self.nAccept = self.nAccept + 1
    del self.checkpt[len(self.checkpt)-1] # To remove the last element of checkpt
    self.cleanup()

  def cleanup(self):
    if self.refcnt == 0:
      self.locking = False
      self.history = []
      self.checkpt = []
      self.pos = 0
        
  def reject(self):
    self.decRef()
    del self.checkpt[len(self.checkpt)-1] # To remove the last element of checkpt
    self.pos, self.tok = self.checkpt[self.refcnt]

  def nextToken(self):
    if self.locking == False:
      self.tok = self.lexer.token()
    else:
      if self.pos == len(self.history):
        self.tok = self.lexer.token()
        self.history.append(self.tok)
        self.pos = self.pos + 1
      else:
        self.tok = self.history[self.pos]
        self.pos = self.pos + 1
    #print "-",self.tok
    #traceback.print_stack()
    return self.tok

  def same(self, val:str) -> bool:
    if self.tok == None:
      return False

    if self.tok.value == val:
      return True

    return False

  def match(self, val:str) -> bool:
    if self.tok == None:
        return False
    
    if self.tok.value == val:
      self.nextToken()
      return True

    return False

  def sameType(self, typeStr:str) -> bool:
    if self.tok.type == typeStr:
      val = self.tok.value
      return True

    return False

  def matchType(self, typeStr:str) -> str:
    if self.tok.type == typeStr:
      val = self.tok.value
      self.nextToken()
      return val

    return None

  def reachEnd(self) -> bool:
    if self.tok == None or self.tok.type == 'EOF':
      return True

    return False

  def __str__(self) -> str:
    if self.tok != None:
      return "(%s) '%s'" % (self.tok.type, self.tok.value)

    return None
