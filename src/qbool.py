class qbool(object):
    """
    Quantum boolean class
    """
    def __init__(self, qclass, initial = None, prob = None):
        self.qclass = qclass
        self.qubit = self.qclass.chunk(1)[0]
        if type(initial) == bool:
            if initial:
                self.qclass.ugate('x', self.qubit)
                self.pureVal = True
            else:
                self.pureVal = False
            self.pure = True
        elif type(prob) == float:
            self.qclass.q_prob(self.qubit, prob)
            self.pure = False
            self.pureVal = None
        else:
            self.pure = True
            self.pureVal = False
        self.classBit = None
    
    def entangle(self):
        """
        Returns a new qbool object whose current probability of being
        true is the same as the current probability
        """
        b = qbool(self.qclass) #Make a fresh qubit
        return _entangle_fresh(b)

    def _entangle_fresh(self, b: qbool):
        """
        Entangles a blank qbool to the current qubit
        """
        self.qclass.cx(self.qubit, b.qubit)
        return b

    def measure(self):
        """
        Allots a classical bit and measures the qbool
        storing the result in said classical bit
        """
        self.classBit = self.qclass.chunk_class(1)[0]
        self.qclass.write("measure q[%d] " % self.qubit + "-> c[%d]; \n" % self.classBit)
        self.qclass.collapsed = True

    def extract_result(self, result):
        """
        Extracts the truth value for the qbool
        from the qclass result object
        """
        if classBit is None:
            raise RuntimeError("qbool was never measured so it can not be extracted")
        if result[self.classBit] == '1':
            return True
        else:
            return False

    def extract_counts(self, counts: dict):
        """
        Extracts the counts for each truth balue for the qbool
        """
        toReturn = {}
        for string, count in counts.items():
            result = self.extract_result(string)
            try:
                toReturn[result] += count
            except KeyError:
                toReturn[result] = count
        return toReturn