# for intel x86-64    
RAX = IReg("rax")
RBX = IReg("rbx")
RCX = IReg("rcx")
RDX = IReg("rdx")
RSI = IReg("rsi")
RDI = IReg("rdi")
R8  = IReg("r8")
R9  = IReg("r9")
R10 = IReg("r10")
R11 = IReg("r11")
R12 = IReg("r12")
R13 = IReg("r13")
R14 = IReg("r14")
R15 = IReg("r15")

CS = IReg("cs", nbits = 32)
DS = IReg("ds", nbits = 32)
ES = IReg("es", nbits = 32)
FS = IReg("fs", nbits = 32)
GS = IReg("gs", nbits = 32)

XMM0 = IReg("xmm0")
XMM1 = IReg("xmm1")
XMM2 = IReg("xmm2")
XMM3 = IReg("xmm3")

class Translate2:
    def __init__(self, globalSymbolTable):
        self.tblGlobalSymbol = globalSymbolTable

        self.codeSection = []
        self.dataSection = {}   # data section은 이름을 가지고 있어야 하공...

        self.context = Context()

        self.localSymbolTable = {}

    def getTypeName(self, tree):
        typeName = something
        # isShortName함수는 int, short, byte등을 Full name으로 변경하는 역할을 한다.
        # alias도 마찬가지공...
        if isShortName(typeName):
            return findLongName(typeName)

        return typeName

    def findSymbol(self, name, **args):
        # 이름이 동일한 Symbol들을 다 찾는다. (다른 인자를 가지는 것들 모두를 찾는다.)
        lst = self.tblGlobalSymbol.searchSymbol(name)

        # 위 목록들 중에서 해당 argument를 가지는 인자를 찾는다.

        pass

    def generateLocalTempSymbol(self):
        tmpreg = None
        while True:
            tmpreg = makeTempRegName()
            if not self.localSymbolTable.has_key(tmpreg):
                break

        return tmpreg

    def makeFuncName(self, path, funcname):
        raise NotImplemented

    def procOperator(self, treeInfo):
        left = self.procExpr(treeInfo.left)
        right = self.procExpr(treeInfo.right)
    
        if left.type != right.type:
            # we must find 
            pass

        context.emitCall(self.makeFuncName(left.type, treeInfo.op), left, right)

    def procExpr(self, tree):
        raise NotImplemented

    # return할 type을 결정해서 보냄... 
    def procWord(self, tree):
        if not isinstance(tree, ASTWord):
            return 

        ret = None
        if tree.isType('System.lang.String'):
            # data section에 넣는다
            while True:
                dname = makeDataName()
                if not self.dataSection.has_key(dname):
                    self.dataSection[dname] = tree.value
                    break

            tmpreg = self.generateLocalTempSymbol()
            self.localSymbolTable[tmpreg] = {"type": "System.lang.String"}
            # tmpreg <- dname 주소를 옮기는 경우
            self.context.emitMove(tmpreg, dname)
            ret = Value(reg = tmpreg, reftype = "memory", type = tree.type)

        elif tree.isType('System.lang.Integer') 
            or tree.isType("System.lang.Float")
            or tree.isType("System.lang.Double"):
            tmpreg = self.generateLocalTempSymbol()
            self.localSymbolTable[tmpreg] = {"type": tree.getType()}
            # 'context' clas must have a expression
            self.context.emitMove(tmpreg, tree.value)
            ret = Value(reg = tmpreg, reftype = "value", type = tree.getType())

        return ret

class Translate:
    def __init__(self, globalSymbolTable):
        self.globalSymbolTable = globalSymbolTable
        self.localSymbolTable = {}
        self.context = []

    def getReg(self, info, mustbe = None):
        # infoÀÇ typeÀÌ basic typeÀÎÁö ¾Æ´ÑÁö °Ë»çÇÑ´Ù.
        bType = checkType(info)
        # ±âº» typeÀÌ¸é,
        if bType == True:
            pass
        else:
            pass
        
    def run(self, info):
        if info == None: return
        
        if not isinstance(info, SymbolInfo):
            print "This is not a object of 'SymbolInfo' type"
            return
        
        if info.isNativeAttribute(): return
        
        if info.getType() == SymbolInfo.TYPE_DEF:
            self.localSymbolTable = {}
            self.context = []
            
            self.analyzeDef(info)

        return
    
    def analyzeDef(self, info):
        #print info
        #print info.info

        args = info.info['@arguments']
        retType = info.info['@rettype']
        body = info.info['@body']

        if len(args.history) != 0:
            order = [RCX, RDX, R8, R9, XMM0, XMM1, XMM2, XMM3]
            for item in args.history:
                argName = item.name.array[0]
                argType = convertType(item.type)

                reg = None
                if len(order) == 0:
                    # ¸Þ¸ð¸® À§Ä¡·Î
                    pass
                else:
                    reg = order.pop()
                
                self.localSymbolTable[argName] = {"type": argType, "usedReg": reg}

        # analyze body
        self.analyzeBody(body)

    def mergePathAndFunc(self, path, func):
        return convertSimpleTypeName(path + "." + func)

    def searchSymbol(self, info):
        pass
    
    def analyzeBody(self, body):
        if isinstance(body, ASTExpr):
            self.analyzeBody(body.expr)
        elif isinstance(body, ASTExprs):
            pass
        elif isinstance(body, ASTSimpleExprs):
            for item in body.exprs:
                self.analyzeBody(item)
        elif isinstance(body, ASTOperator):
            operatorName = body.name.value

            left = self.analyzeBody(body.left)
            self.searchSymbol(left)
            right = self.analyzeBody(body.right)
            self.searchSymbol(right)

            print left
            print right

            # 1. to get the types of two variables.
            path = self.mergePathAndFunc(decodeMachineName(left['type']), operatorName) + right['type'] + 'E'
            print path
            if not self.globalSymbolTable.search(path):
                # 2. ¸Â´Â Å¸ÀÔÀÌ ¾øÀ¸´Ï right¸¦ º¯È¯½ÃÅ°°í ´Ù½Ã °Ë»öÇØº»´Ù.
                print "Not found operator : %s" % (path)
                sys.exit(-1)
            # 3. to call function related to operator
            info = self.globalSymbolTable.search(path)
            print "information : ", info
            # globalSymbolTable¿¡¼­ ¾òÀº Á¤º¸¸¦ ÀÌ¿ëÇØ¼­ return typeÀ» ¾Ë¾Æ³½´Ù.
            # ±×°É return
        elif isinstance(body, ASTWord):
            # type : encoded type's name
            # vtype : 'value' or 'id' or something else
            # value : value when vtype is 'value'
            if body.type == "string":
                t = ASTType("System.lang.String", None, None)
                return {"type": convertType(t), "vtype": "value", "value": body.value}
            elif body.type == "int":
                return {"type": "i", "vtype": "value", "value": int(body.value)}
            elif body.type == "float":
                return {"type": "f", "vtype": "value", "value": float(body.value)}
            elif body.type == "double":
                return {"type": "d", "vtype": "value", "value": float(body.value)}
            elif body.type == "bool":
                return {"type": "b", "vtype": "value", "value": int(body.value)}
            elif body.type == "v":
                return {"type": "v", "vtype": "value", "value": None}
            elif body.type == "id":
                if not self.localSymbolTable.has_key(body.value):
                    print "Undefined symbol : %s" % (body.value)
                    sys.exit(-1)

                # argument typeÀÌ Global Symbol Table¿¡ ÀÖ´ÂÁö È®ÀÎÇÏ´Â ÄÚµå
                encodedTypeName = self.localSymbolTable[body.value]
                return {"type": encodedTypeName, "vtype": "id", "symbol": body.value}
            else:
                print "More coding"
                print body
                return None
            
class Encode():
    def __init__(self):
        self.codes = []
        self.stack = []

    def convertInteger(value):
        # using IEEE??
        return 0
    
    def encoding(self, tr):
        for item in tr:
            if tr["type"] == "i":
                comp = OpMoveWithImm(tr["value"])
                self.codes.append(comp)
                self.stack.push(comp.getUsedReg())
            elif tr["type"] == "d":
                comp = OpMoveWithImm(self.convertInteger(tr["value"]))
                self.codes.append(comp)
                self.stack.push(comp.getUsedReg())
                        
class Parser:
  def __init__(self, fn):
    self.isdebug = True

    self.token  = Token(fn)
 
    # for namespace
    self.workingPath = ""
    self.token.nextToken()

  def parse(self):
    context = []
    while self.token.tok != None:
      tree = None
        
      value = self.token.tok.value
      if value == 'namespace':
        tree = self.parseNamespace()
      elif value == 'template':
        tree = self.parseTemplate()
      elif value == 'class':
        tree = self.parseClass()
      elif value == 'use' \
        or value == 'import':
        self.parseUse()
      elif value == 'def':
        tree = self.parseDefFunc()
      elif value == 'var':
        tree = self.parseDefVar(context = None)
      elif value == 'val':
        tree = self.parseDefVal(context = None)
      elif value == '@':
        # parseAttribute
        pass
      elif value == 'native':
        self.token.match(value)
        self.property.append(value)
      else:
        break

      if tree != None:
        context.append(tree)

    return context

  def parseNamespace(self):
    if not self.token.match('namespace'):
      return None

    old_scope         = self.now_scope

    names = self.parseNames(limitLen = 0)
    if len(self.now_scope) == 0:
      self.now_scope = names.array
    else:
      self.now_scope = self.now_scoop + names.array

    content = None
    if not self.token.match(';'):
      self.token.match('{')
      content = self.parse()
      self.token.match('}')

    ret_tree = ASTNamespace(ASTNames(self.now_scope), content)

    self.now_scope     = old_scope
    return ret_tree

  def parseTemplate(self):
    if not self.token.match('template'):
      return None

    type_info = {"@type": "template"}

    args = self.parseTemplateDefArgs()
    if tmpl == None or len(tmpl) == 0:
      print "Error) Need more template arguments"
      sys.exit(-1)

    # will change regular expression 
    postfix = "".join(map(lambda x: "".join(["?", x]), tmpl))

    tree = None

    value = self.token.tok.value
    if value == 'template':
      tree = self.parseTemplate()
    elif value == 'class':
      tree = self.parseClass()
    elif value == 'def':
      tree = self.parseDefFunc()
    elif value == 'var':
      tree = self.parseDefVar()
    elif value == 'val':
      tree = self.parseDefVal()

    return ASTTemplate(args, tree, type_info = type_info)

  def parseTemplateDefArgs(self):
    if not self.token.match('<'):
      return None

    items = []
    
    while True:
      self.token.match('class')
      name = self.parseNames(limitLen = 1)
      if name[0] in items:
        print "duplicated template name"
        sys.exit(-1)
      else:
        items.append(name[0])
        if not self.token.match(','):
          break
    
    self.token.match('>')
    return items

  def parseClass(self):
    if not self.token.match('class'):
      return None

    type_info = {"@type": "class"}

    cname = self.parseNames(limitLen = 0)
    fname = self.now_scope + cname.array

    if len(cname.array) == 1:
      type_info['@short'] = cname.array[0]
    else:
      type_info["@short"] = ".".join(cname.array[-1])
    type_info["@long"] = fname
    
    type_info["@property"] = self.property
    self.property = []

    symbolTable.reg_symbol(type_info)
  
    # 단순히 정의만...
    # class xxx.xxx.xxx;
    if self.token.match(';'):
      return ASTClass(type_info)

    # 상속 
    if self.token.match(':'):
      level = self.token.tok.value

      if level != 'public' and level != 'protected' and level != 'private':
        print "Error) We didn't want '%s'" % level
        sys.exit(-1)
      
      self.token.nextToken()

      oname = self.parseNames(limitLen = 0)
      lst   = symbolTable.search(oname.array)
      if lst == None:
        print "Not found that symbol"
        exit(-1)

      if lst['type'] != 'class':
        print "You must use class instead of %s" % (lst['type'])
        exit(-1)

      type_info["@parent"] = lst['value']

    self.token.match('{')
    type_info['@children'] = {}
    self.parseClassBody(type_info)
    self.token.match('}')

    return ASTClass(type_info)

  def parseClassBody(self, context):
    level = "public"

    while True:
      _info = None
      value = self.token.tok.value
      if value == 'public':
        self.token.match('public')
        self.token.match(':')
        level = "public"
      elif value == 'private':
        self.token.match('private')
        self.token.match(':')
        level = "private"
      elif value == 'protected':
        self.token.match('protected')
        self.token.match(':')
        level = 'protected'
      elif value == 'def':
        _info = self.parseDefFuncAtClass(context)
      elif value == 'var':
        _info = self.parseDefVarAtClass(context)
      elif value == 'val':
        _info = self.parseDefValAtClass(context)
      else:
        break

      if _info != None:
        _info['@level'] = level

  def parseUse(self):
    if not self.token.match('use') \
      and not self.token.match('import'):
      return

    # in general
    # use <external namespace>;
    names = self.parseNames(limitLen = 0)
    _name  = ".".join(names.array)

    # to load namespace information
    # however, ...
    type_info = {
      "@type" : "class",
      "@long" : names.array,
      "@short": names.array[-1]}
    symbolTable.reg_symbol(type_info)
 
    if self.token.match('='):
      # use <external namespace> = <alias name>;
      alias = self.parseNames(limitLen = 1)
      self.token.nextToken(';')
      _alias = "".join(alias.array)
      if self.reverse_stack.has_key(alias[0]):
        self.reverse_stack[alias[0]].append(names.array)
      else:
        self.reverse_stack[alias[0]] = [names.array]

      type_info = {
        "@type"  : "alias",
        "@alias" : names.array[-1],
        "@long"  : [names.array[-1]],
        "@target": ".".join(names.array)}
      symbolTable.reg_symbol(type_info)

    self.token.match(';')
  
  def parseNames(self, limitLen = 1):
    if self.token.match('_'):
      return ASTNames(['_'])
    elif self.token.tok.type != 'id':
      return None

    history = [self.token.tok.value]
    self.token.nextToken()
    if self.token.tok.value == '.' and limitLen == 1:
      print "we just needed one word!"
      sys.exit(-1)

    while self.token.match('.'):
      history.append(self.token.tok.value)
      self.token.nextToken()

    return ASTNames(history)

  def search_type(self, type):
    name  = type.name
    templ = type.templ
    ranks = type.ranks

    lst   = symbolTable.search_from_last(name)
    if lst == None: return False

    return True

  def convert_to_str(self, type):
    def __inner(__templ):
      if __templ == None:
        return None

      str = None
      for item in _templ.history:
        str  = '<'
        str += self.convert_to_str(item)
        str += '>'
        
      return str
      
    name  = ".".join(type.name)
    templ = __inner(type.templ)
    ranks = None
    if type.ranks != None:
      for item in type.ranks.history:
        ranks += '[]'

    return "".join([name, templ, ranks])
 
  def parseDefFunc(self):
    if not self.token.match('def'):
      return None

    type_info = {}

    type_info['@type']     = 'function'
    type_info['@property'] = []

    # to make full path
    name = self.parseNames(limitLen = 1)
    
    type_info['@name'] = name.array[0]

    if len(self.workingPath) != 0:
      type_info['@path'] = self.workingPath + "." + type_info['@name']
    else:
      type_info['@path'] = type_info['@name']
      
    self.token.match('(')
    args  = self.parseFuncArgsList()
    self.token.match(')')

    mangling = []
    if len(args.history) != 0:
      for item in args.history:
        print item.type
        typename = convertType(item.type)
        mangling.append(typename)
      
    type_info["@arguments"] = args

    #type_info['@symbol'] = encodeSymbolName(type_info['@long'], type_info['@arguments'])
    
    type  = None
    if self.token.match(':'):
      type = self.parseType()
      type_info["@rettype"] = type

    if not self.token.match(';'):
      body  = None
      if self.token.match('='):
        body  = self.parseExpr()
      elif self.token.match('{'):
        body  = self.parseExprs()
        self.token.match('}')

      type_info["@body"] = body
    else:
      type_info["@body"] = None

    symbolTable.registerSymbol(type_info['@path'], "".join(mangling), DefSymbolInfo(isNative = False, info = type_info))
    sourceSets.append({"path": type_info['@path'],
                       "info": DefSymbolInfo(isNative = False, info = type_info)})
    return type_info


  def parseDefFuncAtClass(self):
    if not self.token.match('def'):
      return None

    type_info = {}

    type_info['@type']     = 'function'
    type_info['@property'] = []

    # to make full path
    _tmp = self.parseNames(limitLen = 1)
    if _tmp.array[0] == '~':
      type_info['@type'] = 'destructor'
      _tmp = self.parseNames(limitLen = 1)

    path = _tmp.array[0]
    # 생성자인지 채크한다. 
    cls_name = context['@short']
    if cls_name == _tmp.array[0]:
      type_info['@type'] = 'constructor'
    #elif _tmp.array[0] == '+':
    #  pass

    type_info["@short"] = path
    type_info["@long"] = context['@long'] + [path]

    self.token.match('(')
    args  = self.parseFuncArgsList()
    self.token.match(')')
    
    args_info = {}
    for item in args.history:
      if isinstance(item, ASTEmpty):
        break
      elif isinstance(item, ASTSet):
        # 이거에 대해서는 아직 결정된바가 없다.
        pass
      elif isinstance(item, ASTDefArg):
        name = item.name.array[0]
        # 1. name 중복성 체크
        if args_info.has_key(name):
          print "duplicated name at argument list : %s" % (name)
          sys.exit(-1)
       
        # 2. 그 다음 type의 symbol check : argument parsing을 할때 검사했기에
        # 3. 만들기
        args_info[name] = item.type

    type_info["@arguments"] = args_info

    # 일단 template 제외
    print type_info['@long']
    print type_info['@arguments']

    type_info['@symbol'] = encodeSymbolName(type_info['@long'], type_info['@arguments'])
    
    type  = None
    if self.token.match(':'):
      type = self.parseType()
      type_info["@rettype"] = type

    if not self.token.match(';'):
      body  = None
      if self.token.match('='):
        body  = self.parseExpr()
      elif self.token.match('{'):
        body  = self.parseExprs()
        self.token.match('}')

      type_info["@body"] = body
    else:
      type_info["@body"] = None

    symbolTable.reg_symbol(type_info)
    print symbolTable.hierarchy
    return type_info

  def parseDefInnerFunc(self):
    if not self.token.match('def'):
      return None

    type_info = {}

    type_info['@type']     = 'function'
    type_info['@property'] = []

    # to make full path
    _tmp = self.parseNames(limitLen = 1)
    path = _tmp.array[0]
    type_info['@property'].append('lambda')
    type_info["@name"] = path

    self.token.match('(')
    args  = self.parseFuncArgsList()
    self.token.match(')')
    
    args_info = {}
    for item in args.history:
      if isinstance(item, ASTEmpty):
        break
      elif isinstance(item, ASTSet):
        # 이거에 대해서는 아직 결정된바가 없다.
        pass
      elif isinstance(item, ASTDefArg):
        name = item.name.array[0]
        # 1. name 중복성 체크
        if args_info.has_key(name):
          print "duplicated name at argument list : %s" % (name)
          sys.exit(-1)
       
        # 2. 그 다음 type의 symbol check : argument parsing을 할때 검사했기에
        # 3. 만들기
        args_info[name] = item.type

    type_info["@arguments"] = args_info
    
    type  = None
    if self.token.match(':'):
      type = self.parseType()
      type_info["@rettype"] = type

    body  = None
    if self.token.match('='):
      body  = self.parseExpr()
    elif self.token.match('{'):
      body  = self.parseExprs()
      self.token.match('}')

    type_info["@body"] = body
    
    return ASTDeclFunc(type_info)

  def parseFuncArgsList(self):
    history = []
    while True:
      isset = False
      if self.token.match('*'): 
        isset = True

      name = self.parseNames(limitLen = 1) 
      if name == None:
        history.append(ASTEmpty())
        break

      if isset:
        history.append(ASTSet([name]))
      else:
        self.token.match(':')
        type = self.parseType()
        history.append(ASTDefArg(name, type))

      if not self.token.match(','): break
    return ASTArgList(history)
      
  def parseType(self):
    names = self.parseNames(limitLen = 0)
    tmpl  = self.parseTemplatePart()
    #ename, body = symbolTable.search(names.array)
    #if ename == None:
    #  print "doesn't exist symbol : %s" % (".".join(names.array))
    #  sys.exit(-1) # 일단 죽이고... 나중에 에러처리 생각
    #else:
    #  names.array = ename

    rank  = self.parseRankList()
    return ASTType(names, tmpl, rank)

  def parseTemplatePart(self):
    if not self.token.match('<'):
      return None

    ret = self.parseTemplateArgs()
    self.token.match('>')
    return ret

  def parseTemplateArgs(self):
    history = [self.parseType()]
    while self.token.match(','):
      history.append(self.parseType())
    return ASTTemplateList(history)

  def parseRankList(self):
    history = None
    while self.token.match('['):
      history.append(ASTEmpty())
      self.token.match(']')
    return history

  def parseExprs(self):
    history = []
    while True:
      tree = self.parseExpr()
      if tree == None: break
      history.append(tree)

    return ASTExprs(history)

  def parseExpr(self):
    if self.token.tok == None:
      return None
    
    which = self.token.tok.value
    ret = None
    if which == 'if':
      ret = self.parseIfStmt()
    elif which == 'for':
      ret = self.parseForStmt()
    elif which == 'var':
      ret = self.parseDefInnerVar()

      #realname = ret.name[0]
      #if self.findAt(tbl = self.local_symtbl, target = realname):
      #  print "duplicated name : %s" % (realname)
      #  sys.exit(-1)

      ## to check type
      #typename = convertType(ret.type)
      #if self.validateType(typename) == False:
      #  print "no type!"
      #  sys.exit(-1)

      #self.local_symtbl[realname] = {"attribute": None, "type": typename}
      ## 해당 Type에 assign operator가 있는지 확인
      #if ret.code != None:
      #  rname = self.makeMethodName(type, '=')
      #  if response != None:
      #    ret = ASTFuncCall(rname, ret.code)
      #  else:
      #    print "no method!"
      #    sys.exit(-1) # 일단 무조건 죽이고 본다.
      #else:
      #  ret = ASTEmpty()
    elif which == 'val':
      ret = self.parseDefInnerVal()

      #realname = ret.name[0]
      #if self.findAt(tbl = self.local_symtbl, target = realname):
      #  print "duplicated name : %s" % (realname)
      #  sys.exit(-1)

      ## to check type
      #typename = convertType(ret.type)
      #if self.validateType(typename) == False:
      #  print "no type!"
      #  sys.exit(-1)

      #self.local_symtbl[realname] = {"attribute": ["readonly"], "type": typename}
      ## 해당 Type에 assign operator가 있는지 확인
      #if ret.code != None:
      #  rname = self.makeMethodName(type, '=')
      #  if response != None:
      #    ret = ASTFuncCall(rname, ret.code)
      #  else:
      #    print "no method!"
      #    sys.exit(-1) # 일단 무조건 죽이고 본다.
      #else:
      #  ret = ASTEmpty()
    elif which == '{':
      ret = self.parseBlockExprs()
    else:
      ret = self.parseSimpleExpr1()
      if ret == None: return None

    return ASTExpr(ret)

  def parseSimpleExpr1(self):
    if self.token.tok == None:
      return None
    
    ret = self.parseSimpleExprs()
    if self.token.match('?'):
      body = self.parseMatchingCases()
      ret  = ASTPatternMatch(cond = ret, body = body)
    if ret == None: return None
    return ret
 
  def parseIfStmt(self):
    if not self.token.match('if'):
      return None

    cond = self.parseExpr()
    self.token.match(':')
    body = self.parseExpr()
    return ASTIf(cond, body)

  def parseForStmt(self):
    if not self.token.match('for'):
      return None

    cond = self.parseExpr()
    self.token.match(':')
    body = self.parseExpr()
    return ASTFor(cond, body)

  def parseDefVar(self):
    if not self.token.match('var'):
      return None

    name = self.parseNames(limitLen = 1)
    if not isLambda:
      name = self.now_scope + name

    self.token.match(':')
    type = self.parseType()
    init = None
    if self.token.match('='):
      init = self.parseExpr()
    return ASTVar(name, type, init)

  def parseDefVal(self):
    if not self.token.match('val'):
      return None

    name = self.parseNames(limitLen = 1)
    #if not isLambda:
    #  name = self.now_scope + name

    self.token.match(':')
    type = self.parseType()
    init = None
    if self.token.match('='):
      init = self.parseExpr()

    return ASTVal(name, type, init)

  def parseDefInnerVar(self):
    if not self.token.match('var'):
      return None

    name = self.parseNames(limitLen = 1)
    if not isLambda:
      name = self.now_scope + name

    self.token.match(':')
    type = self.parseType()
    init = None
    if self.token.match('='):
      init = self.parseExpr()
    return ASTVar(name, type, init)

  def parseDefInnerVal(self):
    if not self.token.match('val'):
      return None

    name = self.parseNames(limitLen = 1)
    #if not isLambda:
    #  name = self.now_scope + name

    self.token.match(':')
    type = self.parseType()
    init = None
    if self.token.match('='):
      init = self.parseExpr()

    return ASTVal(name, type, init)

  def parseBlockExprs(self):
    if not self.token.match('{'):
      return None
    body = self.parseExprs()
    self.token.match('}')
    return ASTBlock(body)

  def parseSimpleExprs(self):
    history = []
    while True:
      tree = self.parseSimpleExpr()
      if tree == None: break
      if self.token.tok == None:
        history.append(tree)
        break
      if self.token.tok.value == ',':
        hist = [tree]
        while self.token.match(','):
          tree = self.parseSimpleExpr()
          hist.append(tree)
        tree = ASTSet(hist)
      history.append(tree)

    if len(history) == 0: return None
    self.token.match(';') # caution!!
    return ASTSimpleExprs(history)

  def searchSymbolInLocal(self, name):
    # search at argument symbol list
    if len(self.argumentSymbolTbl) != 0:
      if self.argumentSymbolTbl.has_key(name):
        return convertType(self.argumentSymbolTbl[name])
    # search at local symbol list
    if len(self.localSymbolTbl) != 0:
      if self.localSymbolTbl.has_key(name):
        return convertType(self.localSymbolTbl[name])
    # search at global symbol list
    if len(self.symtbl) != 0:
      return None

    return None
    
  def parseSimpleExpr(self):
    tree = self.parseBasicSimpleExpr()
    if tree == None: return None
    while True:
      tok = self.token.tok
      if tok == None: break
      if self.token.match('.'):
        right = self.parseBasicSimpleExpr()
        if isinstance(tree, ASTWord):
          if isinstance(right, ASTWord):
            tree = ASTNames([tree.value, right.value])
          elif isinstance(right, ASTFuncCall):
            tree = ASTFuncCall(ASTNames([tree.value, right.name.value]), right.body)
          elif isinstance(right, ASTIndexing):
            tree = ASTIndexing(ASTNames([tree.value, right.name.value]), right.history)
        elif isinstance(tree, ASTNames):
          if isinstance(right, ASTWord):
            tree = ASTNames(tree.array + [right.value])
          elif isinstance(right, ASTFuncCall):
            tree = ASTFuncCall(ASTNames(tree.array + [right.name.value]), right.body)
          elif isinstance(right, ASTIndexing):
            tree = ASTIndexing(ASTNames(tree.array + [right.name.value]), right.history)
        else:
          tree = ASTOperator(ASTWord(tok.type, tok.value), tree, right)
      elif tok.type == 'id':
        #if isinstance(tree, ASTSet):
        #  #if len(tree.lst) != 1:
        #  #  print "error!!" # make error!!
        #  if self.check_type(tree.lst[0]):
        #    tree = ASTCasting(tree.lst[0], ASTWord(tok.type, tok.value))
        self.token.nextToken()
        right = self.parseBasicSimpleExpr()
        tree = ASTOperator(ASTWord(tok.type, tok.value), tree, right)
      else:
        break

    return tree

  def parseBasicSimpleExpr(self):
    tok = self.token.tok
    if tok == None: return None
    if tok.type == 'stringLiteral': 
      self.token.nextToken()
      return ASTWord('string', tok.value)
    elif tok.type == 'integerLiteral':
      self.token.nextToken()
      return ASTWord('int', tok.value)
    elif tok.type == 'floatLiteral':
      self.token.nextToken()
      return ASTWord('float', tok.value)
    elif self.token.match('true'):
      return ASTWord('bool', '1')
    elif self.token.match('false'):
      return ASTWord('bool', '0')
    elif self.token.match('return'):
      return ASTReturn(self.parseExpr())
    elif tok.value == 'def':
      ret = self.parseDefInnerFunc()

      #if len(ret.name) != 1:
      #  print "don't use namespace!"
      #  sys.exit(-1)

      #realname = ret.name[0]
      #if realname == '_':
      #  realname = self.genTemporaryName()  
      #if self.findAt(tbl = self.local_symtbl, target = ret.name):
      #  print "already defined!"
      #  sys.exit(-1)

      #typename = convertType(ret.ret)
      #if not self.validateType(typename):
      #  print "not declare type"
      #  sys.exit(-1)
      
      #self.local_symtbl[realname] = {
      #  "attribute": ["lambda"], 
      #  "args": ret.args, 
      #  "type": typename, 
      #  "body": ret.body}

      return ret
    elif tok.type == 'id':
      self.token.nextToken()
      if self.token.tok == None:
        return ASTWord(tok.type, tok.value)
      
      if self.token.tok.value == '[':
        history = []
        while self.token.match('['):
          history.append(self.parseSimpleExpr())
          self.token.match(']')
        return ASTIndexing(ASTWord(tok.type, tok.value), history)
      elif self.token.match('('):
        args = self.parseArgumentList()
        self.token.match(')')
        return ASTFuncCall(ASTWord(tok.type, tok.value), args)
      else:
        return ASTWord(tok.type, tok.value)
    elif tok.value == '_':
      self.token.nextToken()
      return ASTWord('v', tok.value)
    elif tok.value == '[':
      self.token.match('[')
      history = []
      tree = self.parseSimpleExpr()
      if self.token.match('...'):
        right = self.parseSimpleExpr()
        self.token.match(']')
        return ASTListGenerateType1(tree, right)
      elif self.token.tok.value == ',':
        history.append(tree)
        while self.token.match(','):
          item = self.parseSimpleExpr()
          history.append(item)
        self.token.match(']')
        return ASTListValue(history)
       
      self.token.match(']')
      return ASTListValue([tree])
    elif tok.value == '(':
      self.token.match('(')
      tree = self.parseSimpleExpr1()
      self.token.match(')')
      return ASTWrap(tree)

    return None

  def parseArgumentList(self):
    # 인자로 if나 for문이 올 수 있다면 아래것 그대로 사용하면 ㅇㅋ,
    # 하지만 그렇지 않다면...
    tree = self.parseExpr()
    if tree == None: return None

    history = [tree]
    while self.token.match(','):
      history.append(self.parseExpr())

    return ASTArgList(history)

  def parseMatchingCases(self):
    history = []
    while True:
      left = self.parseSimpleExpr()
      self.token.match('=>')
      right = self.parseSimpleExpr()
      if self.token.match(';'): break
      history.append(ASTCase(left, right))
      self.token.match(',')

    return ASTCases(history)

#print parser.symbolTable.hierarchy
#for key in parser.symbolTable.hierarchy:
#  print key
def genRandomString(length):
  chars  = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_$#@~.?"
  locs   = [random.uniform(0, len(chars)) for i in range(0, length)]
  if locs[0] > chars.index('Z'):
    locs[0] = random.uniform(0, chars.index('Z'))
  return map(lambda loc: chars[loc], locs)
