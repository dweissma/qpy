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
        elif type(prob) == float:
            self.qclass.q_prob(self.qubit, prob)
    
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

    def qand(self, other: qbool):
        """
        Applies a quantum and gate to 2 qbool objects
        Returning the resulting qbool
        """
        result = qbool(self.qclass)
        self.qclass.ccx(self.qubit, other.qubit, result.qubit)
        return result

    def qor(self, other: qbool):
        """
        Applies a quantum or gate to 2 qbool objects
        Returning the resulting qbool
        """
        result = qbool(self.qclass)
        self.qclass.ugate("x", self.qubit)
        self.qclass.ugate("x", other.qubit)
        self.qclass.ugate("x", result.qubit)
        self.qclass.ccx(self.qubit, other.qubit, result.qubit)
        self.qclass.ugate("x", self.qubit)
        self.qclass.ugate("x", other.qubit)
        return result
    
    def qnot(self):
        """
        Nots the qbool
        Also works as its own inverse
        """
        self.qclass.ugate("x", self.qubit)

    def qnand(self, other: qbool):
        """
        Applies a quantum nand gate with the
        current qbool and the other qbool
        """
        result = self.qand(other)
        result.qnot()
        return result

    def qxor(self, other: qbool):
        """
        Applies a quantum xor gate with
        the current qbool and the other qbool
        """
        result = qbool(self.qclass)
        self.qclass.ugate("x", self.qubit)
        self.qclass.ccx(self.qubit, other.qubit, result.qubit)
        self.qclass.ugate("x", self.qubit)
        self.qclass.ugate("x", other.qubit)
        self.qclass.ccx(self.qubit, other.qubit, result.qubit)
        self.qclass.ugate("x", other.qubit)
        return result

    def qiff(self, other: qbool):
        """
        Applies the biimplication <=>
        to 2 qbools
        """
        result = qbool(self.qclass)
        self.qclass.ccx(self.qubit, other.qubit, result.qubit)
        self.qclass.ugate("x", self.qubit)
        self.qclass.ugate("x", other.qubit)
        self.qclass.ccx(self.qubit, other.qubit, result.qubit)
        self.qclass.ugate("x", other.qubit)
        self.qclass.ugate("x", self.qubit)
        return result

    def qif(self, other: qbool):
        """
        Applies the implication =>
        to 2 qbools with self => other
        """
        other.qnot()
        result = self.qand(other)
        other.qnot()
        return result

    
    def iqand(self, first: qbool, other: qbool):
        """
        Inverts the qand gate
        """
        first.qclass.ccx(first.qubit, other.qubit, self.qubit)

    def iqor(self, first: qbool, other: qbool):
        """
        Inverts the qor gate
        """
        self.qclass.ugate("x", first.qubit)
        self.qclass.ugate("x", other.qubit)
        self.qclass.ccx(first.qubit, other.qubit, self.qubit)
        self.qclass.ugate("x", first.qubit)
        self.qclass.ugate("x", other.qubit)
        self.qclass.ugate("x", self.qubit)
        
    def iqnand(self, first: qbool, other: qbool):
        """
        Inverts the qnand gate
        """
        self.qnot()
        self.iqand(first, other)

    def iqxor(self, first: qbool, other: qbool):
        """
        Inverts the qxor gate
        """
        self.qclass.ugate("x", first.qubit)
        self.qclass.ccx(first.qubit, other.qubit, self.qubit)
        self.qclass.ugate("x", first.qubit)
        self.qclass.ugate("x", other.qubit)
        self.qclass.ccx(first.qubit, other.qubit, self.qubit)
        self.qclass.ugate("x", other.qubit)

    def iqiff(self, first: qbool, other: qbool):
        """
        Inverts the qiff gate
        """
        self.qclass.ccx(first.qubit, other.qubit, self.qubit)
        self.qclass.ugate("x", first.qubit)
        self.qclass.ugate("x", other.qubit)
        self.qclass.ccx(first.qubit, other.qubit, self.qubit)
        self.qclass.ugate("x", other.qubit)
        self.qclass.ugate("x", first.qubit)

    def iqif(self, first: qbool, other: qbool):
        """
        Inverts the qif gate
        """
        other.qnot()
        self.iqand(first, other)
        other.qnot()
        
    def free(self):
        """
        Frees the qubit storing the qbool back
        to the qclass 
        qbools should not be referenced afterwards
        Any hanging references will likely cause an error
        """
        self.qclass.return_chunk([self.qubit])
        self.qubit = None