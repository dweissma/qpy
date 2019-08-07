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
