# -*- coding: utf-8 -*-
#!/usr/bin/env python
from Operand import *
import pprint,sys

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
    def __init__(self, target, numargs):
        self.target = target
        self.numargs = numargs

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

class MarkLabel(Operand):
    def __init__(self, label):
        self.label = label

    def __str__(self):
        return "%s:" % (self.label)

def isRegister(storage):
    if isinstance(storage, IReg) or isinstance(storage, IUserReg):
        return True

    return False

def getRetReg(type = 'System.lang.Integer'):
    if type == 'System.lang.Double' or type == 'System.lang.Float':
        return IReg('xmm0')
    
    return IReg("rax")

def analyzeLiveVariable(lst):
    pp = pprint.PrettyPrinter(indent=2)

    Lafter = [set([]) for i in range(0, len(lst) + 1)]
    pos = len(lst)
    while pos >= 0:
        operand = lst[pos - 1]

        Lbefore, R, W = None, set([]), set([])
        if isinstance(operand, OpMove):
            if isRegister(operand.src):
                R = set([operand.src])
            W = set([operand.dst])
        elif isinstance(operand, OpAdd) \
            or isinstance(operand, OpSub) \
            or isinstance(operand, OpMul) \
            or isinstance(operand, OpDiv):
            if isRegister(operand.src):
                R = set([operand.src, operand.dst])
            W = set([operand.dst])
        elif isinstance(operand, OpComp):
            reglist = []

            if isRegister(operand.target1):
                reglist.append(operand.target1)

            if isRegister(operand.target2):
                reglist.append(operand.target2)

            R = set(reglist)
            W = set([])
        elif isinstance(operand, OpPush) \
            or isinstance(operand, OpJump) \
            or isinstance(operand, OpJumpZeroFlag):
            if isRegister(operand.target):
                R = set([operand.target])
            W = set([])
        elif isinstance(operand, OpPop):
            R = set([])
            W = set([operand.target])
        elif isinstance(operand, OpCall):
            readRegList = []
            if isRegister(operand.target):
                readRegList.append(operand.target)
            for i in range(0, operand.numargs):
                readRegList.append(IReg("arg%d" % (i)))
            R = set(readRegList)
            W = set([getRetReg()])

        if pos != 0:
            #print "Operand =", operand
            #print "L_after[pos]=",map(lambda x: str(x), Lafter[pos])
            #print "W=",map(lambda x: str(x), W)
            #print "R=",map(lambda x: str(x), R)
            Lafter[pos-1] = (Lafter[pos] - W) | R
            #print "L_after[pos-1]=",map(lambda x: str(x), Lafter[pos-1])
        else:
            print "pos == 0",
            print map(lambda x: str(x), (Lafter[pos] - W) | R)

        pos -= 1

    #pp.pprint(Lafter)

    return Lafter

def calculateInterferenceGraph(lst):
    pp = pprint.PrettyPrinter(indent=2)

    liveList = analyzeLiveVariable(lst)
    parameterList = [IReg('rcx'), IReg('rdx'), IReg('r8'), IReg('r9')]
    parameterListForFloating = [IReg('xmm0'), IReg('xmm1'), IReg('xmm2'), IReg('xmm3')]

    #print len(lst), len(liveList)

    graph, loc = {}, 0
    for operand in lst:
        loc += 1

        #print operand
        if isinstance(operand, OpMove):
            adjectList = []
            if liveList[loc] != None:
                #print map(lambda x: str(x), liveList[loc])
                for reg in liveList[loc]:
                    if operand.dst == reg or operand.src == reg:
                        continue

                    adjectList.append(reg.name)

            t = str(operand.dst)
            rn = set(map(lambda x: str(x), adjectList))
            if graph.has_key(t):
                graph[t] |= rn
            else:
                graph[t] = rn

            for e in adjectList:
                if graph.has_key(str(e)):
                    graph[str(e)] |= set([t])
                else:
                    graph[str(e)] = set([t])

            #pp.pprint(graph)
        elif isinstance(operand, OpAdd) \
            or isinstance(operand, OpSub) \
            or isinstance(operand, OpMul) \
            or isinstance(operand, OpDiv):
            adjectList = []
            if liveList[loc] != None:
                #print map(lambda x: str(x), liveList[loc])
                for reg in liveList[loc]:
                    if operand.dst == reg:
                        continue

                    adjectList.append(reg.name)

            t = str(operand.dst)
            rn = set(map(lambda x: str(x), adjectList))
            if graph.has_key(t):
                graph[t] |= rn
            else:
                graph[t] = rn

            for e in adjectList:
                if graph.has_key(str(e)):
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

            for reg in adjectList:
                t = str(reg)

                if liveList[loc] == None:
                    continue

                #print map(lambda x: str(x), liveList[loc])
                for areg in liveList[loc]:
                    if t == str(areg): 
                        continue

                    if graph.has_key(t):
                        graph[t] |= set([str(areg)])
                    else:
                        graph[t] = set([str(areg)])

                    if graph.has_key(str(areg)):
                        graph[str(areg)] |= set([t])
                    else:
                        graph[str(areg)] = set([t])

    #pp.pprint(graph)
    return graph

def SD(edges, colored):
    cnt = 0
    for c in colored:
        if c in edges:
            cnt += 1

    #print "SD value = %d" % (cnt)

    return cnt

def mapcolour(lst):
    G = calculateInterferenceGraph(lst)

    colors=['rax','rbx','rcx','rdx','rsi','rdi','r8','r9','r10','r11','r12','r13','r14','r15']
    inputList = G.keys()
    colorset=set(colors)
    final={}
    nodes=[0]*len(inputList)
    adj=[0]*len(inputList)
    flag=[0]*len(inputList)
    assigncol=[0]*len(inputList)
    colord=[0]*len(inputList)
    i=0
    j=0
    m=0
    while(i<len(inputList)):
        nodes[i]=i
        flag[i]=0
        adj[i]=map(lambda x: inputList.index(x), G[inputList[i]])
        i+=1

    for pos, reg in enumerate(inputList):
        #print reg, pos
        if reg in colors:
            flag[pos] = 1
            final[pos] = reg

    #print "before =", final
    while(j<len(inputList)):
        if flag[j] == 1:
            j += 1
            continue

        for a in adj[j]:
            if flag[a] == 1:
                colord.append(assigncol[a])
        colordset=set(colord)
        availset=colorset-colordset
        availlist=list(availset)
        assigncol[j]=availlist[0]
        flag[j]=1
        final[j]=assigncol[j]
        colord=[0]*len(inputList)
        j+=1

    retVal = {}
    for pos, reg in enumerate(inputList):
        retVal[reg] = final[pos]
    return retVal

def allocateRegister(lst):
    ret = mapcolour(lst)
    keys = ret.keys()
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
        elif isinstance(operand, OpCall):
            if str(operand.target) is keys:
                operand.target = ret[str(operand.target)]
        elif isinstance(operand, OpComp):
            if str(operand.target1) in keys:
                operand.target1 = ret[str(operand.target1)]
            if str(operand.target2) in keys:
                operand.target2 = ret[str(operand.target2)]
        elif isinstance(operand, OpJump):
            continue        
        elif isinstance(operand, OpJumpZeroFlag):
            continue
        elif isinstance(operand, MarkLabel):
            continue
        else:
            print operand
            raise Exception('error', 'Not Implemented')

        print operand