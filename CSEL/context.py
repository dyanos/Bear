class Context:
    def __init__(self):
        self.context = []

    def enterFunc(self):
        raise NotImplemented

    def endFunc(self):
        raise NotImplemented

    def emitMove(self, t, s):
        cmd = "mov %s %s" % (t, s)
        self.context.append(cmd)

    def emitCall(self, n, **kargs):
        pass