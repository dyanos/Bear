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

def analyzeLiveVariable(lst, args):
    pp = pprint.PrettyPrinter(indent=2)

    Lafter = [set([]) for i in range(0, len(lst) + 1)]
    pos = len(lst)
    while pos > 0:
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

        #print "Operand =", operand
        #print "Pos = %d" % (pos)
        #print "L_after[pos]=",map(lambda x: str(x), Lafter[pos])
        #print "W=",map(lambda x: str(x), W)
        #print "R=",map(lambda x: str(x), R)
        #print "Result=",map(lambda x: str(x), (Lafter[pos] - W) | R)
        if pos != 0:
            #print "Operand =", operand
            #print "L_after[pos]=",map(lambda x: str(x), Lafter[pos])
            #print "W=",map(lambda x: str(x), W)
            #print "R=",map(lambda x: str(x), R)
            Lafter[pos-1] = (Lafter[pos] - W) | R
            #print "L_after[pos-1]=",map(lambda x: str(x), Lafter[pos-1])
        #else:
            #print "pos == 0",
            #print map(lambda x: str(x), (Lafter[pos] - W) | R)

        pos -= 1

    #pp.pprint(Lafter)
    #for elm in Lafter:
    #    print "=",map(lambda x: str(x), elm)

    return Lafter

def calculateInterferenceGraph(lst, args):
    pp = pprint.PrettyPrinter(indent=2)

    liveList = analyzeLiveVariable(lst, args)
    parameterList = [IReg('rcx'), IReg('rdx'), IReg('r8'), IReg('r9')]
    parameterListForFloating = [IReg('xmm0'), IReg('xmm1'), IReg('xmm2'), IReg('xmm3')]

    #print len(lst), len(liveList)

    #print "calculateInterferenceGraph"

    if len(args) <= len(parameterList):
        args = parameterList[0:len(args)]
    else:
        args = parameterList

    graph, loc = {}, 1

    if len(args) >= 2:
        for argName in set(args):
            for extra in set(args) - set([argName]):
                if graph.has_key(argName):
                    graph[argName] |= set([extra])
                else:
                    graph[argName] = set([extra])

    for operand in lst:
        #print operand
        #print "loc=%d" % (loc)
        #print "Operand=",operand
        #print "liveList=",map(lambda x: str(x), liveList[loc])
        if isinstance(operand, OpMove):
            adjectList = []

            if isRegister(operand.src):
                adjectList.append(str(operand.src))

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

            if liveList[loc] == None:
                continue

            for reg in adjectList:
                t = str(reg)

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

        #print "display graph info : "
        #for key in graph:
        #    print "%s="%(key),map(lambda x: str(x), graph[key])

        loc += 1

    #pp.pprint(graph)
    return graph

def SD(adjected, colored):
    cnt = 0
    diffSet = set(adjected) - set(colored)

    #print "SD value = %d" % (cnt)

    return len(adjected) - len(diffSet)

def chooseColor(colors, colored):
    minVal, minNumColor = 999999999, None
    for color in colors:
        cnt = 0
        for selected in colored:
            if selected == color:
                cnt += 1
        if minVal > cnt:
            minVal = cnt
            minNumColor = color

    return minNumColor

def newColoringAlgorithm(graph):
    colors=['rax','rbx','rcx','rdx','rsi','rdi','r8','r9','r10','r11','r12','r13','r14','r15']
    #colors=['rax','rbx','rcx','rdx']

    colored = {}
    nodes = graph.keys()
    m = len(nodes)
    while len(colored) < m:
        maxVal = -1
        for node in nodes:
            index = None
            if not colored.has_key(node):
                d = SD(graph[node], colored.keys())
                print "1", d, maxVal
                if d > maxVal:
                    maxVal = d
                    index = node
                print "2", d, maxVal, index
                if d == maxVal:
                    if len(graph[node]) > len(graph[index]):
                        index = node
    
            if index != None:
                colored[index] = chooseColor(colors, colored.values()) # coloring
            else:
                raise Exception('err', 'err')

    return colored

def mapcolour2(lst):
    G = calculateInterferenceGraph(lst)

    print G
    #print newColoringAlgorithm(G)

    colors = set(['rax','rbx','rcx','rdx','rsi','rdi','r8','r9','r10','r11','r12','r13','r14','r15'])
    #colors = set(['rax','rbx','rcx','rdx'])
    colored = []

    assigned = {}

    nodes = G.keys()
    for node in nodes:
        if node in colors:
            colored.append(node)
            assigned[node] = node

    for node in nodes:
        # 이미 색깔이 칠해진 register라면, skip합니다.
        if node in colored:
            continue

        # colored?
        coloredNode = set([])
        for subNode in G[node]:
            if assigned.has_key(subNode):
                coloredNode |= set([assigned[subNode]])

        # 더 이상 할당 할 수 있는 register가 없을때?
        if len(coloredNode) == len(colors):
            raise Exception('error', 'no more registers')

        availColorList = list(set(colors) - set(coloredNode))
        print colors, coloredNode, availColorList
        assigned[node] = availColorList[-1]
        colored.append(node)

    return assigned

def calculateInterferenceGraph2(lst, outLive, args):
    pp = pprint.PrettyPrinter(indent=2)

    liveList = outLive
    parameterList = [IReg('rcx'), IReg('rdx'), IReg('r8'), IReg('r9')]
    parameterListForFloating = [IReg('xmm0'), IReg('xmm1'), IReg('xmm2'), IReg('xmm3')]

    #print len(lst), len(liveList)

    #print "calculateInterferenceGraph"

    if len(args) <= len(parameterList):
        args = parameterList[0:len(args)]
    else:
        args = parameterList

    graph, loc = {}, 0

    #if len(args) >= 2:
    #    for argName in set(args):
    #        for extra in set(args) - set([argName]):
    #            if graph.has_key(argName):
    #                graph[str(argName)] |= set([str(extra)])
    #            else:
    #                graph[str(argName)] = set([str(extra)])

    for operand in lst:
        #print operand
        #print "loc=%d" % (loc)
        #print "Operand=",operand
        #print "liveList=",map(lambda x: str(x), liveList[loc])
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
            if len(liveList[loc]) != 0:
                #print map(lambda x: str(x), liveList[loc])
                for reg in liveList[loc]:
                    if str(operand.dst) == reg:
                        continue

                    adjectList.append(reg)

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

            if len(liveList[loc]) == 0:
                continue

            for reg in adjectList:
                t = str(reg)

                #print map(lambda x: str(x), liveList[loc])
                for areg in liveList[loc]:
                    if t == areg: 
                        continue

                    if graph.has_key(t):
                        graph[t] |= set([areg])
                    else:
                        graph[t] = set([areg])

                    if graph.has_key(str(areg)):
                        graph[areg] |= set([t])
                    else:
                        graph[areg] = set([t])

        #print "display graph info : "
        #for key in graph:
        #    print "%s="%(key),map(lambda x: str(x), graph[key])

        loc += 1

    #pp.pprint(graph)
    return graph

def newRegisterAssignAlogrithm(lst, args):
    nlst = len(lst)

    succ = dict([(i, set([])) for i in range(0, nlst+1)]) # 후손에 남겨주는 경우
    pred = dict([(i, set([])) for i in range(0, nlst+1)]) # 선조로부터 오는 경우
    def1 = {}
    def2 = dict([(i, set([])) for i in range(0, nlst+1)])
    use1 = {}
    use2 = dict([(i, set([])) for i in range(0, nlst+1)])

    def registerDefVar(reg, pos):
        if not isRegister(reg):
            return 
            
        name = str(reg)
        if not def1.has_key(name):
            def1[name] = set([pos])
        else:
            def1[name] |= set([pos])
        
        def2[pos] |= set([name])

    def registerUseVar(reg, pos):
        if not isRegister(reg):
            return 

        name = str(reg)
        if not use1.has_key(name):
            use1[name] = set([pos])
        else:
            use1[name] |= set([pos])

        use2[pos] |= set([name])

    pred[0] = (-1)  # 이전 instruction은 없다.
    for pos, inst in enumerate(lst):
        real = pos
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
    #print "succ=",succ
    #print "pred=",pred
    #print "def1=",def1
    #print "def2=",def2
    #print "use1=",use1
    #print "use2=",use2

    def removeFirstOpcodeWith(rn, pos):
        for idx, node in enumerate(lst):
            if idx <= pos: 
                continue

            if isinstance(node, OpPop):
                if rn == str(node.target):
                    print "must remove opcode", node, "at", idx
                    return idx

        return -1

    def reorder(pos):
        prevPos = pos - 1
        while prevPos >= 0:
            if succ.has_key(prevPos):
                break

            prevPos -= 1

        nextPos = pos + 1
        while nextPos < len(lst):
            if pred.has_key(nextPos):
                break

            nextPos += 1

        if nextPos < len(lst):
            succ[prevPos] |= set([nextPos])
        succ[prevPos] -= set([pos])
        if prevPos >= 0:
            pred[nextPos] |= set([prevPos])
        pred[nextPos] -= set([pos])

        del succ[pos]
        del pred[pos]

    # 의미없이 register를 push하는 경우에 대한 삭제 코드 삽입 필요, 짝인 pop도 삭제
    reduntantOpcodeList = []
    for pos, node in enumerate(lst):
        if isinstance(node, OpPush):
            cross = filter(lambda x: x <= pos, def1[str(node.target)])
            if len(cross) == 0:
                print "must remove opcode", node, "at",pos

                # remove pop after this
                posOfPop = removeFirstOpcodeWith(str(node.target), pos)

                use1[str(node.target)] -= set([pos])
                del use2[pos]
                def1[str(node.target)] -= set([posOfPop])
                del def2[posOfPop]

                reorder(pos)
                reorder(posOfPop)

                reduntantOpcodeList.append(pos)
                reduntantOpcodeList.append(posOfPop)

    nullSet = set([])
    oldIn, newIn = [nullSet for i in range(0, nlst+1)], [nullSet for i in range(0, nlst+1)]
    oldOut, newOut = [nullSet for i in range(0, nlst+1)], [nullSet for i in range(0, nlst+1)]
    ind = 1
    while True:
        #print ind 
        for n, node in enumerate(reversed(lst)):
            real = nlst - n - 1
            oldIn[real] = newIn[real]
            oldOut[real] = newOut[real]
            newOut[real] = set([])
            if succ.has_key(real):
                for succNodeNum in succ[real]:
                    if succNodeNum < 0 or succNodeNum >= nlst:
                        continue

                    newOut[real] |= newIn[succNodeNum]
                newIn[real] = use2[real] | (newOut[real] - def2[real])
            #print real,"=",newIn[real],newOut[real]
            #print "succ[real]",succ[real]
            #print newOut[n], def2[n]
            #print newOut[n] - def2[n]

        exit = True
        for n in range(0, nlst):
            if oldIn[n] != newIn[n] or oldOut[n] != newOut[n]:
                exit = False
                break

        if exit:
            break

        ind += 1

    reduntantOpcodeList.sort()
    for pos in reversed(reduntantOpcodeList):
        del lst[pos]
    #print newIn
    #print newOut

    #print newIn[0]

    G = calculateInterferenceGraph2(lst, newOut, args)
    s = list(newIn[0])
    for i in range(0, len(newIn[0])):
        reg = s[i]
        for j in range(i, len(newIn[0])):
            if G.has_key(reg):
                G[reg] |= set([s[j]])
                G[s[j]] |= set([reg])
            else:
                G[reg] = set([s[j]])
                G[s[j]] = set([reg])

    return G

def reassign(lst, args):
    parameterList = ['rcx', 'rdx', 'r8', 'r9']
    parameterListForFloating = ['xmm0', 'xmm1', 'xmm2', 'xmm3']

    #print "args=",args

    newList = []
    for op in lst:
        if isinstance(op, OpMove): 
            if isRegister(op.src):
                name = str(op.src)
                if name in args:
                    loc = args.index(name)
                    if len(parameterList) > loc:
                        op.src = IReg(parameterList[loc])
                    else:
                        op.src = IMem(IReg('rbp'), None, loc)                        

            if isRegister(op.dst):
                name = str(op.dst)
                if name in args:
                    loc = args.index(name)
                    if len(parameterList) > loc:
                        op.dst = IReg(parameterList[loc])
                    else:
                        op.dst = IMem(IReg('rbp'), None, loc)
                elif name.startswith('arg'):
                    num = int(name[3:])
                    if num < len(parameterList):
                        op.dst = IReg(parameterList[num])

            newList.append(op)
        elif isinstance(op, OpAdd) \
            or isinstance(op, OpSub) \
            or isinstance(op, OpMul) \
            or isinstance(op, OpDiv):
            if isRegister(op.src):
                name = str(op.src)
                if name in args:
                    loc = args.index(name)
                    if len(parameterList) > loc:
                        op.src = IReg(parameterList[loc])
                    else:
                        tmpReg = genTempRegister()
                        newList.append(OpMove(IMem(IReg('rbp'), None, loc), tmpReg))
                        op.src = tmpReg

            if isRegister(op.dst):
                name = str(op.dst)
                if name in args:
                    loc = args.index(name)
                    if len(parameterList) > loc:
                        op.dst = IReg(parameterList[loc])
                    else:
                        tmpReg = genTempRegister()
                        newList.append(OpMove(IMem(IReg('rbp'), None, loc), tmpReg))
                        op.dst = tmpReg

            newList.append(op)
        elif isinstance(op, OpPush) \
            or isinstance(op, OpPop) \
            or isinstance(op, OpCall):
            if isRegister(op.target):
                name = str(op.target)
                if name in args:
                    loc = args.index(name)
                    if len(parameterList) > loc:
                        op.target = IReg(parameterList[loc])
                    else:
                        op.target = IMem(IReg('rbp'), None, loc)

            newList.append(op)
        else:
            newList.append(op)

    return newList

def mapcolour(lst, args = []):
    #lst = reassign(lst, args)
    #print "="*80
    #for op in lst: print op
    #print "="*80
    #G = calculateInterferenceGraph(lst, args)
    G = newRegisterAssignAlogrithm(lst, args)

    print "G=",G
    #print newColoringAlgorithm(G)

    colors=['rax','rbx','rcx','rdx','rsi','rdi','r8','r9','r10','r11','r12','r13','r14','r15'][::-1]
    #colors=['rax','rbx','rcx','rdx'] 
    symbols = G.keys()

    # make a matrix
    matrix = [[False for i in range(0, len(symbols))] for i in range(0, len(symbols))]
    for pos, regname in enumerate(symbols):
        neighbors = G[regname]
        for elem in neighbors:
            ind = symbols.index(elem)
            matrix[pos][ind] = True
            matrix[ind][pos] = True

    assignedColor = {}
    colored = [False] * len(symbols)
    for pos, symbol in enumerate(symbols):
        if symbol in colors:
            assignedColor[symbol] = symbol
            colored[pos] = True

    # using heuristic algorithm
    while len(filter(lambda x: x == True, colored)) != len(symbols):
        maxval, maxpos = -999999999999, None
        for rowpos, col in enumerate(matrix):
            # is already colored?
            if colored[rowpos] == True:
                continue

            # To calculate SD value
            number = 0
            for colpos, value in enumerate(col):
                if colored[colpos] == True:
                    continue

                if value == True:
                    number += 1

            if maxval < number:
                maxval = number
                maxpos = rowpos

        symbol = symbols[maxpos]

        # to find available registers
        precolored = []
        if symbol in colors:
            precolored.append(symbol)

        for colpos, value in enumerate(matrix[maxpos]):
            if value == False:
                continue

            sym = symbols[colpos]
            if assignedColor.has_key(sym):
                precolored.append(assignedColor[sym])

        availColorList = list(set(colors) - set(precolored))
        if not availColorList:
            raise Exception('Spilling', 'Spilling')
        else:
            assignedColor[symbol] = availColorList[0]
        #print symbol, assignedColor[symbol], availColorList[0]

        colored[maxpos] = True

    return assignedColor

def allocateRegister(lst, args):
    #print "called newRegisterAssignAlogrithm"
    #newRegisterAssignAlogrithm(lst, args)

    ret = mapcolour(lst, args)
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
            pass
        elif isinstance(operand, OpJumpZeroFlag):
            pass
        elif isinstance(operand, MarkLabel):
            pass
        elif isinstance(operand, OpPush) or isinstance(operand, OpPop):
            pass
        else:
            print operand
            raise Exception('error', 'Not Implemented')

        print operand