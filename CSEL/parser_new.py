#!/usr/bin/env pythone
# -*- coding: utf-8 -*-
import traceback

from .Token import *

from .AST import *
from .ASTAlias import *
from .ASTDefArg import *
from .ASTArgList import *
from .ASTAttribute import *
from .ASTTemplate import *
from .ASTClass import *
from .ASTDeclFunc import *
from .ASTEmpty import *
from .ASTExpr import *
from .ASTExprs import *
from .ASTFor import *
from .ASTFuncCall import *
from .ASTIf import *
from .ASTListGenerateType1 import *
from .ASTNames import *
from .ASTNamespace import *
from .ASTOperator import *
from .ASTRankSpecs import *
from .ASTSimpleExprs import *
from .ASTTemplateList import *
from .ASTType import *
from .ASTUse import *
from .ASTVal import *
from .ASTVar import *
from .ASTWord import *
from .ASTBlock import *
from .ASTIndexing import *
from .ASTSet import *
from .ASTCase import *
from .ASTCases import *
from .ASTPatternMatch import *
from .ASTTrue import *
from .ASTFalse import *
from .ASTReturn import *
from .ASTWrap import *
from .mangle import *

class Parser():
  def __init__(self, fn):
    self.token = Token(fn)
    self.token.nextToken()
