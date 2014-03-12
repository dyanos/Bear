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
    '=>' : 'RIGHTBIGARROW',
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

upper = ur'[A-Z$_]'
lower = ur'[a-z]'
letter = ur'('+upper+'|'+lower+')'
digit = ur'[0-9]'
opchar = ur"""[^0-9a-zA-Z\s$_\[\]{}()'`";,\.:=#@]"""

octalDigit = ur'[0-7]'
nonZeroDigit = ur'[1-9]'
digit = ur'[0-9]'
hexDigit = ur'' + digit + '[a-fA-F]'
octalNumeral = ur'0'+octalDigit+'+'
hexNumeral = ur'0x'+hexDigit+'+'
decimalNumeral = ur''+digit+'+'
exponentPart = ur'[Ee][-+]?'+digit+'+'
floatType = ur'[FfDd]'
idrest = ur'('+letter+'|'+digit+')*(_'+opchar+')?'
varid = ur''+lower+idrest
plainid = ur'('+upper+idrest+'|'+varid+'|'+opchar+'+)'

simple_escape = ur"""([a-zA-Z\\?'"])"""
octal_escape = ur"""([0-7]{1,3})"""
hex_escape = ur"""(x[0-9a-fA-F]+)"""
escape_sequence = ur"""(\\("""+simple_escape+'|'+octal_escape+'|'+hex_escape+'))'
cconst_char = ur"""([^'\\\n]|"""+escape_sequence+')'
char_const = "'"+cconst_char+"'"
string_char = ur"""([^"\\\n]|"""+escape_sequence+')'
string_literal = '"'+string_char+'*"'

op = ur''+opchar+'+'
#t_id = ur'[a-zA-Z][a-zA-Z0-9_]*|_[a-zA-Z0-9_]+|_' + opchar +'+|' + opchar + '+|\'' + string_char + '+\''
t_integerLiteral = ur'('+decimalNumeral+'|'+hexNumeral+'|'+octalNumeral+')[L|l]?'
t_floatingLiteral = ur"("+digit+"+\."+digit+"*("+exponentPart+")?("+floatType+")?|\."+digit+"+("+exponentPart+")?("+floatType+")?|"+digit+"+"+exponentPart+"("+floatType+")?|"+digit+"+("+exponentPart+")?"+floatType+")"
#t_characterLiteral = ur"'("+string_char+")\'"
#t_stringLiteral = ur'("'+string_char+'*"|""\"'+string_char+'*""\")'
t_semi = ur'(;|\n+)'
t_threedot = ur'\.\.\.'

def t_newline(t):
    ur'\n'
    t.lexer.lineno = t.lexer.lineno + 1 

def t_comment(t):
    ur'(/\*(.|\n)*\*/)|(//.*)'
    pass

def t_characterLiteral(t):
    ur"""'([a-zA-Z0-9_]|[^\w\n])?'"""
    return t

def t_stringLiteral(t):
    ur'"[^\n]*"'
    return t

def t_mathLiteral(t):
    ur'`[^\n]`'
    return t

def t_symbolLiteral(t):
    ur"""'[^\w\[\]\.\n;]"""
    return t

# id��� `��� ������������ ��������� ������ ������ ������ ������ ������(2013.03.12)
# `������ ������������ ��������� `@abc123`������ ��������� ������+id��������� id��� ������������ ��������� ������
def t_id(t):
    ur"""[a-zA-Z_][0-9a-zA-Z_]*|[^\w\s$\[\]{}\(\)'`";,\.]+|[^0-9a-zA-Z\(\){}[]\.,:]*"""
    if t.value == "_":
        t.type = t.value
    else:
        t.type = reserved.get(t.value, "id")
    return t

t_ignore = ' \t'

def t_error(t):
    print "Illegal character '%s'" % t.value[0]
    t.lexer.skip(1)
 
class Token:
  def __init__(self, fn = None):
    self.lexer = lex.lex(debug = 0)
    
    self.locking = False
    self.history = []
    self.checkpt = []
    self.pos = 0
    self.refcnt = 0

    self.nAccept = 0
    self.nReject = 0

    self.tok = None
    if fn != None or os.path.exists(fn):
      self.code = open(fn,"rt").readlines()
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
    #print self.tok
    return self.tok

  def same(self, val):
    if self.tok == None:
      return False

    if self.tok.value == val:
      return True

    return False

  def match(self, val):
    if self.tok == None:
        return False
    
    if self.tok.value == val:
      self.nextToken()
      return True

    return False

  def sameType(self, typeStr):
    if self.tok.type == typeStr:
      val = self.tok.value
      return True

    return False

  def matchType(self, typeStr):
    if self.tok.type == typeStr:
      val = self.tok.value
      self.nextToken()
      return val

    return None

  def reachEnd(self):
    if self.tok == None or self.tok.type == 'EOF':
      return True

    return False

  def __str__(self):
    if self.tok != None:
      return "(%s) '%s'" % (self.tok.type, self.tok.value)

    return None
