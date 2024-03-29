# -*- coding: utf-8 -*-
#!/usr/bin/env python
from .Operand import *
import pprint,sys

import networkx as nx
import matplotlib.pyplot as plt

class OpMove(Operand):
  def __init__(self, src, dst):
    self.src = src
    self.dst = dst

  def __str__(self):
    return "mov %s, %s" % (self.dst, self.src)

class OpAdd(Operand):
  def __init__(self, src, dst):
    self.src = src
    self.dst = dst

  def __str__(self):
    return "add %s, %s" % (self.dst, self.src)

class OpSub(Operand):
  def __init__(self, src, dst):
    self.src = src
    self.dst = dst

  def __str__(self):
    return "sub %s, %s" % (self.dst, self.src)

class OpMul(Operand):
  def __init__(self, src, dst):
    self.src = src
    self.dst = dst

  def __str__(self):
    return "mul %s, %s" % (self.dst, self.src)

class OpDiv(Operand):
  def __init__(self, src, dst):
    self.src = src
    self.dst = dst

  def __str__(self):
    return "div %s, %s" % (self.dst, self.src)

class OpPush(Operand):
  def __init__(self, src):
    self.target = src

  def __str__(self):
    return "push %s" % (self.target)

class OpPop(Operand):
  def __init__(self, src):
    self.target = src

  def __str__(self):
    return "pop %s" % (self.target)

class OpCall(Operand):
  def __init__(self, target, numargs, ret = False):
    self.target = target
    self.numargs = numargs
    self.ret = ret

  def isReturn(self):
    return self.ret

  def __str__(self):
    return "call %s" % (self.target)

class OpJump(Operand):
  def __init__(self, target):
    self.target = target

  def __str__(self):
    return "jmp %s" % (self.target)

class OpJumpToReg(Operand):
  def __init__(self, reg):
    self.reg = reg

  def __str__(self):
    return "jmp %s" % (self.reg)

class OpComp(Operand):
  def __init__(self, target1, target2):
    self.target1 = target1
    self.target2 = target2

  def __str__(self):
    return "cmp %s, %s" % (self.target1, self.target2)

class OpJumpZeroFlag(Operand):
  def __init__(self, label):
    self.target = label

  def __str__(self):
    return "jz %s" % (self.target)

class OpRet(Operand):
  def __init__(self):
    pass

  def __str__(self):
    return "ret"

class MarkLabel(Operand):
  def __init__(self, label):
    self.label = label

  def __str__(self):
    return "%s:" % (self.label)

def isRegister(storage):
  if isinstance(storage, IReg) or isinstance(storage, IUserReg):
    return True

  return False

def getRetReg(type = 'System.lang.Int'):
  if type == 'System.lang.Double' or type == 'System.lang.Float':
    return IReg('xmm0')
  
  return IReg("rax")

class RegisterAllocation:
  def __init__(self):
    pass
   
  @staticmethod
  def genInterferenceGraph(lst, outLive, args, _isdebug=False):
    liveList = outLive
    parameterList = [IReg('rcx'), IReg('rdx'), IReg('r8'), IReg('r9')]
    parameterListForFloating = [IReg('xmm0'), IReg('xmm1'), IReg('xmm2'), IReg('xmm3')]
  
    #print len(lst), len(liveList)
  
    #print "calculateInterferenceGraph"
  
    graph, loc = {}, 0
  
    for operand in lst:
      if isinstance(operand, OpMove):
        adjectList = []
  
        if isRegister(operand.src):
          adjectList.append(str(operand.src))
  
        if len(liveList[loc]) != 0:
          #print map(lambda x: str(x), liveList[loc])
          for reg in liveList[loc]:
            if str(operand.dst) == reg:
              continue
  
            adjectList.append(reg)
  
        if not isRegister(operand.dst):
          continue
  
        t = str(operand.dst)
        rn = set([str(x) for x in adjectList])
        if t in graph:
          graph[t] |= rn
        else:
          graph[t] = rn
  
        for e in adjectList:
          if str(e) in graph:
            graph[str(e)] |= set([t])
          else:
            graph[str(e)] = set([t])
  
        #pp.pprint(graph)
      elif isinstance(operand, OpAdd) \
        or isinstance(operand, OpSub) \
        or isinstance(operand, OpMul) \
        or isinstance(operand, OpDiv):
        adjectList = []
        if len(liveList[loc]) != 0:
          #print map(lambda x: str(x), liveList[loc])
          for reg in liveList[loc]:
            if str(operand.dst) == reg:
              continue
  
            adjectList.append(reg)
  
        if not isRegister(operand.dst):
          continue
          
        t = str(operand.dst)
        rn = set([str(x) for x in adjectList])
        if t in graph:
          graph[t] |= rn
        else:
          graph[t] = rn
  
        for e in adjectList:
          if str(e) in graph:
            graph[str(e)] |= set([t])
          else:
            graph[str(e)] = set([t])        
      elif isinstance(operand, OpCall):
        adjectList = [getRetReg()]
        # 일단 정수나 pointer밖에 없다고 가정...
        if operand.numargs <= len(parameterList):
          adjectList += parameterList[0:operand.numargs]
        else:
          adjectList += parameterList
  
        if len(liveList[loc]) == 0:
          continue
  
        for reg in adjectList:
          t = str(reg)
  
          #print map(lambda x: str(x), liveList[loc])
          for areg in liveList[loc]:
            if t == areg: 
              continue
  
            if t in graph:
              graph[t] |= set([areg])
            else:
              graph[t] = set([areg])
  
            if str(areg) in graph:
              graph[areg] |= set([t])
            else:
              graph[areg] = set([t])
  
      #print "display graph info : "
      #for key in graph:
      #  print "%s="%(key),map(lambda x: str(x), graph[key])
  
      loc += 1
  
    if _isdebug:
      pprint.pprint(graph)
      
    return graph
 
  @staticmethod
  def getInfoForRegAllocation(lst, args):
    parameterList = ['rcx', 'rdx', 'r8', 'r9']
    parameterListForFloating = ['xmm0', 'xmm1', 'xmm2', 'xmm3']
  
    nlst = len(lst)
  
    succ = dict([(i, set([])) for i in range(0, nlst+1)]) # 후손에 남겨주는 경우 (From successor)
    pred = dict([(i, set([])) for i in range(0, nlst+1)]) # 선조로부터 오는 경우 (From predecessor)
    def1 = {}   # location defined variables
    def2 = dict([(i, set([])) for i in range(0, nlst+1)]) # definition information of variable of nth's position
    use1 = {}   # location of used variables
    use2 = dict([(i, set([])) for i in range(0, nlst+1)]) # which variable is using at nth's position
  
    def registerDefVar(reg, pos):
      # 시스템 레지스터가 들어올경우 def에서는 0을 다음번 use에서는 그것을 사용하는 식으로 표시한다.
      # 그렇게 하는 이유는 해당 register가 이미 선점된 상태에서, 꼭 사용해야 하는 경우(call에서의 rcx나 연산에서의 rax처럼)
      # 에 대해서 spill out을 쉽게 구현할 수 있기 때문이다.
      # 물론 spill out이 끝난 뒤에는 해당 레지스터들은 복구해야한다. 
      # 네이밍은 rcx0, rcx1처럼 하면됨...
      if not isRegister(reg):
        return 
        
      name = str(reg)
      if name not in def1:
        def1[name] = set([pos])
      else:
        def1[name] |= set([pos])
      
      def2[pos] |= set([name])
  
    def registerUseVar(reg, pos):
      if not isRegister(reg):
        return 
  
      name = str(reg)
      if name not in use1:
        use1[name] = set([pos])
      else:
        use1[name] |= set([pos])
  
      use2[pos] |= set([name])
  
    pred[0] = (-1)  # 이전 instruction은 없다.
    for pos, inst in enumerate(lst):
      real = pos
      # per each instruction
      if isinstance(inst, OpJump):
        label = inst.target
        for i in range(0, nlst):
          if not isinstance(lst[i], MarkLabel):
            continue
  
          if str(lst[i].label) == label:
            succ[real] |= set([i])
            pred[i] |= set([real])
      elif isinstance(inst, OpJumpZeroFlag):
        succ[real] |= set([real + 1])
        pred[real + 1] |= set([real])
        label = inst.target
        for i in range(0, nlst):
          if not isinstance(lst[i], MarkLabel):
            continue
  
          if str(lst[i].label) == label:
            succ[real] |= set([i])
            pred[i] |= set([real])
      elif isinstance(inst, OpJumpToReg):
        # jump되는 곳을 예측할 수 없으므로 일단 skip
        raise Exception('at register allocation algorithm', 'error')
      elif isinstance(inst, OpMove):
        succ[real] |= set([real + 1])
        pred[real + 1] |= set([real])
        registerDefVar(inst.dst, real)
        registerUseVar(inst.src, real)
      elif isinstance(inst, OpAdd) or \
        isinstance(inst, OpSub) or \
        isinstance(inst, OpMul) or \
        isinstance(inst, OpDiv):
        # add a, b = a=a+b
        succ[real] |= set([real + 1])
        pred[real + 1] |= set([real])
        registerDefVar(inst.dst, real)
        registerUseVar(inst.src, real)
        registerUseVar(inst.dst, real)
      elif isinstance(inst, OpPush):
        succ[real] |= set([real + 1])
        pred[real + 1] |= set([real])
        registerUseVar(inst.target, real)
      elif isinstance(inst, OpPop):
        succ[real] |= set([real + 1])
        pred[real + 1] |= set([real])
        registerDefVar(inst.target, real)
      elif isinstance(inst, OpCall):
        succ[real] |= set([real + 1])
        pred[real + 1] |= set([real])
        for i in range(inst.numargs):
          registerUseVar(parameterList[i], real)
        # To add 'return register' to definition list (def1, def2)
        if inst.isReturn() == True:
          registerDefVar(IReg('rax'), real)
  
    nullSet = set([])
    
    oldIn  = [nullSet for i in range(0, nlst+1)] 
    newIn  = [nullSet for i in range(0, nlst+1)]
    oldOut = [nullSet for i in range(0, nlst+1)]
    newOut = [nullSet for i in range(0, nlst+1)]
  
    exitFlag = True  
    while exitFlag:
      #print ind 
      for n, node in enumerate(reversed(lst)):
        real     = nlst - n - 1
        oldIn[real]  = newIn[real]
        oldOut[real] = newOut[real]
        newOut[real] = set([])
        if real in succ:
          for succNodeNum in succ[real]:
            if succNodeNum < 0 or succNodeNum >= nlst:
              continue
  
            newOut[real] |= newIn[succNodeNum]
            
          newIn[real] = use2[real] | (newOut[real] - def2[real])
  
      exitFlag = False
      for n in range(nlst):
        if len(newOut[n]) != 0:
          exitFlag = True
          break 
  
      for n in range(0, nlst):
        if oldIn[n] != newIn[n] or oldOut[n] != newOut[n]:
          exitFlag = False
          break
      
    G = RegisterAllocation.genInterferenceGraph(lst, newOut, args)
    
    # To add arguments to graph's node
    # graph is directional
    s = list(newIn[0])
    for i in range(0, len(newIn[0])):
      reg = s[i]
      for j in range(i, len(newIn[0])):
        if reg in G:
          G[reg] |= set([s[j]])
        else:
          G[reg] = set([s[j]])
  
        if s[j] in G:
          G[s[j]] |= set([reg])
        else:
          G[s[j]] = set([reg])
  
    return G, def1, def2, use1, use2
 
  @staticmethod
  def doGraphColoring(lst, args=[], _isdebug=False):
    G, def1, def2, use1, use2 = RegisterAllocation.getInfoForRegAllocation(lst, args)

    if _isdebug:
      print(G)
  
    registerList = ['rax','rbx','rcx','rdx','rsi','rdi','r8','r9','r10','r11','r12','r13','r14','r15']
    #registerList = ['rax','rbx','rcx','rdx'] # for test of spilling out
  
    symbols = list(G.keys())
    nsymbols = len(symbols)
  
    #print "symbols = ", symbols
    #print "nsymbols = ", nsymbols
  
    # To make a adjacency matrix to represent the interference graph
    assignedColor = {}
    colored = [False for i in range(0, nsymbols)]
    colored2 = {}
    
    availColorList = []
  
    for pos, symbol in enumerate(symbols):
      # if a symbol is already colored, 
      if symbol in registerList:
        assignedColor[symbol] = symbol
        colored[pos] = True
        colored2[symbol] = True
  
    availColorList = [x for x in registerList if not x in symbols]
  
    # 1. SD가 가장 큰 것을 찾는다.
    # 2. 할당되었는지 확인 후 되어있다면, 1번으로 돌아간다.
    # 3. 그것과 인접된 노드들을 찾는다.
    # 4. 이미 어떤 것들이 할당되어 있는지 확인한다.
    # 5. 그것들을 제외한 나머지 것들을 본다.
    # 6. 없다면 spilling
  
    spilling = {}
    preservedStackSize = 0
    
    # using heuristic algorithm
    allvars  = [x for x in symbols if x not in colored2] # except pre-assigned registers
  
    # 모든 변수들이 다 assign되었다면,
    if len(allvars) == 0:
      return assignedColor, spilling
  
    #print "allvars = ", allvars
    while True:
      def SD(G, x, colored):
        return len([e for e in G[x] if e not in colored2])
  
      # to find a node that the number of neighbor nodes is maximum
      allvars = [x for x in allvars if x not in colored2]
      _, symbol = max([(SD(G, x, colored), x) for x in allvars])
      ind = symbols.index(symbol)
      
      # 해당 symbol과 관련있는 녀석들 중에 이미 색칠이 칠해진 녀석들을 찾음.
      # if symbol is already colored, mark it.
      #precolored = []
      #for s in G[symbol]:
      #  if not s in colored2.keys(): # to check that the key 's' is in colored2
      #    continue
        
      #  if s in assignedColor.keys():
      #    precolored.append(assignedColor[s])
  
      # full list중에 색칠이 칠해진 녀석들을 지움 - 그게 가용 registers
      # to find the list of non-assigned registers
      #availColorList = list(set(registerList) - set(precolored))
      # if no available register, spill out
      #print "Symbol", symbol, ", availColorList = ", availColorList
      if not availColorList or len(availColorList) == 0: # 가용 레지스터가 없을 경우
        # use회수가 가장 적은걸 spill하려고 하는데,
        # 이 symbol이 use회수가 가장 적은 symbol과 연결되어 있지 않다면, 의미가 없다.
        # 인접 register들을 찾는다.
        # To find no colored symbol of the other symbols connected 'symbol'
        # Don't worry when remains machine registers. because they can spill out.
        outRegList = [y for y in filter(lambda x: x in colored2, list(G[symbol])) if not y in registerList]
        # We will find a symbol that number of 'use1' of precolored symbols is minimum.
        # and get length of 'use1' and sort it.

        outRegList = [(len(use1[x]), x) if x in use1 else (0, x) for x in outRegList]
        outRegList.sort()
        
        #print outRegList
        
        # 하나를 픽업한다.
        # to pick a symbol to spill out
        outReg = None
        for e, s in outRegList:
          if s not in spilling:
            outReg = s
            break
  
        if outReg == None:
          raise Exception("Error", "Your algorithm is wrong")      
        #print "---", outReg 
  
        pos = symbols.index(outReg)
        
        assignedColor[symbol] = assignedColor.pop(outReg)      
        # the number of spilling symbols : the reservation stack size
        spilling[outReg] = IMem(base = IReg('rbp'), imm = 8 * preservedStackSize)
        preservedStackSize += 1 
        
        #raise Exception('Spilling', 'Spilling')
      else:
        assignedColor[symbol] = availColorList[0]
        del availColorList[0]
      #print symbol, assignedColor[symbol], availColorList[0]
  
      #colored[maxpos] = True
      colored[ind] = True
      colored2[symbol] = True
      
      # to recalculate the number of colored registers
      ncolored = len([x for x in colored if x == True])
      if ncolored == nsymbols:
        break
      
    return assignedColor, spilling
 
  @staticmethod
  def doRegisterAllocation(lst, args):
    print("called doRegisterAllocation")
    #getInfoForRegAllocation(lst, args)
  
    codes = []
  
    ret, spilling = RegisterAllocation.doGraphColoring(lst, args)
    keys = list(ret.keys())
    skeys = list(spilling.keys())
    for operand in lst:
      if isinstance(operand, OpMove) \
        or isinstance(operand, OpAdd) \
        or isinstance(operand, OpSub) \
        or isinstance(operand, OpMul) \
        or isinstance(operand, OpDiv):
        if str(operand.src) in keys:
          operand.src = ret[str(operand.src)]
        if str(operand.dst) in keys:
          operand.dst = ret[str(operand.dst)]
        if str(operand.src) in skeys:
          operand.src = spilling[str(operand.src)]
        if str(operand.dst) in skeys:
          operand.dst = spilling[str(operand.dst)]
      elif isinstance(operand, OpCall):
        if str(operand.target) is keys:
          operand.target = ret[str(operand.target)]
        if str(operand.target) is skeys:
          operand.target = spilling[str(operand.target)]
      elif isinstance(operand, OpComp):
        if str(operand.target1) in keys:
          operand.target1 = ret[str(operand.target1)]
        if str(operand.target2) in keys:
          operand.target2 = ret[str(operand.target2)]
  
        if str(operand.target1) in skeys:
          operand.target1 = spilling[str(operand.target1)]
        if str(operand.target2) in skeys:
          operand.target2 = spilling[str(operand.target2)]
      elif isinstance(operand, OpJump):
        pass
      elif isinstance(operand, OpJumpZeroFlag):
        pass
      elif isinstance(operand, MarkLabel):
        pass
      elif isinstance(operand, OpPush) or isinstance(operand, OpPop):
        pass
      elif isinstance(operand, OpRet):
        pass
      else:
        print(operand)
        raise Exception('error', 'Not Implemented')
  
      #print operand
      codes.append(operand)
  
    print("ending doRegisterAllocation")
    
    return codes
